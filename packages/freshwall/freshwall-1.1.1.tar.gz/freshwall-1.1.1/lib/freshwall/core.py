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

from freshwall.background import BackgroundList
from freshwall.gnome_background import GnomeBackground
from freshwall.preferences import Preferences
import freshwall.version as version
import optparse
import os.path
import random
import sys

# Gnome wallpaper source file
_DEFAULT_XML = "~/.gnome2/backgrounds.xml"
# Current background
_current_bg_filename = None


def accept_not_current (bg):
    return bg.settings['filename'] != _current_bg_filename

def accept_not_deleted (bg):
    return not bg.deleted

def accept_not_none (bg):
    return bg.settings['filename'] != '(none)'

def apply_filters (wp_list, prefs):
    filters = []
    if prefs.skip_current:
        filters.append(accept_not_current)
    if prefs.skip_deleted:
        filters.append(accept_not_deleted)
    if prefs.skip_none:
        filters.append(accept_not_none)
    wp_list.filter(filters)


def get_xml_file (prefs):
    alt = prefs.alternate_file

    if alt and prefs.use_alternate_file:
        src = alt
    else:
        src = _DEFAULT_XML

    src_expand = os.path.expanduser(src)
    return src_expand


def load_prefs ():
    """Initialize a GConfClient and load/initialize application settings."""

    prefs = Preferences()

    if not prefs.is_present():
        prefs.save()

    return prefs


def get_parser (program=None, description=None, version_str=None):
    if program is None:
        program = sys.argv[0]
    program = os.path.basename(program)

    if version_str is None:
        # generate version_str across two statements so %prog doesn't confuse
        # string-format operator
        version_tag = str(version.version)
        if len(version.revision) > 0:
            version_tag += " [revision %s]" % version.revision
        version_str = "%prog " + version_tag

    parser = optparse.OptionParser(prog=program, description=description,
                                   version=version_str)

    return parser


def change_wallpaper (prefs, do_filters=True):
    global _current_bg_filename
    desktop_bg = GnomeBackground(client=prefs.client)

    # Load current background for skip_current filter
    current_bg_data = desktop_bg.get()
    _current_bg_filename = current_bg_data.settings['filename']
    del current_bg_data

    # Filter available backgrounds
    wp_list = BackgroundList(get_xml_file(prefs))
    if do_filters:
        apply_filters(wp_list, prefs)

    # choose random wallpaper
    chosen_bg = random.choice(wp_list.items)

    # write wp to gconf
    desktop_bg.set(chosen_bg)

    # notify caller of choice
    return chosen_bg

