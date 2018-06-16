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
from glob import glob

try:
    import pycodestyle
except ImportError:
    print("Please install `pycodestyle` first.")
    exit(0)

CURRENT_DIR = path.dirname(path.abspath(__file__))
ABS_PATH = path.abspath(path.join(CURRENT_DIR, "../"))


class TestCodeFormat(unittest.TestCase):
    """Test Code format using pep8."""

    def setUp(self):
        self.style = pycodestyle.StyleGuide(show_source=True,
                                            ignore="E402")

    def test_code_format(self):
        """Test code format."""
        files = glob("{}/**/**/*.py".format(ABS_PATH))
        files.extend(glob("{}/**/**/*.py.in".format(ABS_PATH)))

        result = self.style.check_files(files)
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")


if __name__ == "__main__":
    unittest.main()
