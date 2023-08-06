"""

================================================================================

	mingus - Music theory Python package
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

	A Bar is basically a container for NoteContainers (a 
	NoteContainerContainer if you will, but you shouldn't).

================================================================================

"""

from mingus.core import meter as _meter
from NoteContainers import NoteContainer

class Bar:

	key = 'C'
	meter = (4, 4)
	current_beat = 0.0
	length = 0.0
	bar = []

	def __init__(self, key = 'C', meter=(4,4)):

		self.key = key
		self.set_meter(meter)	
		self.empty()

	def empty(self):
		"""Empties the Bar, removes all the NoteContainers"""
		self.bar = []
		self.current_beat = 0.0
		return self.bar

	def set_meter(self, meter):
		"""Meters in mingus are represented by a single tuple.
		This function will set the meter of this bar."""

		if _meter.valid_beat_duration(meter[1]):
			self.meter = (meter[0], meter[1])
			self.length = meter[0] * (1.0 / meter[1])
		elif meter == (0, 0):
			self.meter = (0, 0)
			self.length = 0.0
		else:
			# Raise exception
			return False


	def place_notes(self, notes, duration):
		"""Places the NoteContainer notes on the current_beat."""

		# note should be able to be strings, lists, Notes or NoteContainers

		if _meter.valid_beat_duration(duration):
			if self.current_beat + 1.0 / duration <= self.length or\
							self.length == 0.0:
				self.bar.append([self.current_beat, duration, notes])
				self.current_beat += 1.0 / duration
				return True
			else:
				return False
		else:
			# Raise exception
			return False

	def place_notes_at(self, notes, duration, at):
		for x in self.bar:
			if x[0] == at:
				x[0][2] += notes

	def place_rest(self, duration):
		return self.place_notes(None, duration)
	
	def remove_last_entry(self):
		self.current_beat -= 1.0 / self.bar[-1][1]
		self.bar = self.bar[:-1]
		return self.current_beat

	def is_full(self):
		"""Returns False if there is room in this Bar for another
		NoteContainer, True otherwise."""
		if self.length == 0.0:
			return False
		
		if self.current_beat + 1.0 / self.bars[-1][1] == self.length:
			return True

		return False

	def change_note_duration(self, at, to):
		if valid_beat_duration(to):
			diff = 0
			for x in self.bar:
				if diff != 0:
					x[0][0] -= diff
				if x[0] == at:
					cur = x[0][1]
					x[0][1] = to
					diff = 1/cur - 1/to

	def get_range(self):
		"""Returns the highest and the lowest note in a tuble"""
		min, max = (100000, -1)
		for cont in self.bar:
			for note in cont[2]:
				if int(note) < int(min):
					min = note
				elif int(note) > int(max):
					max = note
		return (min, max)


	def __add__(self, note_container):
		"""Enables the '+' operator on Bars"""
		self.place_notes(note_container, self.meter[1])

	def __getitem__(self, index):
		"""Allows you to use [index] notation on Bars to get the 
		item at the index."""
		return self.bar[index]

	def __setitem__(self, index, value):
		"""Allows you to use [] = notation on Bars. The value
		should be NoteContainer, or a string/list/Note understood
		by the NoteContainer."""
		if value == str:
			value = NoteContainer(value)
		self.bar[index][2] = value

	def __repr__(self):
		return str(self.bar)

	def __len__(self):
		return len(self.bar)
