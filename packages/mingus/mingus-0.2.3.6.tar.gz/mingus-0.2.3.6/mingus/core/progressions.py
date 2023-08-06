"""

================================================================================

	mingus - Music theory Python package, progressions module
	Copyright (C) 2008, Bart Spaans

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

================================================================================


================================================================================

"""

import chords

jazz = ["ii7", "V7", "I7"]

standard_blues = ["I", "I", "I", "I",\
				  "IV", "IV", "I", "I",\
				  "V7", "V7", "IV", "IV"]

def to_chords(progression, key):
	return map(lambda x: chords.__dict__[x](key), progression)
