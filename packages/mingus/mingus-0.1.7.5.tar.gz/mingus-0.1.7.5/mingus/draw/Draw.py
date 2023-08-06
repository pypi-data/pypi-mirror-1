"""

================================================================================

	mingus - Music theory Python package, Draw module
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

from PIL import Image, ImageDraw
import mingus.containers.Note as Note
from mingus.core import notes
import os

class Draw:

	current_instrument = None
	scale = 1.0
	bg_color = "#ffffff"
	fg_color = "#000000"

	def __init__(self):
		pass

	def set_scale(self, scale):
		self.scale = scale

	def zoom_in(self):
		scale *= 2.0

	def zoom_out(self):
		scale /= 2.0

	# Functions to draw the container objects
	def draw_Note(self):
		pass

	def draw_Bar(self):
		pass

	def draw_Track(self):
		pass

	def draw_Composition(self):
		pass

	def draw_Suite(self):
		pass


	# Functions to help draw the container objects
	def draw_empty_bar(self, size, offset):
		"""

			size is a tuple (width, height)
			offset is a tuple (offset_left_right, offset_top_bottom)
		"""
		pass

	def empty_surface(self, size):
		return Image.new("RGB", size, self.bg_color)

	def guess_clef(self, range):
		"""A helper function to guess the clef in which to represent
		a range"""
		if range[0] > Note("A", 4):
			return 'treble'
		else:
			if range[1] < Note("E", 4):
				return 'bass'
			else:
				return 'bass and treble'

class DrawClassic(Draw):

	last_key = ""
	note_diameter = 8
	accidental_height = 15

	def __init__(self):
		Draw.__init__(self)

	def draw_Bar(self, bar, size):
		i = self.empty_surface(size)

		# If no instrument is set (we are drawing a single Bar 
		# instead of a Track containing an Instrument) we should find
		# the range and figure out the clef.

		if self.current_instrument == None:
			range = bar.get_range()
			clef = self.guess_clef(range)

		# An instrument is set.
		else:
			clef = self.current_instrument.clef

		# Does the key need to be drawn?
		# Needs more code for modulation (key change)
		if self.last_key != bar.key:
			self.draw_key(bar.key, i)

		#!!!!!!!!!! DEBUG HACK REMOVE THIS HACK DEBUG!!!!!!!!!!!!#
		clef = 'treble'

		if clef == 'treble':
			result, offsety = self.draw_empty_bar(size)

			draw = ImageDraw.Draw(result)
			note_names = ["C", "D", "E", "F", "G", "A", "B"]

			# Resize the clef and paste it onto the empty bar
			cl = self.draw_clef(clef)
			clheight = int(5 * self.note_diameter * self.scale)
			cl = cl.resize((int(cl.size[0] * clheight / float(cl.size[1])), clheight))
			cloffsetx = max(10, size[0] / 10 - cl.size[0])
			result.paste(cl, (cloffsetx, offsety - self.note_diameter), cl)


			note_offset = max(20 + cl.size[0], size[0] / 5)

			# Draw the notes on the empty bar
			for bar_entry in bar:
				t, dur, nc = bar_entry
				x1 = t * (size[0] - note_offset) + note_offset
				x2 = int(x1 + self.scale * self.note_diameter - 2)
				
				for n in nc.notes:
					# draw notes
					y1 = note_names.index(n.name[0]) * (-1 * self.scale * self.note_diameter / 2) + (offsety + self.scale * self.note_diameter * 5) - (self.note_diameter * self.scale / 2)
					y1 = y1 - int((n.octave - 4) * 3.5 * self.scale * self.note_diameter)
					y2 = y1 + self.note_diameter * self.scale
					draw.ellipse([x1, y1, x2, y2], self.fg_color)
					if dur < 4:
						draw.ellipse([x1 + 1, y1 + 2, x2 - 1, y2 - 2], self.bg_color)

					# draw accidentals
					i = 1
					for acc in n.name[1:]:
						ac = self.draw_accidental(acc)
						ac = ac.resize((int(ac.size[0] * ((self.note_diameter * self.scale * 1.5) / ac.size[1])), int(self.scale * self.note_diameter * 1.5)))
						result.paste(ac, (x1 - (i * (ac.size[0] + 2)), y1 - self.scale * self.note_diameter / 4) ,ac)
						i += 1

				# draw note values
				nc.notes.sort()
				range= (nc.notes[0], nc.notes[-1])
				a = int(range[0]) - int(Note("B", 4))
				b = int(range[1]) - int(Note("B", 4))
				if self.get_position_y(clef, range[0], offsety) > self.get_position_y(clef, Note("B", 4), offsety):
					# Down 
					if a < b:
						draw.line([ x2, self.get_position_y(clef, range[0], offsety) + self.scale * self.note_diameter * 2 , x2, self.get_position_y(clef, range[1], offsety) + self.scale * self.note_diameter / 2], self.fg_color)
				else:
					# Up
					draw.line([ x2, self.get_position_y(clef, range[0], offsety) + self.scale * self.note_diameter / 2, x2, self.get_position_y(clef, range[1], offsety) - self.scale * self.note_diameter * 2], self.fg_color)


			return result
		elif clef == 'bass and treble':
			return self.draw_empty_bar(i, size)

	def get_position_y(self, clef, note, offsety):
		note_names = ["C", "D", "E", "F", "G", "A", "B"]
		if clef == "treble":
			n = note_names.index(note.name[0]) * (-1 * self.scale * self.note_diameter / 2)\
							+ (offsety + self.scale * self.note_diameter * 5) - (self.note_diameter * self.scale / 2)
			return n - int((note.octave - 4) * 3.5 * self.scale * self.note_diameter)


	# Helper functions
	def draw_empty_bar(self, size):
		i = self.empty_surface(size)
		draw = ImageDraw.Draw(i)
		width, height = size

		# Calculate vertical offset
		minimal_height_needed = int(4 * self.note_diameter * self.scale)
		if minimal_height_needed > height:
			# Raise exception; can't fit bar in size
			return False
	
		offsety = (height - minimal_height_needed) / 2

		# Paint the lines
		for y_counter in range(0, 5):
			y = offsety + int(y_counter * self.note_diameter * self.scale)
			draw.line([(0, y), (width, y)], self.fg_color)

		return (i, offsety)

	def draw_clef(self, clef):
		if clef == "treble":
			# Make this cross platform with os.join
			return Image.open(os.path.join("data", "gclef.png"))

	def draw_accidental(self, accidental):
		if accidental == "#":
			return Image.open(os.path.join("data", "sharp.png"))
		elif accidental == "b":
			return Image.open(os.path.join("data", "flat.png")).convert("RGBA")
		elif accidental == "natural":
			return Image.open(os.path.join("data", "natural.gif"))

	def draw_key(self, key, surface):
		pass


class DrawTablature(Draw):

	def __init__(self):
		Draw.__init__(self)
