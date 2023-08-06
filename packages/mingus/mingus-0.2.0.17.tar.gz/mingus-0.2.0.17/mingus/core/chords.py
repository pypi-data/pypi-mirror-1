"""
================================================================================

	Music theory Python package, chords module
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

	The chords module builds on the [refMingusCoreIntervals intervals]
	module to provide easy ways to handle chords.

================================================================================
"""

import intervals
import notes
import diatonic

#
#	Triads
#


# diatonic

def triad(note, key):
	"""Returns the triad on note in key as a list.
	Example:
{{{
>>> triad("E", "C") 
["E", "G", "B"]
>>> triad("E", "B")
["E", "G#", "B"]
}}}"""
	return [note, intervals.third(note, key), intervals.fifth(note, key)]


triads_cache = {}

def triads(key):
	"""Returns all the triads in key. Implemented using a cache."""
	
	if triads_cache.has_key(key):
		return triads_cache[key]
	res = map(lambda x: triad(x, key), diatonic.get_notes(key))
	triads_cache[key] = res
	return res

# absolute
def major_triad(note):
	"""Builds a major triad on note.
	Example:
{{{
>>> major_triad("C")
["C", "E", "G"]
}}}"""
	return [note, intervals.major_third(note), intervals.perfect_fifth(note)]

def minor_triad(note):
	"""Builds a minor triad on note.
	Example:
{{{
>>> minor_triad("C")
["C", "Eb", "G"]
}}}"""
	return [note, intervals.minor_third(note), intervals.perfect_fifth(note)]

def diminished_triad(note):
	"""Builds a diminished triad on note.
	Example:
{{{
>>> diminished_triad("C")
["C", "Eb", "Gb"]
}}}"""
	return [note, intervals.minor_third(note), intervals.minor_fifth(note)]

def augmented_triad(note):
	"""Builds an augmented triad on note.
	Example:
{{{
>>> augmented_triad("C")
["C", "E", "G#"]
}}}"""
	return [note, intervals.major_third(note),\
					notes.augment(intervals.major_fifth(note))]

def suspended_triad(note):
	"""Builds a suspended triad on note.
	Example:
{{{
>>> suspended_triad("C")
["C", "F", "G"]
}}}"""
	return [note, intervals.perfect_fourth(note), intervals.perfect_fifth(note)]

#
#	Sevenths
#

# diatonic
def seventh(note, key):
	"""Returns the seventh chord on note in key.
	Example:
{{{
>>> seventh("C", "C")
["C", "E", "G", "B"]
}}}"""
	return triad(note, key) + [intervals.seventh(note, key)]

sevenths_cache = {}
def sevenths(key):
	"""Returns all the sevenths chords in key in a list"""
	if sevenths_cache.has_key(key):
		return sevenths_cache[key]
	
	res = map(lambda x: seventh(x, key), diatonic.get_notes(key))
	sevenths_cache[key] = res
	return res

#absolute
def major_seventh(note):
	"""Builds a major seventh on note.
	Example:
{{{
>>> major_seventh("C") 
["C", "E", "G", "B"]
}}}"""
	return major_triad(note) + [intervals.major_seventh(note)]

def minor_seventh(note):
	"""Builds a minor seventh on note.
	Example:
{{{
>>> minor_seventh("C")
["C", "Eb", "G", "Bb"]
}}}"""
	return minor_triad(note) + [intervals.minor_seventh(note)]

def dominant_seventh(note):
	"""Builds a dominant seventh on note.
	Example:
{{{
>>> dominant_seventh("C")
["C", "E", "G", "Bb"]
}}}"""
	return major_triad(note) + [intervals.minor_seventh(note)]

def half_diminished_seventh(note):
	"""Builds a half diminished seventh (=minor seventh flat five) \
chord on note.
	Example:
{{{
>>> half_diminished_seventh("C")
["C", "Eb", "Gb", "Bb"]
}}}"""
	return diminished_triad(note) + [intervals.minor_seventh(note)]

def minor_seventh_flat_five(note):
	"""See half_diminished_seventh(note) for docs"""
	return half_diminished_seventh(note)

def diminished_seven(note):
	"""Builds a diminished seventh chord on note.
	Example:
{{{
>>> diminished_seven("C") 
["C", "Eb", "Gb", "Bbb"]
}}}"""
	return diminished_triad(note) + [notes.diminish(\
					intervals.minor_seventh(note))]

def minor_major_seventh(note):
	"""Builds a minor major seventh chord on note.
	Example:
{{{
>>> minor_major_seventh("C")
["C", "Eb", "G", "B"]
}}}"""
	return minor_triad(note) + [intervals.major_seventh(note)]

def augmented_major_seventh(note):
	"""Builds an augmented major seventh chord on note.
	Example:
{{{
>>> augmented_major_seventh("C") 
["C", "E", "G#", "B"]
}}}"""
	return augmented_triad(note) + [intervals.major_seventh(note)]

def augmented_minor_seventh(note):
	"""Builds an augmented minor seventh chord on note.
	Example:
{{{
>>> augmented_minor_seventh("C")
["C", "E", "G#", "Bb"]
}}}"""
	return augmented_triad(note) + [intervals.minor_seventh(note)]


#
#	Chords by harmonic function
#

def tonic(key):
	"""Returns the tonic chord in key.
	Example:
{{{
>>> tonic("C") 
["C", "E", "G"]
}}}"""
	return triads(key)[0]

def tonic7(key):
	"""Same as tonic(key), but returns seventh chord instead"""
	return sevenths(key)[0]

def supertonic(key):
	"""Returns the supertonic chord in key.
	Example:
{{{
>>> supertonic("C")
["D", "F", "A"]
}}}"""
	return triads(key)[1]

def supertonic7(key):
	"""Same as supertonic(key), but returns seventh chord"""
	return sevenths(key)[1]

def mediant(key):
	"""Returns the mediant chord in key.
	Example:
{{{
>>> mediant("C") 
["E", "G", "B"]
}}}"""
	return triads(key)[2]

def mediant7(key):
	"""Same as mediant(key), but returns seventh chord"""
	return sevenths(key)[2]

def subdominant(key):
	"""Returns the subdominant chord in key.
	Example:
{{{
>>> subdominant("C") 
["F", "A", "C"]
}}}"""
	return triads(key)[3]

def subdominant7(key):
	"""Same as subdominant(key), but returns seventh chord"""
	return sevenths(key)[3]


def dominant(key):
	"""Returns the dominant chord in key.
	Example:
{{{
>>> dominant("C") 
["G", "B", "D"]
}}}"""
	return triads(key)[4]

def dominant7(key):
	"""Same as dominant(key), but returns seventh chord"""
	return sevenths(key)[4]

def submediant(key):
	"""Returns the submediant chord in key.
	Example:
{{{
>>> submediant("C") 
["A", "C", "E"]
}}}"""
	return triads(key)[5]

def submediant7(key):
	"""Same as submediant(key), but returns seventh chord"""
	return sevenths(key)[5]


# Aliases

def I(key):
	return tonic(key)

def I7(key):
	return tonic7(key)

def ii(key):
	return supertonic(key)

def II(key):
	return supertonic(key)

def ii7(key):
	return supertonic7(key)

def II7(key):
	return supertonic7(key)

def iii(key):
	return mediant(key)

def III(key):
	return mediant(key)

def iii7(key):
	return mediant7(key)

def III7(key):
	return mediant7(key)

def IV(key):
	return subdominant(key)

def IV7(key):
	return subdominant7(key)

def V(key):
	return dominant(key)

def V7(key):
	return dominant7(key)

def vi(key):
	return submediant(key)

def VI(key):
	return submediant(key)

def vi7(key):
	return submediant7(key)

def VI7(key):
	return submediant7(key)

# Inversions

def invert(chord):
	"""Inverts a given chord one time"""
	return chord[1:] + [chord[0]]

def first_inversion(chord):
	"""The first inversion of a chord"""
	return invert(chord)

def second_inversion(chord):
	"""Returns the second inversion of chord"""
	return invert(invert(chord))

def third_inversion(chord):
	"""Returns the third inversion of chord"""
	return invert(invert(invert(chord)))

# Other

def determine(chord, shorthand = False):
	"""Names a chord."""
	if chord == []:
		return []
	elif len(chord) == 1:
		return chord
	elif len(chord) == 2:
		return [intervals.determine(chord[0], chord[1])]
	elif len(chord) == 3:
		return determine_triad(chord, shorthand)
	elif len(chord) == 4:
		return determine_seventh(chord, shorthand)
	else:
		return ["unknown chord"]

def determine_triad(triad, shorthand = False, tries = 1):
	"""Names the triad. Returns answers in a list. The third argument should \
not be given. If shorthand is True the answers will be in abbreviated form.

Can determine major, minor, diminished and suspended triads. \
Also knows about invertions.

Examples:
{{{
>>> determine_triad(["A", "C", "E"])
'A minor triad'
>>> determine_triad(["C", "E", "A"]) 
'A minor triad, first inversion'
>>> determine_triad(["A", "C", "E"], True)
'Amin'
}}}"""
	intval1 = intervals.determine(triad[0], triad[1])
	intval2 = intervals.determine(triad[0], triad[2])
	inttype1 = intval1.split(" ")[1]

	result = []

	if intval2 == "perfect fifth":
		if intval1 == "major third":
			if shorthand:
				result.append(triad[0] + "maj")
			else:
				result.append(triad[0] + " major triad" + int_desc(tries))
		elif intval1 == "minor third":
			if shorthand:
				result.append(triad[0] + "min")
			else:
				result.append(triad[0] + " minor triad" + int_desc(tries))
		elif inttype1 == "fourth":
			if shorthand:
				result.append(triad[0] + "sus4")
				result.append(triad[1] + "sus2")
			else:
				result.append(triad[0] + " suspended 4 triad"+ int_desc(tries))
				tries = 3 - (tries - 1)
				result.append(triad[1] + " suspended 2 triad" + int_desc(tries))
				tries = 3 - (tries - 1)
		elif inttype1 == "second":
			if shorthand:
				result.append(triad[0] + "sus2")
				result.append(triad[2] + "sus4")
			else:
				result.append(triad[0] + " suspended 2 triad" + int_desc(tries))
				tries = tries + 1
				result.append(triad[2] + " suspended 4 triad" + int_desc(tries))
	elif intval2 == "minor fifth":
		if intval1 == "minor third":
			if shorthand:
				result.append(triad[0] + "dim")
			else:
				result.append(triad[0] + " diminished triad" + int_desc(tries))
	elif intval2 == "augmented fifth":
		if intval1 == "major third":
			if shorthand:
				result.append(triad[0] + "aug")
			else:
				result.append(triad[0] + " augmented triad" + int_desc(tries))

	if result != []:
		return result

	if tries == 3:
		return result
	else:
		return determine_triad([triad[-1]] + triad[:-1], shorthand, tries + 1)

def determine_seventh(seventh, shorthand = False, tries = 1):
	"""Determines the type of seventh chord"""
	intval1 = intervals.determine(seventh[0], seventh[1])
	intval2 = intervals.determine(seventh[0], seventh[2])
	intval3 = intervals.determine(seventh[0], seventh[3])
	inttype1 = intval1.split(" ")[1]

	# [full, shorthand version]
	chord_names = [\
		[" minor seventh", "min7"],\
		[" major seventh", "maj7"],\
		[" dominant seventh", "7"],\
		[" half diminished seventh", "min7b5"],\
		[" diminished seventh", "dim7"],\
		[" minor/major seventh", "m/M7"],\
		[" augmented major seventh", "maj7+"],\
		[" augmented minor seventh", "min7+"],\
		[" minor sixth", "min6"],\
		[" sixth", "6"],\
				]

	result = []

	def add_result(note, name_index):
		if shorthand:
			result.append(seventh[note] + chord_names[name_index][shorthand])
		else:
			result.append(seventh[note] + chord_names[name_index][shorthand] +\
							int_desc(tries))

	if intval2 == "perfect fifth":

		if intval1 == "minor third":
			if intval3 == "minor seventh":
				add_result(0, 0)			# min7
			elif intval3 == "major seventh":
				add_result(0, 5)			# m/M7

		elif intval1 == "major third":
			if intval3 == "minor seventh":
				add_result(0, 2)			# 7
				if tries == 1: tries = 4
				else: tries -= 1
				add_result(1, 9)			# 6
			elif intval3 == "major seventh":
				add_result(0, 1)			# maj7

	elif intval2 == "minor fifth":

		if intval1 == "minor third":
			if intval3 == "minor seventh":
				add_result(0, 3)			# min7b5
				if tries == 1: tries = 4
				else: tries -= 1
				add_result(1, 8)			# min6
			elif intval3 == "diminished seventh":
				add_result(0, 4)			# dim7

	elif intval2 == "augmented fifth":

		if intval1 == "major third":
			if intval3 == "major seventh":
				add_result(0, 6)			# maj7+

			elif intval3 == "minor seventh":
				add_result(0, 7)			# min7+
				
	if result != []:
		return result

	if tries == 4:
		return result
	else:
		return determine_seventh([seventh[-1]] + seventh[:-1], shorthand, tries + 1)


def int_desc(tries):
	"""Helper function that returns the inversion of the triad in a string"""
	if tries == 1:
		return ""
	elif tries == 2:
		return ", first inversion"
	elif tries == 3:
		return ", second inversion"
	elif tries == 4:
		return ", third inversion"


def get_chord_by_string(chord_string):
	pass
