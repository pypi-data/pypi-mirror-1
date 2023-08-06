"""

================================================================================

	mingus - Music theory Python package, composition module
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
	
	The composition module provides a way to build compositions from 
	tracks and instruments. The module works with the fundaments provided
	by notes and meter and is just one of the many possible ways to implement
	a song or composition.

================================================================================

"""

class Composition:

	title = 'Untitled'
	subtitle = ''
	author = ''
	email = ''
	tracks = []

	def __init__(self):
		self.tracks = []

	def empty(self):
		self.tracks = []

	def reset(self):
		self.empty()
		self.set_title()
		self.set_author()

	def add_track(self, track, instrument):
		self.tracks.append([track, instrument])

	def add_note(self, note, tracks = []):
		pass

	def set_title(self, title = 'Untitled', subtitle = ''):
		self.title = title
		self.subtitle = subtitle

	def set_author(self, author = '', email = ''):
		self.author = author
		self.email = email


