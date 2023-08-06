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

from __future__ import division

import pygtk
pygtk.require("2.0")
import gobject

from freshwall import core
from freshwall import daemon_ipc as ipc
import os
import random
import re
import sys


_time_units = dict(d=86400, h=3600, m=60, s=1)


def decimal_of_percent (p, default, min=0, max=100):
    def int_of_percent (p, default, min, max):
        if p is None:
            return default

        try:
            value = float(p)
        except ValueError:
            return default

        if value < min:
            return min
        if value > max:
            return max

        return value

    return int_of_percent(p, default, min, max) / 100

def parse_time (t, default, min=None, max=None):
    if t is None or t == "":
        return default

    match = re.match(r'\s*([.\d]+)([d|h|m|s])?', str(t), re.I)
    if match is None:
        return default

    try:
        raw_value = float(match.group(1))
    except ValueError:
        return default

    unit = match.group(2)
    if unit is None:
        unit = 's'

    mult = _time_units[unit]
    value = raw_value * mult

    if min is not None and value < min:
        return min
    if max is not None and value > max:
        return max

    return value


class Daemon (object):
    _bounds = None
    _mainloop = None
    _min_period = 10
    _next_id = None
    _period = None
    _prefs = None
    _spread = None

    def __init__ (self, prefs, period=None, spread=None, mainloop=None):
        self._mainloop = mainloop
        self._prefs = prefs
        self.set_time(period, spread)

        prefs.init_notify()

    # Public properties
    def get_period (self):
        return self._period

    def set_period (self, value):
        default = self._prefs.daemon_period
        self._period = parse_time(value, default)
        self._recalc_bounds()

    period = property(get_period, set_period)

    def get_spread (self):
        return self._spread

    def set_spread (self, value):
        default = self._prefs.daemon_spread
        self._spread = decimal_of_percent(value, default) * 100
        self._recalc_bounds()

    spread = property(get_spread, set_spread)

    # Internal property handling
    def _recalc_bounds(self):
        if self._period is None or self._spread is None:
            return

        period = self._period
        spread_sec = (self._spread / 100) * period

        lower = period - spread_sec
        upper = period + spread_sec
        if lower < self._min_period:
            lower = self._min_period
        if upper < lower:
            upper = lower

        self._bounds = lower, upper

    # Public methods
    def set_time (self, period, spread):
        # Mostly convenience, but puts potential in the API for optimizing this
        # case someday.
        self.period = period
        self.spread = spread

    def run (self, change_at_start=True):
        if self._mainloop is None:
            self._mainloop = gobject.MainLoop()

        self.schedule_next()
        if change_at_start:
            core.change_wallpaper(self._prefs)

        try:
            self._mainloop.run()
        except KeyboardInterrupt, e:
            print ""

        return 0

    def stop (self):
        self.remove_schedule()
        self._mainloop.quit()

    def force_update (self):
        core.change_wallpaper(self._prefs)
        self.reschedule()

    def schedule_next (self):
        if self._next_id is not None:
            raise Exception("Already scheduled")

        lower, upper = self._bounds
        seconds = random.uniform(lower, upper)
        millisec = int(seconds * 1000)
        self._next_id = gobject.timeout_add(millisec, self._do_change)

    def remove_schedule (self):
        if self._next_id is None:
            return

        gobject.source_remove(self._next_id)
        self._next_id = None

    def reschedule (self):
        self.remove_schedule()
        self.schedule_next()

    # Timer callback
    def _do_change (self, *args):
        core.change_wallpaper(self._prefs)

        if self._bounds[0] != self._bounds[1]:
            # variable time: remove current interval and schedule a new one
            self.reschedule()
            return False
        else:
            # fixed time: call this function again at the same interval
            return True


class DaemonKiller (object):
    client = None
    locator = None
    _mainloop = None
    _timeout = None

    def __init__ (self, timeout=None, mainloop=None):
        self._mainloop = mainloop
        if timeout is None:
            timeout = 3

        self._timeout = int(timeout * 1000)

    def connect (self):
        self.client = ipc.create_client()
        self.client.exit_all()

    def _on_time_expired (self, *args):
        self.stop()
        return False

    def run (self):
        if self._mainloop is None:
            self._mainloop = gobject.MainLoop()

        gobject.timeout_add(self._timeout, self._on_time_expired)

        self._mainloop.run()

        if self.client is None or self.client.kill_count == 0:
            return 1
        else:
            return 0

    def stop (self):
        self._mainloop.quit()


def _fork ():
    try:
        if os.fork() > 0:
            os._exit(0)
    except OSError, error:
        print 'detaching failed: %s' % error.strerror
        os._exit(1)

def _close_files ():
    if hasattr(os, 'devnull'):
        null = os.devnull
    else:
        null = '/dev/null'

    for stream in (sys.stdin, sys.stdout, sys.stderr):
        try:
            stream.close()
        except:
            pass

    try:
        sys.stdout = open(null, 'w')
    except:
        pass

    try:
        sys.stderr = open(null, 'w')
    except:
        pass

def daemonize ():
    _fork()
    os.chdir('/')
    os.setsid()
    _fork()
    _close_files()


def run (prefs, period, spread, detach=None, mainloop=None):
    daemon = Daemon(prefs, period, spread, mainloop=mainloop)

    try:
        listener = ipc.create_server(daemon)
    except Exception, e:
        print >>sys.stderr, "Warning: IPC failed: %s" % ipc.get_error()

    if detach == True:
        daemonize()

    return daemon.run()

def exit (mainloop=None):
    killer = DaemonKiller(mainloop=mainloop)
    try:
        killer.connect()
        return killer.run()
    except:
        print >>sys.stderr, "Error: IPC failed: %s" % ipc.get_error()
        return 2

