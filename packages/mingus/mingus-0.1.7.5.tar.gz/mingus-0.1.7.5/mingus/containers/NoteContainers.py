"""

================================================================================

	mingus - Music theory Python package, note containers.
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

	The NoteContainer provides a container for notes (hey, now!). 
	Interval is a direct subclass of NoteContainer and has some restrictions
	and extra methods on it to work comfortably with intervals.
	Chords does the same for chords.
	The NoteContainer in other words, is the most general container.

================================================================================

"""

from Note import Note
from mingus.core import intervals

class NoteContainer:
	"""An interface for things containing notes."""

	notes = []

	def __init__(self, notes = []):
		self.empty()
		self.add_notes(notes)

	def empty(self):
		"""Empties the container"""
		self.notes = []

	def add_note(self, note, octave = 4, dynamics = {}):
		"""Adds a note to the container and sorts the notes from low
		to high. The note can either be a string, in which case you can
		also use the octave and dynamics arguments, or a Note."""

		if type(note) == str:
			note = Note(note, octave, dynamics)
		if note not in self.notes:
			self.notes.append(note)
			self.notes.sort()
		return self.notes

	def add_notes(self, notes):
		"""Feeds notes to self.add_note. The notes can either be a list
		of Note objects or strings or a list of lists formatted like this:
			notes = [["C", 5], ["E", 5], ["G", 6]] 
		or even:
			notes = [["C", 5, {"volume" : 20}], ["E", 6, {"volume":20}]]"""
		if hasattr(notes, "notes"):
			for x in notes.notes:
				self.add_note(x)
			return self.notes
		elif hasattr(notes, "name"):
			self.add_note(notes)
			return self.notes

		for x in notes:
			if type(x) == list and len(x) != 1:
				if len(x) == 2:
					self.add_note(x[0], x[1])
				else:
					self.add_note(x[0], x[1], x[2])
			else:
				self.add_note(x)
		return self.notes

	def remove_note(self, note, octave = -1):
		"""Removes note from container. The note can either be a Note 
		object or a string representing the note's name. If no octave 
		is given, the note gets removed in every octave."""

		res = []
		for x in self.notes:
			if type(note) == str:
				if x.name != note:
					res.append(x)
				else:
					if x.octave != octave and octave != -1:
						res.append(x)
			else:
				if x != note:
					res.append(x)
		self.notes = res
		return res

	def remove_notes(self, notes):
		for x in notes:
			if type(x) == list and len(x) != 1:
				if len(x) == 2:
					self.remove_note(x[0], x[1])
			else:
				self.remove_note(x)
		return self.notes

	def remove_duplicate_notes(self):
		"""Removes duplicate and enharmonic notes from the container"""
		res = []
		for x in self.notes:
			if x not in res:
				res.append(x)
		self.notes = res
		return res

	def sort(self):
		"""Sorts the notes in the container from low to high."""
		self.notes.sort()

	def __repr__(self):
		"""A nice and clean representation of the note container"""
		return str(self.notes)

	def __getitem__(self, item):
		"""This method allows you to use the container as a simple array.
		Example:
			>>> n = NoteContainer(["C", "E", "G"])
			>>> n[0]
			'C-5' 
		"""
		return self.notes[item]

	def __setitem__(self, item, value):
		"""This allows you to use [] notation on NoteContainers.
		Examples:
			>>> n = NoteContainer(["C", "E", "G"])
			>>> n[0] = "B"
			["B-5", "E-5", "G-5"] """
		if type(value) == str:
			n = Note(value)
			self.notes[item] = n
		elif type(value) == list:
			if len(value) == 1:
				n = Note(value[0])
				self.notes[item] = n
			elif len(value) == 2:
				n = Note(value[0], value[1])
				self.notes[item] = n
			elif len(value) == 3:
				n = Note(value[0], value[1], value[2])
				self.notes[item] = n
		else:
			self.notes[item] = value
		return self.notes

	def __add__(self, notes):
		"""This method allows you to use '+' notation on NoteContainers.
		Example:
			>>> n = NoteContainer(["C", "E", "G"])
			>>> n + "B"
			["C-5", "E-5", "G-5", "B-5"] 
		"""
		self.add_notes(notes)
		return self.notes

	def __sub__(self, notes):
		"""This method allows you to use the '-' operator on NoteContainers.
		Example:
			>>> n = NoteContainer(["C", "E", "G"])
			>>> n - "E"
			["C-5", "G-5"]
		"""
		self.remove_notes(notes)
		return self.notes

	def __len__(self):
		"""Returns the number of notes in the container"""
		return len(self.notes)

	def __eq__(self, other):
		"""Overloads the == operator for NoteContainer instances."""
		for x in self:
			if x not in other:
				return False
		return True

class Interval(NoteContainer):

	notes = []

	def __init__(self, notes):
		NoteContainer.__init__(self, notes)

	def set_notes(self, notes):
		self.empty()
		self.add_notes(notes)

	def add_notes(self, notes):
		if len(self.notes) + len(notes) <= 2:
			NoteContainer.add_notes(self, notes)
			return self.notes
		return False

	def determine(self):
		return intervals.determine(self.notes[0].name, self.notes[1].name)

class Chord(NoteContainer):

	def __init__(self):
		NoteContainer.__init__(self, [])

	def set_notes(self, notes):
		self.empty()

	def add_notes(self, notes):
		pass

	def remove_notes(self, notes):
		pass

