#!/usr/bin/python2
"""
Change your nautilus directories icons easily

Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Version : 1.0
Website : https://github.com/bil-elmoussaoui/nautilus-git
Licence : GPL-3.0
nautilus-git is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
nautilus-git is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with nautilus-git. If not, see <http://www.gnu.org/licenses/>.
"""
from gettext import textdomain, gettext as _
from subprocess import Popen, PIPE
from urllib2 import unquote
from urlparse import urlparse

from gi import require_version
require_version("Gtk", "3.0")
require_version('Nautilus', '3.0')
from gi.repository import Gtk, Nautilus, GObject

textdomain('nautilus-folder-icons')


def get_default_icon(directory):
    attributes = ["metadata::custom-icon-name ", "standard::icon"]
    for attribute in attributes:
        command = ["gio", "info", directory, "-a", attribute]
        output, error = Popen(command,
                              stdout=PIPE,
                              stderr=PIPE).communicate()
        output = output.strip().split("\n")
        if len(output) == 3:
            print(output)
            icons = output[2].split(
                attribute)[-1].split(':')[-1].strip().split(",")
            print(icons)
            return icons[0]
        if error:
            print(error.decode("utf-8"))
    return "folder"


def set_folder_icon(folder, icon):

    command = ["gio", "set", folder,
               "metadata::custom-icon-name", icon]
    output, error = Popen(command,
                          stdout=PIPE,
                          stderr=PIPE).communicate()
    if error:
        print(error.decode("utf-8"))


class NautilusFolderIconsChooser(Gtk.Window, GObject.GObject):
    __gsignals__ = {
        'selected': (GObject.SIGNAL_RUN_FIRST, None, (str,))
    }

    def __init__(self, default_icon, parent):
        GObject.GObject.__init__(self)
        Gtk.Window.__init__(self)
        self._default_icon = default_icon
        self.set_border_width(18)
        self.set_transient_for(parent)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self._build_header_bar()
        self._build_content()

        self.show_all()

    def _build_header_bar(self):
        # Header bar
        hb = Gtk.HeaderBar()
        hb.set_title(_("Icon Chooser"))
        hb.set_show_close_button(False)

        # Apply Button
        self.apply_button = Gtk.Button()
        self.apply_button.set_label(_("Apply"))
        # self.apply_button.set_sensitive(False)
        self.apply_button.get_style_context().add_class("suggested-action")
        self.apply_button.connect("clicked", self._do_select)

        # Cancel Button
        cancel_button = Gtk.Button()
        cancel_button.set_label(_("Cancel"))
        cancel_button.connect("clicked", self._close_window)

        hb.pack_start(cancel_button)
        hb.pack_end(self.apply_button)
        self.set_titlebar(hb)

    def _build_content(self):
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                            spacing=6)

        container.set_halign(Gtk.Align.CENTER)
        container.set_valign(Gtk.Align.CENTER)
        # Preview image
        self._preview = Gtk.Image()
        self._preview.set_from_icon_name(self._default_icon,
                                         Gtk.IconSize.DIALOG)
        # Icon name entry
        self._icon_entry = Gtk.Entry()
        self._icon_entry.connect("changed", self._refresh_preview)

        container.pack_start(self._preview, False, False, 6)
        container.pack_start(self._icon_entry, False, False, 6)

        self.add(container)

    def _refresh_preview(self, entry):
        icon_name = entry.get_text().strip()
        if not icon_name:
            icon_name = self._default_icon
        self._preview.set_from_icon_name(icon_name,
                                         Gtk.IconSize.DIALOG)

    def _do_select(self, *args):
        self.emit("selected", self._icon_entry.get_text())
        self._close_window()

    def _close_window(self, *args):
        self.destroy()


class NautilusFolderIcons(GObject.GObject, Nautilus.MenuProvider):

    def get_file_items(self, window, files):
        if len(files) != 1:
            return
        file_ = files[0]
        if file_.is_directory():
            directory = file_.get_uri()

            item = Nautilus.MenuItem(name='NautilusPython::change_folder_icon',
                                     label=_('Folder Icon'),
                                     tip=_('Change folder icon of {}').format(directory))
            item.connect('activate', self._chagne_folder_icon,
                         directory, window)
            return [item]

    def _chagne_folder_icon(self, *args):
        directory = urlparse(args[1])
        parent = args[2]
        if directory.scheme == 'file':
            directory = unquote(directory.path)

            def set_icon(*args):
                icon_name = args[1]
                set_folder_icon(directory, icon_name)
                # Refresh Nautilus
                action = parent.lookup_action("reload")
                action.emit("activate", None)

            current_icon = get_default_icon(directory)

            icon = NautilusFolderIconsChooser(current_icon, parent)
            icon.connect("selected", set_icon)
