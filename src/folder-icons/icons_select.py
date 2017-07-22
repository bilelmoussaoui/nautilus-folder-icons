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

from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import GdkPixbuf, Gio, GObject, Gtk, Pango

from utils import (SUPPORTED_EXTS, Image, filter_folders, get_default_icon,
                   get_ext, is_path, uriparse)




class FolderIconChooser(Gtk.Window, GObject.GObject):
    __gsignals__ = {
        'selected': (GObject.SIGNAL_RUN_FIRST, None, (str, ))
    }

    def __init__(self, folders):
        GObject.GObject.__init__(self)
        Gtk.Window.__init__(self)
        # Here i assume that all folders got the same icon...
        self._folders = folders
        # Window configurations
        self.set_default_size(350, 150)
        self.set_size_request(350, 150)
        self.set_border_width(18)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)

        # Widgets & Accelerators
        self._build_header_bar()
        self._build_content()
        self._setup_accels()

    def _build_header_bar(self):
        # Header bar
        headerbar = Gtk.HeaderBar()
        headerbar_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)

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

        # Cancel Button
        cancel_button = Gtk.Button()
        cancel_button.set_label(_("Cancel"))
        cancel_button.connect("clicked", self._close_window)

        headerbar.pack_start(cancel_button)
        headerbar.pack_end(self._apply_button)
        self.set_titlebar(headerbar)

    def _build_content(self):
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        container.set_halign(Gtk.Align.CENTER)
        container.set_valign(Gtk.Align.CENTER)

        # Preview image
        self._preview = Image()
        self._default_icon = get_default_icon(self._folders[0])
        self._preview.set_icon(self._default_icon)

        hz_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,
                               spacing=6)
        # Icon name entry
        self._icon_entry = Gtk.Entry()
        if self._default_icon:
            self._icon_entry.set_text(self._default_icon)
        else:
            self._icon_entry.set_text("folder")
        self._icon_entry.connect("changed", self._refresh_preview)
        self._icon_entry.grab_focus_without_selecting()

        # Icon Completion
        completion = Gtk.EntryCompletion()
        model = Gtk.ListStore(str, GdkPixbuf.Pixbuf)
        # List all the places icons
        theme = Gtk.IconTheme.get_default()
        icons = theme.list_icons('Places')
        folders = list(filter(filter_folders, icons))
        folders.sort()
        # Fill in the model (str: icon path, pixbuf)
        for folder in folders:
            icon = theme.load_icon(folder, 24, 0)
            model.append([folder, icon])

        pixbuf = Gtk.CellRendererPixbuf()
        completion.pack_start(pixbuf, False)
        completion.add_attribute(pixbuf, 'pixbuf', 1)
        completion.set_model(model)
        completion.set_text_column(0)
        completion.set_popup_set_width(True)
        completion.set_popup_single_match(True)
        completion.set_match_func(self._filter_func)
        self._icon_entry.set_completion(completion)

        # Icon file selector
        select_file = Gtk.Button()
        select_icon = Gio.ThemedIcon(name="document-open-symbolic")
        select_image = Gtk.Image.new_from_gicon(select_icon,
                                                Gtk.IconSize.BUTTON)
        select_file.set_image(select_image)
        select_file.get_style_context().add_class("flat")
        select_file.connect("clicked", self._on_select_file)

        hz_container.pack_start(self._icon_entry, False, False, 3)
        hz_container.pack_start(select_file, False, False, 3)

        container.pack_start(self._preview, False, False, 6)
        container.pack_start(hz_container, False, False, 6)

        self.add(container)

    def _filter_func(self, completion, data, iterr):
        model = completion.get_model()
        return data in model[iterr][0]

    def _setup_accels(self):
        self._accels = Gtk.AccelGroup()
        self.add_accel_group(self._accels)

        key, mod = Gtk.accelerator_parse("Escape")
        self._accels.connect(key, mod, Gtk.AccelFlags.VISIBLE,
                             self._close_window)

        key, mod = Gtk.accelerator_parse("Return")
        self._accels.connect(key, mod, Gtk.AccelFlags.VISIBLE,
                             self._do_select)

    def _on_select_file(self, *args):
        dialog = Gtk.FileChooserDialog(_("Select an icon"), self,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        # Filter images
        filter_images = Gtk.FileFilter()
        filter_images.set_name(_("Image files"))
        filter_images.add_mime_type("image/png")
        filter_images.add_mime_type("image/svg+xml")
        dialog.add_filter(filter_images)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            icon_path = uriparse(dialog.get_uri())
            self._icon_entry.set_text(icon_path)
        dialog.destroy()

    def _refresh_preview(self, entry):
        icon_name = uriparse(entry.get_text().strip())
        entry.set_text(icon_name)
        # Fallback to the default icon
        if not icon_name:
            icon_name = self._default_icon
        # No need to set the same icon again?
        exists = False
        if is_path(icon_name):
            ext = get_ext(icon_name)
            exists = (path.exists(icon_name)
                      and ext in SUPPORTED_EXTS)
        else:
            theme = Gtk.IconTheme.get_default()
            exists = theme.has_icon(icon_name)
        self._apply_button.set_sensitive(exists and icon_name)
        if exists:
            self._preview.set_icon(icon_name)
        else:
            self._preview.set_icon("image-missing")

    def _do_select(self, *args):
        if self._apply_button.get_sensitive():
            self.emit("selected", self._icon_entry.get_text())
            self._close_window()

    def _close_window(self, *args):
        self.destroy()
