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

from freshwall.background import BackgroundData
from freshwall.gconf_adapter import box, unbox

class GnomeBackground (object):
    _root = "/desktop/gnome/background/"
    _gconf_key_of_xml = dict(filename='picture_filename',
                             options='picture_options',
                             shade_type='color_shading_type',
                             pcolor='primary_color',
                             scolor='secondary_color')

    def __init__ (self, *args, **kwargs):
        self._client = kwargs['client']
        del kwargs['client']

    def get (self):
        bg_data = BackgroundData()
        bg_data.deleted = False

        for attr_name, gconf_key in self._gconf_key_of_xml.items():
            abs_key = self._root + gconf_key
            value = unbox(self._client.get(abs_key))
            bg_data.settings[attr_name] = value

        return bg_data

    def set (self, bg_data):
        key_table = self._gconf_key_of_xml
        root = self._root
        client = self._client

        for xml_key, value in bg_data.settings.items():
            try:
                gconf_key = key_table[xml_key]
                client.set(root + gconf_key, box(value))
            except KeyError:
                pass

        client.suggest_sync()

