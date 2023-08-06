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
#
# This module contains the DBus interface to freshwall.
#

import dbus
import dbus.service

# This is the version where dbus.service.Object gains the ability to receive a
# Bus directly, instead of requiring a BusName.
MIN_BINDINGS_VERSION = (0, 80, 0)
if dbus.version < MIN_BINDINGS_VERSION:
    raise ImportError("need python-dbus version >=%s; found %s" %
                      (MIN_BINDINGS_VERSION, dbus.version))


DAEMON_INTERFACE = 'org.sapphirepaw.FreshWall.Daemon'
DAEMON_PATH = '/org/sapphirepaw/FreshWall/Daemon'

LOCATOR_INTERFACE = 'org.sapphirepaw.FreshWall.Locator'
LOCATOR_PATH = '/org/sapphirepaw/FreshWall/Locator'


def init_mainloop (raise_on_fail=False):
    """Connect the dbus-python bindings to the glib mainloop.

    Returns True on success, or False on failure. The dbus_service is basically
    unusable if this function fails, since signals and async calls are a
    required part of the DaemonLocator.
    
    If raise_on_fail is True, then ImportError will not be silenced."""

    try:
        from dbus.mainloop.glib import DBusGMainLoop
        DBusGMainLoop(set_as_default=True)
        return True
    except ImportError:
        if raise_on_fail:
            raise
        return False


class _LocatorData (object):
    """Private data of the DaemonLocator.

    This is a separate class to prevent a profusion of double-underscore
    prefixed attributes on DaemonLocator, or name clashes."""

    bus = None
    daemon_address = None

    on_found = None
    on_lost = None
    on_remote_error = None
    on_remote_ok = None

    def __init__ (self, bus):
        self.bus = bus

    def fire_event (self, name, *event_args):
        """Call a callback for the event, if it is present.
        
        If the name is invalid or unknown, ValueError is raised. If the
        callback is not set, None is returned."""

        if name[0:3] != "on_":
            raise ValueError("Invalid event name.")

        try:
            callback = getattr(self, name)
        except AttributeError, e:
            raise ValueError("Unknown event name.")

        if callback is None:
            return 

        return callback(*event_args)


class DaemonLocator (dbus.service.Object):
    """DBus object supporting the ad-hoc daemon location protocol.

    This protocol allows for locating the daemon without forcing it to register
    a well-known name (which would require file installation, and defeat the
    purpose of running as a self-extracting script). The LocateDaemon and
    DaemonStartup signals notify other clients of activity; when a running
    daemon receives one of these signals, it calls the sender's DaemonLocation
    method to reveal the daemon's location to that sender.
    
    There may be some race conditions left in here but it's good enough for
    now.
    
    This object is exported by all freshwall processes that are interested in
    their peers, such as the daemon mode and the preferences window."""

    def __init__ (self, conn=None, object_path=None, bus_name=None):
        """Initialize the locator on a DBus connection.

        conn, object_path, and bus_name are purposely chosen to have the same
        basic semantics as dbus.service.Object; in addition, conn defaults to
        the session bus, and object_path defaults to LOCATOR_PATH."""

        if bus_name is not None:
            the_bus = bus_name.get_bus()
        elif conn is None:
            the_bus = conn = dbus.SessionBus()

        if object_path is None:
            object_path = LOCATOR_PATH

        dbus.service.Object.__init__(self, conn, object_path, bus_name)
        self.__data = _LocatorData(the_bus)

    def init_client (self, on_daemon_found=None, on_daemon_lost=None):
        """Initialize a client of the daemon.

        on_daemon_found gives a callback to be called when a daemon is
        discovered (by responding to our LocateDaemon() signal by calling our
        DaemonLocation() method, or by issuing DaemonStartup()). The arguments
        given to this callback are this DaemonLocator instance and the sender's
        DBus address.

        on_daemon_lost gives a callback to be called when the daemon is shut
        down. The only argument given is this DaemonLocator instance.
        
        For best results, these callbacks should not block."""

        self.set_callback('on_found', on_daemon_found)
        self.set_callback('on_lost', on_daemon_lost)

        self.LocateDaemon()
        self._listen_for('DaemonStartup', self._client_on_startup)

    def init_daemon (self, on_running):
        """Initialize the daemon.

        on_running gives a callback to be called if another daemon is already
        running (responding to our DaemonStartup() signal by calling our
        DaemonLocation() method). The arguments given are the DaemonLocator and
        the DBus sender address.
        
        For best results, this callback should not block."""

        self.set_callback('on_found', on_running)
        self.DaemonStartup()

        for signal in ('DaemonStartup', 'LocateDaemon'):
            self._listen_for(signal, self._on_locate_request)

    def _listen_for (self, signal, callback):
        bus = self.__data.bus
        bus.add_signal_receiver(callback, signal, LOCATOR_INTERFACE,
                                sender_keyword='sender')

    def set_callback (self, name, callback):
        """Generic callback setting interface.

        name is the name of a callback, 'on_foo', and callback is a callable
        to be called when foo occurs.
        
        You most likely want to pass callbacks to init_client, init_daemon, or
        set_dbus_async_handlers instead of using this method directly."""

        if name[0:3] == 'on_':
            setattr(self.__data, name, callback)
        else:
            raise ValueError("Invalid event name.")

    def set_dbus_async_handlers (self, ok_handler=None, error_handler=None):
        """Sets callbacks to be notified in case of success/error.

        ok_handler takes arguments: the DaemonLocator instance, the remote
        method/signal name, and the remote proxy object.

        error_handler takes the same initial arguments, plus the
        dbus_exception.

        Note that setting these handlers will notify you of ALL internal DBus
        call results, so it is up to you to pay attention to the method name if
        you only want to handle a specific method."""

        self.set_callback('on_remote_ok', ok_handler)
        self.set_callback('on_remote_error', error_handler)

    def get_proxy_for_daemon (self, target=None):
        """Returns a proxy to the daemon object and interface of the target.

        If target is None, the sender most recently heard from will be used
        instead."""

        return self.get_proxy_for(target, DAEMON_PATH, DAEMON_INTERFACE)

    def get_proxy_for_locator (self, target=None):
        """Returns a proxy to the locator object and interface of the target.

        If target is None, the sender most recently heard from will be used
        instead."""

        return self.get_proxy_for(target, LOCATOR_PATH, LOCATOR_INTERFACE)

    def get_proxy_for (self, target, object_path, interface):
        """Returns a proxy to the specified object/interface of the target.

        If target is None, the sender most recently heard from will be used
        instead. If none is known, then ValueError is raised."""

        if target is None:
            target = self.__data.daemon_address
            if target is None:
                raise ValueError("No target available to create proxy.")

        obj_proxy = self.__data.bus.get_object(target, object_path)
        if_proxy = dbus.Interface(obj_proxy, dbus_interface=interface)
        return if_proxy

    def has_daemon (self):
        return self.__data.daemon_address is not None

    def _on_lost (self, name, old_owner, new_owner):
        """Internal handling of "daemon lost" condition."""

        if new_owner == "":
            self.__data.daemon_address = None
            self.__data.fire_event('on_lost', self)
        else:
            self.__data.daemon_address = new_owner

    def _on_locate_request (self, sender=None):
        """Respond to LocateDaemon and DaemonStartup as a daemon.
        
        This can fire callbacks set by set_dbus_async_handlers(); the method
        name will be 'DaemonLocation'."""

        remote = self.get_proxy_for_locator(sender)
        fire = self.__data.fire_event

        # async dbus call: remote may try to call us before returning from
        # their DaemonLocation handler, and deadlock.
        def on_ok ():
            fire('on_remote_ok', self, 'DaemonLocation', remote)
        def on_error (dbus_exc):
            fire('on_remote_error', self, 'DaemonLocation', remote, dbus_exc)

        remote.DaemonLocation(reply_handler=on_ok, error_handler=on_error)

    def _client_on_startup (self, sender=None):
        """Respond to DaemonStartup as a client."""

        if self.has_daemon():
            return

        try:
            self.__data.daemon_address = sender
            self.__data.fire_event('on_found', self, sender)
        finally:
            self._connect_on_lost(sender)

    def _connect_on_lost (self, sender):
        # signal
        #   sender=org.freedesktop.DBus -> dest=(null destination)
        #   path=/org/freedesktop/DBus;
        #   interface=org.freedesktop.DBus;
        #   member=NameOwnerChanged
        # args
        #   name=":1.64", old_owner=":1.64", new_owner=""
        bus = self.__data.bus
        bus.add_signal_receiver(self._on_lost, 'NameOwnerChanged',
                                'org.freedesktop.DBus', # interface
                                # bus_name, path not needed
                                arg0=sender)


    #DaemonLocation
    @dbus.service.method(dbus_interface=LOCATOR_INTERFACE,
                         in_signature='', out_signature='',
                         sender_keyword='sender')
    def DaemonLocation (self, sender=None):
        """Respond to remote daemons informing us of their existence."""

        self.__data.daemon_address = sender

        try:
            self.__data.fire_event('on_found', self, sender)
        finally:
            self._connect_on_lost(sender)


    #LocateDaemon
    @dbus.service.signal(dbus_interface=LOCATOR_INTERFACE,
                         signature='')
    def LocateDaemon (self):
        """Signal for discovering the currently running daemon."""
        pass


    #DaemonStartup
    @dbus.service.signal(dbus_interface=LOCATOR_INTERFACE,
                         signature='')
    def DaemonStartup (self):
        """Notify clients and other daemons of a new daemon instance."""
        pass


class DaemonController (dbus.service.Object):
    """DBus object allowing for remote control of the daemon process.

    This object is only exported by freshwall daemons."""

    daemon = None

    def __init__ (self, daemon, conn=None, object_path=None, bus_name=None):
        """Initialize the daemon on a DBus connection.

        conn, object_path, and bus_name are purposely chosen to have the same
        basic semantics as dbus.service.Object; in addition, conn defaults to
        the session bus, and object_path defaults to DAEMON_PATH."""

        self.daemon = daemon

        if bus_name is None and conn is None:
            conn = dbus.SessionBus()

        if object_path is None:
            object_path = DAEMON_PATH

        dbus.service.Object.__init__(self, conn, object_path, bus_name)


    #Exit
    @dbus.service.method(dbus_interface=DAEMON_INTERFACE,
                         in_signature='', out_signature='')
    def Exit (self):
        """Quit the daemon."""

        self.daemon.stop()


    #ChangeWallpaper
    @dbus.service.method(dbus_interface=DAEMON_INTERFACE,
                         in_signature='', out_signature='')
    def ChangeWallpaper (self):
        """Change the wallpaper immediately.

        This does not affect the time at which the wallpaper will be changed
        again."""

        self.daemon.force_update()


    #ResetTimer
    @dbus.service.method(dbus_interface=DAEMON_INTERFACE,
                         in_signature='', out_signature='')
    def ResetTimer (self):
        """Restart the timer for changing the wallpaper.

        This should most likely be called after the Set methods, or after
        ChangeWallpaper."""

        self.daemon.reschedule()


    #GetPeriod
    @dbus.service.method(dbus_interface=DAEMON_INTERFACE,
                         in_signature='', out_signature='d')
    def GetPeriod (self):
        """Return the basic interval between wallpaper changes, in seconds."""

        return self.daemon.period


    #SetPeriod
    @dbus.service.method(dbus_interface=DAEMON_INTERFACE,
                         in_signature='d', out_signature='')
    def SetPeriod (self, seconds):
        """Set the basic interval between wallpaper changes, in seconds."""

        self.daemon.period = seconds


    #GetSpread
    @dbus.service.method(dbus_interface=DAEMON_INTERFACE,
                         in_signature='', out_signature='d')
    def GetSpread (self):
        """Return the randomness of the interval, in decimal percent."""

        return self.daemon.spread / 100


    #SetSpread
    @dbus.service.method(dbus_interface=DAEMON_INTERFACE,
                         in_signature='d', out_signature='')
    def SetSpread (self, percent):
        """Set the randomness of the interval, in decimal percent."""

        self.daemon.spread = percent * 100


    #SetTime
    @dbus.service.method(dbus_interface=DAEMON_INTERFACE,
                         in_signature='dd', out_signature='')
    def SetTime (self, period, spread):
        """Set the basic interval and randomness in one call.

        period gives the length of the basic interval, in seconds. spread gives
        the amount of randomness, in decimal percent."""

        self.daemon.set_time(period, spread * 100)

