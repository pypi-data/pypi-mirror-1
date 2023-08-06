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

import pygtk
pygtk.require("2.0")
import gtk

from freshwall import core
from freshwall import daemon_ipc as ipc
import os.path


GUI_LAYOUT_VERSION = 2

_ipc_client = None
_prefs = None
_config_items = {}
_gui_data = {}


class ConfigWidget (object):
    is_container = False

    root = None

    pack_expand = True
    pack_fill = True
    pack_padding = 0

    def __init__ (self, root):
        self.root = root


class ConfigArea (ConfigWidget):
    is_container = True

    child = None
    child_add_func = None

    def __init__ (self, root, child, child_add_func=None):
        ConfigWidget.__init__(self, root)
        self.child = child
        self.child_add_func = child_add_func

    def add_items (self, item_list):
        if self.child_add_func is not None:
            add = self.child_add_func
        else:
            add = self.child.add

        for item in item_list:
            if item is not None:
                add(item)

        self.root.add(self.child)


class ConfigItem (ConfigWidget):
    key = None

    def __init__ (self, root, key, get_fn, set_fn):
        ConfigWidget.__init__(self, root)

        root.set_data('get_fn', get_fn)
        root.set_data('set_fn', set_fn)

        self.key = key
        _config_items[key] = self

    def sync_from_prefs (self, prefs=None):
        if prefs is None:
            prefs = _prefs

        self.set(getattr(prefs, self.key))

    def get (self):
        getter = self.root.get_data('get_fn')
        return getter()

    def set (self, value):
        setter = self.root.get_data('set_fn')
        return setter(value)

    def save (self):
        _prefs.save_key(self.key, self.get())

    def connect (self, signal, child, filter_cb=None):
        child.connect(signal, self._on_change, filter_cb)

    def connect_external (self, signal, child, callback, cb_data=None):
        child.connect(signal, self._on_change_external, (callback, cb_data))

    def _on_change (self, widget, filter_cb):
        if filter_cb is None or filter_cb(widget):
            _prefs.save_key(self.key, self.get())

    def _on_change_external (self, *args):
        callback, cb_data = args[-1]
        cb_args = args[:-1] + (self, cb_data)
        if callback(*cb_args):
            _prefs.save_key(self.key, self.get())


def boolean_pref (pref, label):
    root = gtk.CheckButton(label)
    item = ConfigItem(root, pref, root.get_active, root.set_active)
    item.connect("toggled", root)
    return item

def frame (label, items):
    frame = gtk.Frame(label)
    vbox = gtk.VBox()
    for item in items:
        vbox.add(item.root)

    frame.add(vbox)
    return frame


def widget_skip_current ():
    return boolean_pref("skip_current",
                        "Ignore cu_rrent wallpaper")

def widget_skip_deleted ():
    return boolean_pref("skip_deleted",
                        "Ignore _deleted entries")

def widget_skip_none ():
    return boolean_pref("skip_none",
                        "Ignore '_no wallpaper' setting")


def _on_alt_file_dialog_response (dialog, response_id, alt_file_item, data):
    if response_id == int(gtk.RESPONSE_OK):
        alt_file_item.save()
        return True
    return False

def group_alternate_file (file_chooser_config_hook=None, want_dialog=False):
    off = gtk.RadioButton(None, "Gnome background preferences")
    on = gtk.RadioButton(off, "XML file:")

    on_box = gtk.HBox()
    on_box.pack_start(on, False, True)

    dialog_buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                      gtk.STOCK_OPEN, gtk.RESPONSE_OK)
    dialog = gtk.FileChooserDialog("Select a File", buttons=dialog_buttons)
    chooser = gtk.FileChooserButton(dialog) # 2.6
    on_box.pack_start(chooser, True, True)

    def set_alternate_file (value):
        dialog.set_filename(os.path.expanduser(value))

    alt_file_item = ConfigItem(on_box, 'alternate_file',
                               dialog.get_filename, set_alternate_file)
    # chooser's file-set signal isn't available until GTK 2.10
    alt_file_item.connect_external('response', dialog,
                                   _on_alt_file_dialog_response)

    if file_chooser_config_hook is not None:
        if want_dialog == True:
            file_chooser_config_hook(chooser, alt_file_item, dialog)
        else:
            file_chooser_config_hook(chooser, alt_file_item)

    vbox = gtk.VBox()
    vbox.add(off)
    vbox.add(on_box)

    def get_use_alternate_file ():
        return on.get_active()
    def set_use_alternate_file (value):
        if value:
            on.set_active(True)
        else:
            off.set_active(True)

    use_alt_item = ConfigItem(vbox, 'use_alternate_file',
                              get_use_alternate_file, set_use_alternate_file)
    use_alt_item.connect('toggled', on)
    use_alt_item.alternate_file = alt_file_item

    return use_alt_item


def widget_daemon_period ():
    # Change every [ 30][minutes |v]
    hbox = gtk.HBox()

    change_label = gtk.Label("Change every")
    hbox.pack_start(change_label, False, True)

    units = (('seconds', 1), ('minutes', 60), ('hours', 3600), ('days', 86400))

    entry = gtk.Entry()
    entry.set_width_chars(3)
    hbox.pack_start(entry, False, False)

    menu = gtk.combo_box_new_text()
    for text, mult in units:
        menu.append_text(text)
    hbox.pack_start(menu, False, False)

    def get_time ():
        value = int(entry.get_text())
        unit_text = menu.get_active_text() # 2.6
        for text, mult in units:
            if unit_text == text:
                return mult * value
        return value

    def set_time (value):
        try:
            val = int(value)
        except:
            # silently reject invalid values
            return

        for text, mult in reversed(units):
            if val % mult == 0:
                entry.set_text(str(val/mult))
                # menu.set_active_text(text) would be nice here
                model = menu.get_model()
                i = 0
                for row in model:
                    if row[0] == text:
                        menu.set_active(i)
                        break
                    i += 1
                # unit found, quit processing
                break

    item = ConfigItem(hbox, 'daemon_period', get_time, set_time)
    item.connect('changed', entry, lambda e: e.get_text() != '')
    item.connect('changed', menu)
    return item

def widget_daemon_spread ():
    hbox = gtk.HBox()

    name_label = gtk.Label("Percent randomness:")
    hbox.pack_start(name_label, False, False)

    rand_adjust = gtk.Adjustment(0, 0, 100, 1, 10, 0)
    rand_scale = gtk.HScale(rand_adjust)
    rand_scale.set_digits(0)
    rand_scale.set_value_pos(gtk.POS_RIGHT)
    rand_scale.set_update_policy(gtk.UPDATE_DELAYED)
    hbox.pack_start(rand_scale, True, True)

    def get_value ():
        return int(rand_adjust.get_value())
    def set_value (value):
        rand_adjust.set_value(int(value))

    item = ConfigItem(hbox, 'daemon_spread', get_value, set_value)
    item.connect('value-changed', rand_adjust)
    return item

def widget_daemon_apply_button ():
    if _ipc_client is None:
        return None

    button = gtk.Button("Apply settings to running daemon")
    button.set_sensitive(False)
    id = button.connect("clicked", apply_daemon_settings)
    _gui_data['daemon-apply-button'] = button
    _gui_data['daemon-apply-handler'] = id

    return ConfigWidget(button)

def apply_daemon_settings (button):
    period = _config_items['daemon_period'].get()
    spread = _config_items['daemon_spread'].get()
    _ipc_client.configure_daemon(period, spread)


def std_frame (title, border_width=3):
    frame = gtk.Frame(title)

    vbox = gtk.VBox()
    vbox.set_border_width(border_width)
    def add_to_vbox (item):
        vbox.pack_start(item.root, item.pack_expand, item.pack_fill)

    return ConfigArea(frame, vbox, add_to_vbox)

def frame_selection ():
    return std_frame("Wallpaper Selection")

def frame_file ():
    return std_frame("Wallpaper Listing")

def frame_daemon ():
    return std_frame("Daemon Settings")

def widget_buttons_end ():
    hbbox = gtk.HButtonBox()

    btn = gtk.Button(label="C_hange Now")
    _gui_data['change-now-button'] = btn
    hbbox.add(btn)

    btn = gtk.Button(stock="gtk-close")
    _gui_data['close-button'] = btn
    hbbox.add(btn)

    item = ConfigWidget(hbbox)
    item.pack_expand = False
    item.pack_fill = False
    return item

def buttons_end_connect (main_win, prefs=None):
    if prefs is None:
        prefs = _prefs

    def on_change_now (btn):
        core.change_wallpaper(prefs)
    id = _gui_data['change-now-button'].connect("clicked", on_change_now)
    _gui_data['change-now-handler'] = id

    id = _gui_data['close-button'].connect_object("clicked",
                                                  _on_win_delete,
                                                  main_win)
    _gui_data['close-handler'] = id


def build_layout (layout_data):
    for chunk in layout_data:
        yield build_chunk(chunk)

def build_chunk (chunk):
    cfg_item = chunk[0]()
    if cfg_item.is_container:
        contents = [contained() for contained in chunk[1]]
        cfg_item.add_items(contents)
    return cfg_item


def _on_daemon_found (locator, sender):
    _gui_data['daemon-apply-button'].set_sensitive(True)

def _on_daemon_lost (locator):
    _gui_data['daemon-apply-button'].set_sensitive(False)

def start_ipc_client ():
    return ipc.create_client(_on_daemon_found, _on_daemon_lost)


def _on_pref_changed (key, value, old_value):
    try:
        item = _config_items[key]
        if item.get() != value:
            item.set(value)
    except KeyError:
        # possibly hidden config items
        pass


def _on_win_delete (win, *args):
    quit_gui(win)

def quit_gui (win=None):
    if win is not None:
        win.destroy()

    _prefs.save()
    gtk.main_quit()

def create_main_window (title, border_width=5, quit_on_delete=True,
                        default_size=(325, -1)):
    win = gtk.Window()
    win.set_title(title)
    win.set_border_width(border_width)
    win.set_default_size(*default_size)
    if quit_on_delete:
        _gui_data['main-handler'] = win.connect("delete-event", _on_win_delete)

    _gui_data['main-window'] = win
    return win

def layout_main_window (win, layout_data):
    vbox = gtk.VBox()
    for item in build_layout(layout_data):
        vbox.pack_start(item.root, item.pack_expand, item.pack_fill,
                        item.pack_padding)

    win.add(vbox)
    win.show_all()

def set_initial_values (prefs):
    for item in _config_items.values():
        item.set(getattr(prefs, item.key))


layout = [(frame_selection, [widget_skip_current,
                             widget_skip_deleted,
                             widget_skip_none]),
          (frame_file, [group_alternate_file]),
          (frame_daemon, [widget_daemon_period,
                          widget_daemon_spread,
                          widget_daemon_apply_button]),
          (widget_buttons_end,)]

def run_prefs_dialog (prefs):
    global _ipc_client
    global _prefs

    _prefs = prefs
    prefs.init_notify()
    prefs.add_notify(_on_pref_changed)

    try:
        _ipc_client = start_ipc_client()
    except NotImplementedError:
        pass

    win = create_main_window("FreshWall Configuration")
    layout_main_window(win, layout)
    set_initial_values(prefs)
    buttons_end_connect(win)

    gtk.main()

    prefs.save()
    return 0

