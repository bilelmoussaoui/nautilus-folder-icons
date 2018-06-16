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
import unittest
from os import getenv, path, makedirs, rmdir
from sys import path as sys_path
from tempfile import NamedTemporaryFile

CURRENT_DIR = path.dirname(path.abspath(__file__))
ABS_PATH = path.abspath(path.join(CURRENT_DIR, "../"))
sys_path.insert(0, path.join(ABS_PATH, 'src/'))

from utils import is_path, get_ext, uriparse, get_default_icon, set_default_icon, restore_default_icon

USERNAME = getenv("SUDO_USER") or getenv("USER")
if USERNAME:
    HOME = path.expanduser("~" + USERNAME)
else:
    HOME = path.expanduser("~")

class TestUtils(unittest.TestCase):

    def test_is_path(self):
        self.assertEqual(is_path("test/icon.png"), True)
        self.assertEqual(is_path("/test/icon.png"), True)
        self.assertEqual(is_path("/"), True)
        self.assertEqual(is_path("test.png"), False)

    def test_get_ext(self):
        self.assertEqual(get_ext("test.png"), ".png")
        self.assertEqual(get_ext("test.test.png"), ".png")
        self.assertEqual(get_ext("test"), "")
        self.assertEqual(get_ext("test.PNG"), ".png")

    def test_get_default_icon(self):
        self.assertEqual(get_default_icon(path.join(HOME, "Videos")), "folder-videos")
        self.assertEqual(get_default_icon(path.join(HOME, "Music")), "folder-music")

        # Create a simple dir
        test_dir = path.join(HOME, NamedTemporaryFile().name)
        makedirs(test_dir)
        self.assertEqual(get_default_icon(test_dir), "folder")
        rmdir(test_dir)

    def test_set_default_icon(self):
        test_dir = path.join(HOME, NamedTemporaryFile().name)
        makedirs(test_dir)
        self.assertEqual(get_default_icon(test_dir), "folder")
        set_default_icon(test_dir, "folder-videos")
        self.assertEqual(get_default_icon(test_dir), "folder-videos")
        rmdir(test_dir)

    def test_restore_default_icon(self):
        test_dir = path.join(HOME, NamedTemporaryFile().name)
        makedirs(test_dir)
        self.assertEqual(get_default_icon(test_dir), "folder")
        set_default_icon(test_dir, "folder-videos")
        self.assertEqual(get_default_icon(test_dir), "folder-videos")
        restore_default_icon(test_dir)
        self.assertEqual(get_default_icon(test_dir), "folder")
        rmdir(test_dir)

if __name__ == "__main__":
    unittest.main()
