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

import gconf
from freshwall.gconf_adapter import box, unbox

class Preferences (object):
    """Application preferences container."""

    _ROOT = "/apps/freshwall/"
    _cnxn = None

    # This is set up so that adding a key to _defaults here will add load/save
    # support for it, as well as a corresponding type-checked property on the
    # Preferences instance. The type will be detected from the Python type of
    # the default.
    _defaults = dict(alternate_file="",
                     daemon_period=600,
                     daemon_spread=0,
                     skip_current=True,
                     skip_deleted=True,
                     skip_none=True,
                     use_alternate_file=False)

    def __init__ (self, client=None):
        if client is None:
            client = gconf.client_get_default()

        self._client = client
        self._notifies = dict()

        self.load()

    @property
    def client (self):
        return self._client

    @classmethod
    def _init_properties (cls):
        for key, value in cls._defaults.iteritems():
            cls._init_property(key, value)

    @classmethod
    def _init_property (cls, name, default, doc=""):
        slot = "_" + name

        def fget (obj):
            return getattr(obj, slot)
        def fset (obj, value):
            # PY3K: bytes
            if type(default) in (str, unicode):
                if type(value) not in (str, unicode):
                    raise ValueError("%s must be a string value (got %s)" %
                                     (name, type(value)))
            elif type(value) is not type(default):
                raise ValueError("%s must be a %s value (got %s)" %
                                 (name, type(default), type(value)))
            setattr(obj, slot, value)
        def fdel (obj):
            setattr(obj, slot, default)

        setattr(cls, name, property(fget, fset, fdel, doc))
        setattr(cls, slot, default)

    def default_of (self, name):
        return self._defaults[name]

    def init_notify (self, reload=None):
        # preload types: NONE, ONELEVEL, RECURSIVE
        self._client.add_dir(self._ROOT[:-1], gconf.CLIENT_PRELOAD_ONELEVEL)
        self.enable_notify(reload)

    def enable_notify (self, reload=True):
        if self._cnxn is not None:
            return

        self._cnxn = self._client.notify_add(self._ROOT[:-1],
                                             self._notify_handler)
        if reload != False:
            self.load()

    def disable_notify (self):
        if self._cnxn is None:
            return

        self._client.notify_remove(self._cnxn)
        self._cnxn = None

    def _notify_handler (self, client, cnxn_id, gc_entry, *trash):
        key, value = self.parse_entry(gc_entry)
        old_value = getattr(self, key)
        setattr(self, key, value)

        for callback, cb_info in self._notifies.items():
            user_args = cb_info[1]
            callback(key, value, old_value, *user_args)

    def add_notify (self, callback, *user_args):
        if callback in self._notifies:
            #FIXME: Raise something
            return False

        self._notifies[callback] = (id, user_args)
        return True

    def remove_notify (self, callback):
        if callback not in self._notifies:
            #FIXME: Raise something
            return False

        id = self._notifies[callback][0]
        del self._notifies[callback]
        return True

    def load (self):
        for key in self._defaults.keys():
            gc_value = self._client.get(self._ROOT + key)

            # Use the default if the key is missing or has a weird type
            value = None

            try:
                value = unbox(gc_value)
                if value is None:
                    value = self._defaults[key]

                setattr(self, key, value)
            except Exception, e:
                #print "%s using default: %s" % (key, e.message)
                setattr(self, key, self._defaults[key])

    def save (self):
        for key in self._defaults.keys():
            gc_value = box(getattr(self, key))
            self._client.set(self._ROOT + key, gc_value)

        self._client.suggest_sync()

    def save_key (self, key, new_value):
        setattr(self, key, new_value)

        gc_value = box(new_value)
        self._client.set(self._ROOT + key, gc_value)

    def sync (self):
        self._client.suggest_sync()

    def parse_entry (self, entry):
        abs_key = entry.get_key()
        rootlen = len(self._ROOT)
        if self._ROOT != abs_key[0:rootlen]:
            raise RuntimeError("Key %s is not under _ROOT" % key)

        key = abs_key[rootlen:]
        value = unbox(entry.get_value())

        return key, value

    def is_present (self):
        return self._client.dir_exists(self._ROOT[:-1])

    def nuke (self):
        del self._client

Preferences._init_properties()

