"""
================================================================================

	mingus - Music theory Python package, Note class.
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

	In the mingus.core module, notes are generally represented by strings.
	Most of the times, this is not enough. We want to set the octave and
	maybe the amplitude or vibrato. Then we want to store the notes in bars,
	the bars in tracks, the tracks in compositions, etc.

	We could do this with a number of lists, but ultimately it is a lot 
	easier to use objects. The Note class provides an easy way to deal 
	with notes in an object oriented matter.

	You can use the classes in NoteContainers to store the Notes in other
	objects.

================================================================================

"""

from mingus.core import notes

__all__ = ['Note']

class Note:

	name = 'C'
	octave = 5
	dynamics = { "volume" : 64 }

	def __init__(self, name = 'C', octave = 5, dynamics = {}):
		self.set_note(name, octave, dynamics)

	def set_note(self, name = 'C', octave = 5, dynamics = {}):
		"""Sets the note to name in octave with dynamics if
		the name of the note is valid. Returns True if it 
		succeeded, False otherwise."""
		dash_index = name.split('-')
		if len(dash_index) == 1:
			if notes.is_valid_note(name):
				self.name = name
				self.octave = octave
				self.dynamics = dynamics
				return True
			else:
				#Raise exception
				return False
		elif len(dash_index) == 2:
			if notes.is_valid_note(dash_index[0]):
				self.name = dash_index[0]
				self.octave = int(dash_index[1])
				self.dynamics = dynamics
				return True
			else:
				#Raise exception
				return False
		return False

	def empty(self):
		self.name = ''
		octave = 0
		dynamics = {}

	def augment(self):
		"""Calls notes.augment with this note as argument"""
		self.name = notes.augment(self.name)
	
	def diminish(self):
		"""Calls notes.diminish with this note as argument"""
		self.name = notes.diminish(self.name)

	def change_octave(self, diff):
		self.octave += diff
		if self.octave < 0:
			self.octave = 0

	def octave_up(self):
		self.change_octave(1)

	def octave_down(self):
		self.change_octave(-1)

	def to_minor(self):
		"""Calls notes.to_minor with this note as argument. 
		Doesn't change the octave."""
		self.name = notes.to_minor(self.name)

	def to_major(self):
		"""Calls notes.to_major with this note name as argument.
		Doesn't change the octave."""
		self.name = notes.to_major(self.name)

	def remove_redundant_accidentals(self):
		"""Calls notes.remove_redundant_accidentals on this
		note's name."""
		self.name = notes.remove_redundant_accidentals(self.name)

	def __int__(self):
		"""Returns the current octave multiplied by twelve and adds
		notes.note_to_int to it. This means a C-0 returns 0, C-1 
		returns 12, etc. This method allows you to use int() on Notes."""
		return self.octave * 12 + notes.note_to_int(self.name)

	def __cmp__(self, other):
		"""This method allows you to use the comparing operators
		on Notes (>, <, ==, !=, >= and <=). So we can sort() Intervals, etc.
		Examples:
			Note("C") < Note("B") returns True
			Note("C") < Note("B", 4) returns False"""
		s = int(self)
		o = int(other)
		if s < o:
			return -1
		elif s > o:
			return 1
		else:
			return 0

	def __repr__(self):
		"""A helpful representation for printing Note classes"""
		return "'%s-%d'" %  (self.name, self.octave)


	
