"""

================================================================================

	mingus - Music theory Python package, Track module
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

	The Track Class can be used to store and work on Bars. It's also 
	designed to be used with Instruments in mind.

================================================================================

"""

from mt_exceptions import InstrumentRangeError

class Track:

	bars = []
	instrument = None

	def __init__(self, instrument = None):
		self.bars = []
		self.instrument = instrument

	def add_bar(self, bar):
		"""Adds a bar to the current track"""
		self.bars.append(bar)


	def add_notes(self, note, duration = None):
		"""Adds a Note, note as string or NoteContainer to the 
		last Bar. If the Bar is full, a new one will automatically
		be created. If the Bar is not full but the note can't fit in,
		this method will return False. True otherwise. 
		An InstrumentRangeError exception is being raised if an 
		instrument is attached to the Track, but the note is not 
		within the range of the instrument."""

		if self.instrument != None:
			if not(self.instrument.can_play_notes(note)):
				raise InstrumentRangeError,\
					"Note '%s' is not in range of the instrument (%s)"\
					% (note, self.instrument)

		if duration == None:
			duration = 4

		# Check whether the last bar is full,
		# if so create a new bar and add the note there
		last_bar = self.bars[-1]
		if last_bar.is_full():
			self.bars.append(Bar(last_bar.key, last_bar.meter))

		return self.bars[-1].place_notes(note, duration)
		

	def __add__(self, value):
		"""Overloads the + operator for Tracks. Accepts Notes, 
		notes as string, NoteContainers and Bars."""

		if hasattr(value, "bar"):
			return self.add_bar(value)
		elif hasattr(value, "notes"):
			return self.add_notes(value)
		elif hasattr(value, "name") or type(value) == str:
			return self.add_notes(value)

	def test_integrity(self):
		"""Test whether all but the last bars contained
		in this track are full."""
		for b in self.bars[:-1]:
			if not ( b.is_full() ):
				return False
		return True

	def __getitem__(self, index):
		"""Overloads the [] notation for Tracks"""
		return self.bars[index]

	def __setitem__(self, index, value):
		"""Overloads the [] = notation for Tracks. Throws an
		UnexpectedObjectError if the value being set is not a
		mingus.containers.Bar object."""

		if not ( hasattr (value, "bar") ):
			raise UnexpectedObjectError,\
				"Unexpected object '%s', expecting a mingus.containers.Bar"\
				"object" % value
		self.bars[index] = value

	def __repr__(self):
		"""The string representation of the class"""
		return str([self.instrument,str(self.bars)])

	def __len__(self):
		"""Overloads the len() function for Tracks."""
		return len(self.bars)
