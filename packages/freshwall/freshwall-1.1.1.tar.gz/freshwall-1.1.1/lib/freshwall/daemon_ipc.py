# Copyright 2009 Chad Daelhousen.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
#


_IPC_UNAVAILABLE = "IPC is not available in the current environment."
_error_msg = ""

try:
    from freshwall import dbus_service
    _dbus_running = None
except ImportError, e:
    _dbus_running = False
    _error_msg = str(e)


def init ():
    """Initialize IPC.

    Second and subsequent calls merely return the result of the first call,
    with no further side effects."""

    global _dbus_running
    global _error_msg

    if _dbus_running is not None:
        return _dbus_running

    try:
        _dbus_running = dbus_service.init_mainloop(True)
    except Exception, e:
        _dbus_running = False
        _error_msg = str(e)

    return _dbus_running

def get_error ():
    """Return the error message of the last attempt to initialize IPC."""

    return _error_msg

def get_backend ():
    return "DBus"

def create_client (on_found=None, on_lost=None):
    """Create a client connection suitable for the available IPC type."""

    return _create(DaemonClientDBus, on_found=on_found, on_lost=on_lost)

def create_server (daemon):
    """Create a server listener suitable for the available IPC type."""

    return _create(DaemonControllerDBus, daemon)

def _create (klass, *init_args, **init_kwargs):
    global _error_msg

    if init():
        try:
            return klass(*init_args, **init_kwargs)
        except Exception, e:
            _error_msg = str(e)
            raise
    else:
        raise NotImplementedError(_IPC_UNAVAILABLE)


class Callback (object):
    """Sugar for callbacks used by the DaemonLocator class.

    Instances of this class are callables, but they append their stored args
    and kwargs to the args and kwargs of the actual call.
    
    Example::
        
        cb = Callback(foo, a, b, c=3)
        cb(x, c=6, d=4)
        # Results in a call to foo(x, a, b, c=6, d=4)"""

    _callback = None
    args = None
    kwargs = None

    def __init__ (self, callback, *args, **kwargs):
        """Store the callback into this instance.

        Any further arguments or keyword arguments passed will be stored as
        properties of this object, to be used when the instance is called (see
        __call__)."""

        self._callback = callback
        self.args = args
        self.kwargs = kwargs

    def __call__ (self, *args, **kwargs):
        """Call the callback contained in the instance.

        Args supplied to the call will be prepended to self.args. Keyword args
        will be merged into a shallow copy of self.kwargs. The resulting
        sequence and dict will be the final args and keyword args to the actual
        callable."""

        cb_args = args + self.args
        cb_kwargs = self.kwargs.copy()
        cb_kwargs.update(kwargs)

        return self._callback(*cb_args, **cb_kwargs)


class DaemonInterface (object):
    """Common code shared by the server and client."""

    def _configure (self, remote, period, spread):
        remote.SetTime(period, spread)
        remote.ResetTimer()


class DaemonClient (DaemonInterface):
    """Code shared by all clients, regardless of IPC mechanism."""

    def configure_daemon (self, period, spread):
        """Reconfigure the running daemon.

        Available when using DBus only."""

        raise NotImplementedError("Daemon cannot be configured using "
                                  "current IPC mechanism.")

    def exit_all (self):
        """Kill the running daemon(s).

        There should never be more than one, but the DBus backend can kill more
        than one if it does happen."""

        raise NotImplementedError("DaemonClient.exit_all "
                                  "must be implemented in subclass.")


class DaemonClientDBus (DaemonClient):
    """Client IPC interface."""

    kill_count = 0

    def __init__ (self, on_found=None, on_lost=None):
        """Locate the daemon.

        on_found will be called when a daemon is discovered; on_lost will be
        called when it exits."""

        self._locator = dbus_service.DaemonLocator()
        self._locator.init_client(on_found, on_lost)

    def configure_daemon (self, period, spread):
        """Reconfigure the currently available (running) daemon."""

        if self._locator.has_daemon():
            remote = self._locator.get_proxy_for_daemon()
            self._configure(remote, period, spread)
            remote.ChangeWallpaper()
            return True
        else:
            return False

    def exit_all (self):
        """Exit all daemons that respond to LocateDaemon().
        
        This MUST be called before entering the mainloop, or responses between
        starting the loop and calling exit_all() may be lost."""

        self._locator.set_callback('on_found', self._exit_daemon)

    def _exit_daemon (self, locator, target):
        """Exit daemon callback."""

        remote = locator.get_proxy_for_daemon(target)
        remote.Exit()
        self.kill_count += 1


class DaemonController (DaemonInterface):
    """Code shared by all servers, regardless of IPC mechanism."""

    pass


class DaemonControllerDBus (DaemonController):
    """Server IPC interface."""

    def __init__ (self, daemon):
        self._controller = dbus_service.DaemonController(daemon)

        self._locator = dbus_service.DaemonLocator()
        self._locator.init_daemon(self._send_settings)

    def _send_settings (self, locator, daemon_address):
        daemon = self._controller.daemon

        remote = locator.get_proxy_for_daemon(daemon_address)
        self._configure(remote, daemon.period, daemon.spread)
        daemon.stop()

