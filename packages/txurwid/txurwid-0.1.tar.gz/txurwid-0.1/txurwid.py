# encoding: utf-8
"""
Twisted integration for Urwid.

This module allows you to serve Urwid applications remotely over ssh.

The idea is that the server listens as an SSH server, and each connection is
routed by Twisted to urwid, and the urwid UI is routed back to the console.
The concept was a bit of a head-bender for me, but really we are just sending
escape codes and the what-not back to the console over the shell that ssh has
created. This is the same service as provided by the UI components in
twisted.conch.insults.window, except urwid has more features, and seems more
mature.

This module is not highly configurable, and the API is not great, so
don't worry about just using it as an example and copy-pasting.

TODO:

- better gpm tracking: there is no place for os.Popen in a Twisted app I
  think.

Copyright: 2010, Ali Afshar <aafshar@gmail.com>
License:   MIT <http://www.opensource.org/licenses/mit-license.php>
"""

import os

import urwid

from twisted.application.internet import TCPServer
from twisted.cred.portal import Portal
from twisted.conch.interfaces import IConchUser
from twisted.conch.insults.insults import TerminalProtocol, ServerProtocol
from twisted.conch.manhole_ssh import (ConchFactory, TerminalRealm,
    TerminalUser, TerminalSession)


class TwistedSharedEventLoop(urwid.TwistedEventLoop):
    """An Urwid event loop which will run as part of Twisted without starting and
    stopping the reactor.
    """
    def run(self):
        # reactor is already running, so don't start it
        pass


class TwistedScreen(urwid.BaseScreen):
    """A Urwid screen which knows about the Twisted terminal protocol that is
    driving it.

    A Urwid screen is responsible for:

    1. Input
    2. Output

    Input is achieved in normal urwid by passing a lsit of available readable
    file descriptors to the event loop for polling/selecting etc. In the
    Twisted situation, this is not necessary because Twisted polls the input
    descriptors itself. Urwid allows this by being driven using the main loop
    instance's `process_input` method which is triggered on Twisted protocol's
    standard `dataReceived` method.
    """

    def __init__(self, terminalProtocol):
        # We will need these later
        self.terminalProtocol = terminalProtocol
        self.terminal = terminalProtocol.terminal
        # Don't need to wait for anything to start
        self.started = True

    # Urwid Screen API

    def get_cols_rows(self):
        """Get the size of the terminal as (cols, rows)
        """
        return self.terminalProtocol.width, self.terminalProtocol.height

    def draw_screen(self, (maxcol, maxrow), r ):
        """Render a canvas to the terminal.

        The canvas contains all the information required to render the Urwid
        UI. The content method returns a list of rows as (cs, attr, text)
        tuples. This very simple implementation iterates each row and simply
        writes it out.
        """
        self.terminal.eraseDisplay()
        for i, row in enumerate(r.content()):
            self.terminal.cursorPosition(0, i)
            for (cs, attr, text) in row:
                if cs or attr:
                    print cs, attr
                self.write(text)
        cursor = r.get_cursor()
        if cursor is not None:
            self.terminal.cursorPosition(*cursor)

    # XXX from base screen
    def set_mouse_tracking(self):
        """
        Enable mouse tracking.

        After calling this function get_input will include mouse
        click events along with keystrokes.
        """
        self.write(urwid.escape.MOUSE_TRACKING_ON)

        self._start_gpm_tracking()

    # twisted handles polling, so we don't need the loop to do it, we just
    # push what we get to the loop from dataReceived.
    def get_input_descriptors(self):
        return []

    # Do nothing here either. Not entirely sure when it gets called.
    def get_input(self, raw_keys=False):
        return

    # Twisted driven
    def dataReceived(self, data):
        """Receive data from Twisted and push it into the urwid main loop.

        We must here:

        1. filter the input data against urwid's input filter.
        2. Calculate escapes and other clever things using urwid's
        `escape.process_keyqueue`.
        3. Pass the calculated keys as a list to the Urwid main loop.
        4. Redraw the screen
        """
        keys = self.loop.input_filter(data, [])
        keys, remainder = urwid.escape.process_keyqueue(map(ord, keys), True)
        self.loop.process_input(keys)
        self.loop.draw_screen()

    # Convenience
    def write(self, data):
        self.terminal.write(data)

    # Private
    def _start_gpm_tracking(self):
        if not os.path.isfile("/usr/bin/mev"):
            return
        if not os.environ.get('TERM',"").lower().startswith("linux"):
            return
        if not Popen:
            return
        m = Popen(["/usr/bin/mev","-e","158"], stdin=PIPE, stdout=PIPE,
            close_fds=True)
        fcntl.fcntl(m.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)
        self.gpm_mev = m

    def _stop_gpm_tracking(self):
        os.kill(self.gpm_mev.pid, signal.SIGINT)
        os.waitpid(self.gpm_mev.pid, 0)
        self.gpm_mev = None


class UrwidTerminalProtocol(TerminalProtocol):
    """A terminal protocol that knows to proxy input and receive output from
    Urwid.

    This integrates with the TwistedScreen in a 1:1.
    """

    def __init__(self, urwid_toplevel):
        self.urwid_toplevel = urwid_toplevel
        self.width = 80
        self.height = 24
        self.loop = None

    def connectionMade(self):
        self.terminalSize(self.width, self.height)
        self._create_urwid_mainloop()

    def terminalSize(self, width, height):
        """Resize the terminal.
        """
        self.width = width
        self.height = height
        self.terminal.eraseDisplay()
        if self.loop is not None:
            self.loop.draw_screen()

    def dataReceived(self, data):
        """Received data from the connection.

        This overrides the default implementation which parses and passes to
        the keyReceived method. We don't do that here, and must not do that so
        that Urwid can get the right juice (which includes things like mouse
        tracking).

        Instead we just pass the data to the screen instance's dataReceived,
        which handles the proxying to Urwid.
        """
        self.screen.dataReceived(data)

    def _create_urwid_mainloop(self):
        self.screen = TwistedScreen(self)
        self.loop = urwid.MainLoop(self.urwid_toplevel, screen=self.screen,
                                   event_loop=TwistedSharedEventLoop(),
                                   unhandled_input=self._unhandled_input)
        self.screen.loop = self.loop
        # not exactly necessary, the twisted reactor is already running
        self.loop.run()

    def _unhandled_input(self, input):
        if input == 'ctrl c':
            self.terminal.loseConnection()


class UrwidServerProtocol(ServerProtocol):
    def dataReceived(self, data):
        self.terminalProtocol.dataReceived(data)


class UrwidUser(TerminalUser):
    """A terminal user that remembers its avatarId

    The default implementation doesn't
    """
    def __init__(self, original, avatarId):
        TerminalUser.__init__(self, original, avatarId)
        self.avatarId = avatarId


class UrwidTerminalSession(TerminalSession):
    """A terminal session that remembers the avatar and chained protocol for
    later use. And implements a missing method for changed Window size.

    Note: This implementation assumes that each SSH connection will only
    request a single shell, which is not an entirely safe assumption, but is
    by far the most common case.
    """

    def openShell(self, proto):
        """Open a shell.
        """
        chainedProtocol = self.chainedProtocolFactory()
        chainedProtocol.avatar = IConchUser(self.original)
        chainedProtocol.session = self
        self.chainedProtocol = chainedProtocol
        self.transportFactory(
            proto, chainedProtocol,
            chainedProtocol.avatar,
            self.width, self.height)

    def windowChanged(self, (h, w, x, y)):
        """Called when the window size has changed.
        """
        self.chainedProtocol.terminalProtocol.terminalSize(h, w)


class UrwidRealm(TerminalRealm):
    """Custom terminal realm class-configured to use our custom Terminal User
    Terminal Session.
    """
    sessionFactory = UrwidTerminalSession
    userFactory = UrwidUser


def create_realm(urwid_toplevel):
    """Convenience to create a realm that will serve a given urwid widget.
    """

    def _protocol_factory(urwid_toplevel=urwid_toplevel):
        return UrwidServerProtocol(UrwidTerminalProtocol, urwid_toplevel)

    rlm = UrwidRealm()
    rlm.chainedProtocolFactory = _protocol_factory
    return rlm


def create_server_factory(urwid_toplevel, checkers):
    """Convenience to create a server factory with a portal that uses a realm
    serving a given urwid widget against checkers provided.
    """
    rlm = create_realm(urwid_toplevel)
    ptl = Portal(rlm, checkers)
    return ConchFactory(ptl)


def create_service(urwid_toplevel, checkers, port, **kw):
    """Convenience to create a service for use in tac-ish situations.
    """
    f = create_server_factory(urwid_toplevel, checkers)
    return TCPServer(port, f, **kw)

