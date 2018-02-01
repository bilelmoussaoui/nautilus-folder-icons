"""
Your favorite Audio Cutter.
Author : Bilal Elmoussaoui (bil.elmoussaoui@gmail.com)
Artist : Alfredo Hernández
Website : https://github.com/bil-elmoussaoui/Audio-Cutter
Licence : The script is released under GPL, uses a modified script
     form Chromium project released under BSD license
This file is part of AudioCutter.
AudioCutter is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
AudioCutter is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with AudioCutter. If not, see <http://www.gnu.org/licenses/>.
"""
import unittest
from os import path
from glob import glob

import pycodestyle

ABS_PATH = path.abspath(path.join(path.dirname(path.abspath(__file__)),
                                  "../"))


class TestCodeFormat(unittest.TestCase):
    """Test Code format using pep8."""

    def setUp(self):
        self.style = pycodestyle.StyleGuide(show_source=True,
                                            ignore="E402")

    def test_code_format(self):
        """Test code format."""

        files = glob("{}/**/*.py".format(ABS_PATH))
        result = self.style.check_files(files)
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")


if __name__ == "__main__":
    unittest.main()
