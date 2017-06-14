#!/usr/bin/python2
"""
Change your nautilus directories icons easily

Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Version : 1.1
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
from gettext import textdomain
from os import path
from subprocess import PIPE, Popen
from urllib2 import unquote
from urlparse import urlparse

from gi import require_version
require_version("Gtk", "3.0")
require_version('Nautilus', '3.0')
from gi.repository import GdkPixbuf, Gio, GObject, Gtk, Nautilus

textdomain('nautilus-folder-icons')


def get_default_icon(directory):
    """Use Gio to get the default icon."""
    attributes = ["metadata::custom-icon",
                  "metadata::custom-icon-name",
                  "standard::icon"]

    gfile = Gio.File.new_for_path(directory)
    ginfo = gfile.query_info(",".join(attributes),
                             Gio.FileQueryInfoFlags.NOFOLLOW_SYMLINKS)

    for attribute in attributes:
        value = ginfo.get_attribute_string(attribute)
        if value is not None:
            return unquote(urlparse(value).path)
    return "folder"


def set_folder_icon(folder, icon):
    """Use Gio to set the default folder icon."""
    if not isinstance(folder, str):
        folder = folder.get_uri()
    folder = unquote(urlparse(folder).path)
    gfile = Gio.File.new_for_path(folder)
    # Property to set by default
    prop = "metadata::custom-icon-name"
    # Property to unsert by default
    # Otherwise Nautilus won't be able
    # to handle both icons at the same time
    unset_prop = "metadata::custom-icon"

    ginfo = gfile.query_info("{0},{1}".format(prop, unset_prop),
                             Gio.FileQueryInfoFlags.NOFOLLOW_SYMLINKS)
    # In case the icon is a path & not an icon name
    if len(icon.split("/")) > 1:
        prop, unset_prop = unset_prop, prop
        icon = "file://{}".format(icon)

    # Set the new icon name
    ginfo.set_attribute_string(prop, icon)
    ginfo.set_attribute_status(prop, Gio.FileAttributeStatus.SET)
    # Unset the other attribute
    ginfo.remove_attribute(unset_prop)
    ginfo.set_attribute_status(unset_prop, Gio.FileAttributeStatus.UNSET)
    # Remove attribute doesn't seem to work correctly.
    # File.set_attribute_from_info doesn't remove attributes
    Popen(["gio", "set", folder, "-t", "unset", unset_prop],
          stdout=PIPE, stderr=PIPE).communicate()
    # Set the attributes to the file
    gfile.set_attributes_from_info(ginfo,
                                   Gio.FileQueryInfoFlags.NOFOLLOW_SYMLINKS)


def change_folder_icon(folders, window):
    """Change default folder icon."""
    def set_icon(*args):
        """Set the folder icon & refresh Nautilus's view."""
        icon_name = args[1]
        for folder in folders:
            set_folder_icon(folder, icon_name)
        # Refresh Nautilus
        action = window.lookup_action("reload")
        action.emit("activate", None)
    # Show Icon Chooser window
    icon = NautilusFolderIconChooser(folders)
    icon.set_transient_for(window)
    icon.connect("selected", set_icon)
    icon.show_all()


def filter_folders(icon):
    """Filter icons to only show folder ones."""
    icon = icon.lower()
    return (icon.startswith("folder")
            and not icon.endswith("-symbolic"))


class Image(Gtk.Image):

    def __init__(self):
        Gtk.Image.__init__(self)

    def set_icon(self, icon_name):
        if len(icon_name.split("/")) > 1:
            # Make sure the icon name doesn't contain any special char
            icon_name = unquote(icon_name)
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(icon_name,
                                                             48, 48, True)
            self.set_from_pixbuf(pixbuf)
        else:
            self.set_from_icon_name(icon_name,
                                    Gtk.IconSize.DIALOG)


class NautilusFolderIconChooser(Gtk.Window, GObject.GObject):
    __gsignals__ = {
        'selected': (GObject.SIGNAL_RUN_FIRST, None, (str, ))
    }

    def __init__(self, folders):
        GObject.GObject.__init__(self)
        Gtk.Window.__init__(self)

        if len(folders) == 1:
            folder = urlparse(folders[0].get_uri()).path
            self._folder_path = folder
            self._default_icon = get_default_icon(folder)
        else:
            self._folder_path = _("Number of folders: {}").format(str(len(folders)))
            self._default_icon = "folder"
        # Window configurations
        self.set_default_size(350, 150)
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
        headerbar.set_title(_("Icon Chooser"))
        headerbar.set_subtitle(self._folder_path)
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
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                            spacing=6)
        container.set_halign(Gtk.Align.CENTER)
        container.set_valign(Gtk.Align.CENTER)

        # Preview image
        self._preview = Image()
        self._preview.set_icon(self._default_icon)

        hz_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,
                               spacing=6)
        # Icon name entry
        self._icon_entry = Gtk.Entry()
        self._icon_entry.set_text(self._default_icon)
        self._icon_entry.connect("changed", self._refresh_preview)
        self._icon_entry.grab_focus_without_selecting()

        # Icon Completion
        completion = Gtk.EntryCompletion()
        model = Gtk.ListStore(str, GdkPixbuf.Pixbuf)
        # List all the places icons
        theme = Gtk.IconTheme.get_default()
        icons = theme.list_icons('Places')
        folders = list(filter(filter_folders, icons))
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
        self._icon_entry.set_completion(completion)

        # Icon file selector
        select_file = Gtk.Button()
        select_icon = Gio.ThemedIcon(name="document-open-symbolic")
        select_image = Gtk.Image.new_from_gicon(select_icon,
                                                Gtk.IconSize.BUTTON)
        select_file.set_image(select_image)
        select_file.get_style_context().add_class("flat")
        select_file.connect("clicked", self._on_select_file)

        hz_container.pack_start(self._icon_entry, False, False, 6)
        hz_container.pack_start(select_file, False, False, 6)

        container.pack_start(self._preview, False, False, 6)
        container.pack_start(hz_container, False, False, 6)

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

    def _on_select_file(self, button):
        dialog = Gtk.FileChooserDialog(_("Select an icon"), self,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        # Filter images
        filter_images = Gtk.FileFilter()
        filter_images.set_name("Image files")
        filter_images.add_mime_type("image/png")
        filter_images.add_mime_type("image/svg+xml")
        dialog.add_filter(filter_images)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            icon_path = urlparse(dialog.get_uri()).path
            self._icon_entry.set_text(icon_path)
        dialog.destroy()

    def _refresh_preview(self, entry):
        icon_name = entry.get_text().strip()
        # Fallback to the default icon
        if not icon_name:
            icon_name = self._default_icon
        # No need to set the same icon again?
        self._apply_button.set_sensitive(icon_name != self._default_icon)

        self._preview.set_icon(icon_name)

    def _do_select(self, *args):
        self.emit("selected", self._icon_entry.get_text())
        self._close_window()

    def _close_window(self, *args):
        self.destroy()


class OpenFolderIconProvider(GObject.GObject,
                             Nautilus.LocationWidgetProvider):

    def __init__(self):
        self._window = None
        self._uri = None

    def _create_accel_group(self):
        self._accel_group = Gtk.AccelGroup()
        key, mod = Gtk.accelerator_parse("<Shift><Ctrl>S")
        self._accel_group.connect(key, mod, Gtk.AccelFlags.VISIBLE,
                                  self._open_folder_icon)

    def _open_folder_icon(self, *args):
        change_folder_icon(self._uri, self._window)

    def get_widget(self, uri, window):
        self._uri = uri
        if self._window:
            self._window.remove_accel_group(self._accel_group)
        if path.isdir(urlparse(unquote(self._uri)).path):
            self._create_accel_group()
            window.add_accel_group(self._accel_group)
        self._window = window
        return None


class NautilusFolderIcons(GObject.GObject, Nautilus.MenuProvider):

    def get_file_items(self, window, files):
        # Force use to select only directories
        for file_ in files:
            if not file_.is_directory() and file_.get_uri_scheme() != "file":
                return False

        item = Nautilus.MenuItem(name='NautilusPython::change_folder_icon',
                                 label=_('Folder Icon'),
                                 tip=_('Change folder icon'))
        item.connect('activate', self._chagne_folder_icon, files, window)
        return [item]


    def _chagne_folder_icon(self, *args):
        change_folder_icon(args[1], args[2])
