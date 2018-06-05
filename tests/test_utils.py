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
from os import path
from sys import path as sys_path


CURRENT_DIR = path.dirname(path.abspath(__file__))
ABS_PATH = path.abspath(path.join(CURRENT_DIR, "../"))
sys_path.insert(0, path.join(ABS_PATH, 'src/'))

from icons_utils import is_path, get_ext, uriparse

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




if __name__ == "__main__":
    unittest.main()
