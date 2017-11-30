#!/usr/bin/python2
"""
Change your nautilus directories icons easily

Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Website : https://github.com/bil-elmoussaoui/nautilus-folder-icons
Licence : GPL-3.0
nautilus-folder-icons is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
nautilus-folder-icons is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with nautilus-folder-icons. If not, see <http://www.gnu.org/licenses/>.
"""
from gettext import gettext as _
from os import path
from threading import Thread

from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import GdkPixbuf, Gio, GLib, GObject, Gtk, Pango

from icons_utils import (SUPPORTED_EXTS, Image, filter_folders, get_default_icon,
                         get_ext, is_path, uriparse)



class FolderBox(Gtk.Box):

    def __init__(self, icon_name):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.name = icon_name
        self._build_widget()
        self.show()

    def _build_widget(self):
        theme = Gtk.IconTheme.get_default()
        pixbuf = theme.load_icon(self.name, 48, 0)
        # Force the icon to be 48x48
        pixbuf = pixbuf.scale_simple(48, 48, GdkPixbuf.InterpType.BILINEAR)

        image = Gtk.Image.new_from_pixbuf(pixbuf)
        image.show()
        self.pack_start(image, False, False, 6)

        label = Gtk.Label()
        label.set_text(self.name)
        label.show()
        self.pack_start(label, False, False, 6)



class FolderIconChooser(Gtk.Window, GObject.GObject, Thread):
    __gsignals__ = {
        'icon_selected': (GObject.SIGNAL_RUN_LAST, None, (str, )),
        'loaded': (GObject.SIGNAL_RUN_FIRST, None, ()),
    }

    def __init__(self, folders):
        GObject.GObject.__init__(self)
        Thread.__init__(self)
        Gtk.Window.__init__(self)
        # Here i assume that all folders got the same icon...
        self._folders = folders
        self.model = []

        # Threading stuff
        self.setDaemon(True)
        self.run()

        # Window configurations
        self.set_default_size(650, 400)
        self.set_size_request(650, 400)
        self.set_resizable(True)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)

        # Widgets & Accelerators
        self._build_header_bar()
        self._build_content()
        self._setup_accels()

    def emit(self, *args):
        GLib.idle_add(GObject.GObject.emit, self, *args)

    def run(self):
        # Load the completion entries
        self.model = []
        # List all the places icons
        theme = Gtk.IconTheme.get_default()
        icons = theme.list_icons('Places')
        folders = list(filter(filter_folders, icons))
        folders.sort()
        # Fill in the model (str: icon path, pixbuf)
        for folder in folders:
            self.model.append(folder)
        self.emit("loaded")
        return False

    def do_loaded(self):
        for folder in self.model:
            self._flowbox.add(FolderBox(folder))

    def _build_header_bar(self):
        # Header bar
        headerbar = Gtk.HeaderBar()
        headerbar_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                                      spacing=3)

        title = Gtk.Label()
        title.set_text(_("Icon Chooser"))
        title.get_style_context().add_class("title")
        headerbar_container.pack_start(title, False, False, 0)

        subtitle = Gtk.Label()
        subtitle.get_style_context().add_class("subtitle")
        subtitle_text = ", ".join(self._folders)
        subtitle.set_text(subtitle_text)
        subtitle.set_ellipsize(Pango.EllipsizeMode.END)
        subtitle.set_tooltip_text(subtitle_text)
        subtitle.props.max_width_chars = 30
        headerbar_container.pack_start(subtitle, False, False, 0)

        headerbar.set_custom_title(headerbar_container)
        headerbar.set_show_close_button(False)
        # Apply Button
        self._apply_button = Gtk.Button()
        self._apply_button.set_label(_("Apply"))
        self._apply_button.set_sensitive(False)
        self._apply_button.get_style_context().add_class("suggested-action")
        self._apply_button.connect("clicked", self._do_select)

        # Search Button
        self._search_btn = Gtk.ToggleButton()
        search_icn = Gio.ThemedIcon(name="system-search-symbolic")
        search_img = Gtk.Image.new_from_gicon(search_icn, Gtk.IconSize.BUTTON)
        self._search_btn.set_image(search_img)

        # Cancel Button
        cancel_button = Gtk.Button()
        cancel_button.set_label(_("Cancel"))
        cancel_button.connect("clicked", self._close_window)

        headerbar.pack_start(cancel_button)
        headerbar.pack_end(self._apply_button)
        headerbar.pack_end(self._search_btn)
        self.set_titlebar(headerbar)

    def _build_content(self):
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Search bar
        self._search_bar = Gtk.SearchBar()
        self._search_bar.set_show_close_button(True)

        self._search_btn.bind_property("active",
                                        self._search_bar,
                                        "search-mode-enabled",
                                        1)

        self._search_entry = Gtk.SearchEntry()
        self._search_entry.connect("search-changed", self._on_search)
        self._search_bar.add(self._search_entry)
        self._search_bar.connect_entry(self._search_entry)

        container.pack_start(self._search_bar, False, False, 0)

        # Preview image
        self._preview = Image()
        self._default_icon = get_default_icon(self._folders[0])
        self._preview.set_icon(self._default_icon)


        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self._flowbox = Gtk.FlowBox()
        self._flowbox.connect("selected-children-changed", self._on_select)
        self._flowbox.set_valign(Gtk.Align.START)
        self._flowbox.set_max_children_per_line(10)
        self._flowbox.set_selection_mode(Gtk.SelectionMode.SINGLE)

        scrolled.add(self._flowbox)

        container.pack_start(self._preview, False, False, 6)
        container.pack_start(scrolled, True, True, 6)

        self.add(container)


    def _setup_accels(self):
        self._accels = Gtk.AccelGroup()
        self.add_accel_group(self._accels)

        key, mod = Gtk.accelerator_parse("Escape")
        self._accels.connect(key, mod, Gtk.AccelFlags.VISIBLE,
                             self._close_window)

        key, mod = Gtk.accelerator_parse("Return")
        self._accels.connect(key, mod, Gtk.AccelFlags.VISIBLE,
                             self._do_select)

        key, mod = Gtk.accelerator_parse("<Control>F")
        self._accels.connect(key, mod, Gtk.AccelFlags.VISIBLE,
                            self._toggle_search)


    def _get_selected_icon(self):
        selected_child = self._flowbox.get_selected_children()[0].get_child()
        icon_name = selected_child.name
        return icon_name

    def _on_select(self, *args):
        icon_name = self._get_selected_icon()
        self._preview.set_icon(icon_name)
        self._apply_button.set_sensitive(True)

    def _do_select(self, *args):
        if self._apply_button.get_sensitive():
            self.emit("icon_selected", self._get_selected_icon())
            self._close_window()

    def _on_search(self, *args):
        data = self._search_entry.get_text().strip()
        self._flowbox.set_filter_func(self._filter_func, data, True)

    def _close_window(self, *args):
        self.destroy()

    def _toggle_search(self, *args):
        self._search_bar.set_search_mode(not self._search_bar.get_search_mode())

    def _filter_func(self, row, data, notify_destroy):
        folder_icon_name = row.get_child().name
        data = data.lower()
        if len(data) > 0:
            return data in folder_icon_name
        else:
            return True