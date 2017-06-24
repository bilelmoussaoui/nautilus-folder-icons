#!/usr/bin/python2
"""
Change your nautilus directories icons easily

Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Version : 2.0
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
from os import path
from urllib2 import unquote
from urlparse import urlparse

from gi import require_version
require_version("Gtk", "3.0")
from gi.repository import GdkPixbuf, Gio, Gtk


SUPPORTED_EXTS = [".svg", ".png"]


class Image(Gtk.Image):

    def __init__(self):
        Gtk.Image.__init__(self)

    def set_icon(self, icon_name):
        icon_name = uriparse(icon_name)
        if is_path(icon_name):
            # Make sure the icon name doesn't contain any special char
            ext = get_ext(icon_name)
            # Be sure that the icon still exists on the system
            if path.exists(icon_name) and ext in SUPPORTED_EXTS:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(icon_name,
                                                                 48, 48, True)
                self.set_from_pixbuf(pixbuf)
            else:
                self.set_from_icon_name("image-missing",
                                        Gtk.IconSize.DIALOG)
        else:
            self.set_from_icon_name(icon_name,
                                    Gtk.IconSize.DIALOG)


def get_default_icon(directory):
    """Use Gio to get the default icon."""
    attributes = ["metadata::custom-icon",
                  "metadata::custom-icon-name",
                  "standard::icon"]

    gfile = Gio.File.new_for_path(directory)
    ginfo = gfile.query_info("standard::icon,metadata::*",
                             Gio.FileQueryInfoFlags.NOFOLLOW_SYMLINKS)

    for attribute in attributes:
        if ginfo.has_attribute(attribute):
            value = ginfo.get_attribute_string(attribute)
            if value is not None:
                return uriparse(value)
    return "folder"


def set_folder_icon(folder, icon):
    """Use Gio to set the default folder icon."""
    gfile = Gio.File.new_for_path(folder)
    # Property to set by default
    prop = "metadata::custom-icon-name"
    # Property to unsert by default
    # Otherwise Nautilus won't be able
    # to handle both icons at the same time
    unset_prop = "metadata::custom-icon"

    ginfo = gfile.query_info("metadata::*",
                             Gio.FileQueryInfoFlags.NOFOLLOW_SYMLINKS)
    # In case the icon is a path & not an icon name
    if is_path(icon):
        prop, unset_prop = unset_prop, prop
        icon = "file://{}".format(icon)

    # Set the new icon name
    ginfo.set_attribute_string(prop, icon)
    ginfo.set_attribute_status(prop, Gio.FileAttributeStatus.SET)
    # Unset the other attribute
    if ginfo.has_attribute(unset_prop):
        ginfo.set_attribute(unset_prop,
                            Gio.FileAttributeType.INVALID, 0)
    # Set the attributes to the file
    gfile.set_attributes_from_info(ginfo,
                                   Gio.FileQueryInfoFlags.NOFOLLOW_SYMLINKS)


def change_folder_icon(folders, window):
    """Change default folder icon."""
    from icons_select import FolderIconChooser

    def set_icon(*args):
        """Set the folder icon & refresh Nautilus's view."""
        icon_name = args[1]
        for folder in folders:
            set_folder_icon(folder, icon_name)
        # Refresh Nautilus (doesn't work on Nemo...)
        if window.has_action("reload"):
            action = window.lookup_action("reload")
            action.emit("activate", None)
    # Show Icon Chooser window
    icon = FolderIconChooser(folders)
    icon.set_transient_for(window)
    icon.connect("selected", set_icon)
    icon.show_all()


def filter_folders(icon):
    """Filter icons to only show folder ones."""
    icon = icon.lower()
    return (icon.startswith("folder")
            and not icon.endswith("-symbolic"))


def uriparse(uri):
    """Uri parser & return the path."""
    if not isinstance(uri, str):
        uri = uri.get_uri()
    return unquote(urlparse(uri).path)


def is_path(icon):
    """Returns whether an icon is an absolute path or an icon name."""
    return len(icon.split("/")) > 1


def get_ext(filepath):
    """Returns file extension."""
    return path.splitext(filepath)[1].lower()