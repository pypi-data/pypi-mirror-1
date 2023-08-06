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
from mt_exceptions import NoteFormatError


#===================================================================
#							Triads
#===================================================================


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




#===================================================================
#	Sevenths
#===================================================================


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




def diminished_seventh(note):
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




#===================================================================
#	Sixths
#===================================================================


# absolute



def minor_sixth(note):
	"""Builds a minor sixth chord on note.
	Example:
{{{
>>> minor_sixth("C")
['C', 'Eb', 'G', 'A']
}}}"""
	return minor_triad(note) + [intervals.major_sixth(note)]




def major_sixth(note):
	"""Builds a major sixth chord on note.
	Example:
{{{
>>> major_sixth("C")
['C', 'E', 'G', 'A']
}}}"""
	return major_triad(note) + [intervals.major_sixth(note)]




def dominant_sixth(note):
	"""Builds the altered chord 6/7 on note.
	Example:
{{{
>>> dominant_sixth("C")
['C', 'E', 'G', 'A', 'Bb']
}}}"""
	return major_sixth(note) + [intervals.minor_seventh(note)]



def sixth_ninth(note):
	"""Builds the sixth/ninth chord on note.
	Example:
{{{
>>> sixth_ninth('C')
['C', 'E', 'G', 'A', 'D']
}}}"""
	return major_sixth(note) + [intervals.major_second(note)]




#===================================================================
#	Ninths
#===================================================================



# absolute


def minor_ninth(note):
	"""Builds a minor ninth chord on note.
	Example:
{{{
>>> minor_ninth("C")
['C', 'Eb', 'G', 'Bb', 'D']
}}}"""
	return minor_seventh(note) + [intervals.major_second(note)]



def major_ninth(note):
	"""Builds a major ninth chord on note.
	Example:
{{{
>>> major_ninth("C")
['C', 'E', 'G', 'B', 'D']
}}}"""
	return major_seventh(note) + [intervals.major_second(note)]



def dominant_ninth(note):
	"""Builds a dominant ninth chord on note.
	Example:
{{{
>>> dominant_ninth("C")
['C', 'E', 'G', 'Bb', 'D']
}}}"""
	return dominant_seventh(note) + [intervals.major_second(note)]



def dominant_flat_ninth(note):
	"""Builds a dominant flat ninth chord on note.
	Example:
{{{
>>> dominant_ninth("C")
['C', 'E', 'G', 'Bb', 'Db']
}}}"""
	res = dominant_ninth(note)
	res[4] = intervals.minor_second(note)
	return res



def dominant_sharp_ninth(note):
	"""Builds a dominant sharp ninth chord on note.
	Example:
{{{
>>> dominant_ninth("C")
['C', 'E', 'G', 'Bb', 'D#']
}}}"""
	res = dominant_ninth(note)
	res[4] = notes.augment(intervals.major_second(note))
	return res



#===================================================================
#	Elevenths
#===================================================================

# diatonic


# absolute


def eleventh(note):
	"""Builds an eleventh chord on note.
	Example:
{{{
>>> eleventh("C")
['C', 'G', 'Bb', 'F']
}}}"""
	return [note, intervals.perfect_fifth(note), \
		intervals.minor_seventh(note), intervals.perfect_fourth(note)]


def minor_eleventh(note):
	"""Builds a minor eleventh chord on note.
	Example:
{{{
>>> minor_eleventh("C")
['C', 'Eb', 'G', 'Bb', 'F']
}}}"""
	return minor_seventh(note) + [intervals.perfect_fourth(note)]



#===================================================================
#	Thirteenths
#===================================================================

# absolute
def minor_thirteenth(note):
	"""Builds a minor thirteenth chord on note.
	Example:
{{{
>>> minor_thirteenth('C')
['C', 'Eb', 'G', 'Bb', 'D', 'A']
}}}"""
	return minor_ninth(note) + [intervals.major_sixth(note)]



def major_thirteenth(note):
	"""Builds a major thirteenth chord on note.
	Example:
{{{
>>> major_thirteenth('C')
['C', 'E', 'G', 'B', 'D', 'A']
}}}"""
	return major_ninth(note) + [intervals.major_sixth(note)]



def dominant_thirteenth(note):
	"""Builds a dominant thirteenth chord on note.
	Example:
{{{
>>> dominant_thirteenth('C')
['C', 'E', 'G', 'Bb', 'D', 'A']
}}}"""
	return dominant_ninth(note) + [intervals.major_sixth(note)]




#===================================================================
#	Suspended Chords
#===================================================================


# absolute


def suspended_triad(note):
	"""An alias for suspended_fourth_triad"""
	return suspended_fourth_triad(note)



def suspended_second_triad(note):
	"""Builds a suspended second triad on note.
	Example:
{{{
>>> suspended_second_triad("C")
["C", "D", "G"]
}}}"""
	return [note, intervals.major_second(note), intervals.perfect_fifth(note)]



def suspended_fourth_triad(note):
	"""Builds a suspended fourth triad on note.
	Example:
{{{
>>> suspended_fourth_triad("C")
["C", "F", "G"]
}}}"""
	return [note, intervals.perfect_fourth(note), intervals.perfect_fifth(note)]



def suspended_seventh(note):
	"""Builds a suspended (flat) seventh chord on note.
	Example:
{{{
>>> suspended_seventh("C")
["C", "F", "G", "Bb"]

}}}"""
	return suspended_fourth_triad(note) + [intervals.minor_seventh(note)]



def suspended_fourth_ninth(note):
	"""Builds a suspended fourth flat ninth chord on note.
	Example:
{{{
>>> suspended_ninth("C")
['C', 'F', 'G', 'Db']
}}}"""
	return suspended_fourth_triad(note) + [intervals.minor_second(note)]




#===================================================================
#	Augmented Chords
#===================================================================




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




#===================================================================
#	Various
#	Altered and Special chords
#===================================================================


def dominant_flat_five(note):
	"""Builds a dominant flat five chord on note.
	Example:
{{{
>>> dominant_flat_five("C")
['C', 'E', 'Gb', 'Bb']
}}}"""
	res = dominant_seventh(note)
	res[2] = notes.diminish(res[2])
	return res



def lydian_dominant_seventh(note):
	"""Builds the lydian dominant seventh (7#11) on note
	Example:
{{{
>>> lydian_dominant_seventh('C')
['C', 'E', 'G', 'Bb', 'F#']

}}}"""
	return dominant_seventh(note) + [notes.augment(intervals.perfect_fourth(note))]


def hendrix_chord(note):
	"""Builds the famous Hendrix chord (7b12)
	Example:
{{{
>>> hendrix_chord('C')
['C', 'E', 'G', 'Bb', 'Eb']
}}}"""
	return dominant_seventh(note) + [intervals.minor_third(note)]




#===================================================================
#	Chords by harmonic function
#===================================================================



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


#===================================================================
#	 Aliases
#===================================================================


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



#===================================================================
# 	Inversions
#===================================================================


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


#===================================================================
# 	Other
#===================================================================


def from_shorthand(shorthand_string, slash = None):
	"""Takes a chord written in shorthand and returns the notes in the \
chord. The function can recognize triads, sevenths, sixths, ninths, elevenths, \
thirteenths, slashed chords and a number of altered chords. \
The second argument should not be given and is only used for a recursive call \
when a slashed chord is found.
	Example:
{{{
>>> from_shorthand("Amin")
["A", "C", "E"]
>>> from_shorthand("Am/M7")
["F", "Ab", "C", "E"]
>>> from_shorthand("A")
["A", "C#", "E"]
>>> from_shorthand("G/A")
["G", "A", "C#", "E"]

}}}
	Recognised abbreviations: the letters `m` and `M` in the following abbreviations  \
can always be substituted by respectively `min`, `mi` or `-` and `maj` or `ma` (eg. \
`from_shorthand("Amin7") == from_shorthand("Am7")`, etc.).
	* Triads: *'m'*, *'M'* or *''*, *'dim'*. 
	* Sevenths: *'m7'*, *'M7'*, *'7'*, *'m7b5'*, *'dim7'*, *'m/M7'* or *'mM7'*
	* Augmented chords: *'aug'* or *'+'*, *'7#5'* or *'M7+5'*, *'M7+'*, *'m7+'*, *'7+'*
	* Suspended chords: *'sus4'*, *'sus2'*, *'sus47'*, *'sus'*, *'11'*, *'sus4b9'* or *'susb9'*
	* Sixths: *'6'*, *'m6'*, *'M6'*, *'6/7'* or *'67'*, *6/9* or *69*
	* Ninths: *'9'*, *'M9'*, *'m9'*, *'7b9'*, *'7#9'*
	* Elevenths: *'11'*, *'7#11'*, *'m11'*
	* Thirteenths: *'13'*, *'M13'*, *'m13'*
	* Altered chords: *'7b5'*, *'7b9'*, *'7#9'*, *'67'* or *'6/7'*
	* Special: *'5'*, *'NC'*, *'hendrix'*
	"""
	shorthand = {
			# Triads
			"m" : minor_triad,
			"M" : major_triad, 
			"" : major_triad,
			"dim" : diminished_triad,

			# Augmented chords
			"aug" : augmented_triad,
			"+" : augmented_triad,
			"7#5" : augmented_minor_seventh,
			"M7+5" : augmented_minor_seventh,
			"M7+" : augmented_major_seventh,
			"m7+" : augmented_minor_seventh,
			"7+" : augmented_major_seventh,

			# Suspended chords
			"sus47" : suspended_seventh,
			"sus4" : suspended_fourth_triad,
			"sus2" : suspended_second_triad,
			"sus" : suspended_triad,
			"11" : eleventh,
			"sus" : eleventh,
			"sus4b9" : suspended_fourth_ninth,
			"susb9" : suspended_fourth_ninth,

			# Sevenths
			"m7" : minor_seventh,
			"M7" : major_seventh,
			"7" : dominant_seventh,
			"m7b5" : minor_seventh_flat_five,
			"dim7" : diminished_seventh,
			"m/M7" : minor_major_seventh,
			"mM7" : minor_major_seventh,
			
			
			# Sixths
			"m6" : minor_sixth,
			"M6" : major_sixth,
			"6" : major_sixth, 
			"6/7" : dominant_sixth,
			"67": dominant_sixth,
			"6/9" : sixth_ninth,
			"69" : sixth_ninth,

			# Ninths
			"9" : dominant_ninth,
			"7b9" : dominant_flat_ninth,
			"7#9" : dominant_sharp_ninth,
			"M9" : major_ninth,
			"m9" : minor_ninth,

			# Elevenths
			"7#11" : lydian_dominant_seventh,
			"m11" : minor_eleventh,

			# Thirteenths
			"M13" : major_thirteenth,
			"m13" : minor_thirteenth,

			"13" : dominant_thirteenth,

			# Altered Chords
			"7b5" : dominant_flat_five,
			
			# Special
			"hendrix" : hendrix_chord,
			"7b12" : hendrix_chord,
			"5" : (lambda x: [x, intervals.perfect_fifth(x)])
			}

	if shorthand_string in ["NC", "N.C."]:
		return []

	# Get the note name
	if not notes.is_valid_note(shorthand_string[0]):
		raise NoteFormatError, "Unrecognised note '%s' in chord '%s'" % \
				(shorthand_string[0], shorthand_string)

	name = shorthand_string[0]

	# Look for accidentals and slashes
	for n in shorthand_string[1:]:
		if n == '#':
			name += n
		elif n == 'b':
			name += n
		elif n == '/':
			# Slash chord found
			if slash == None:
				return from_shorthand(shorthand_string[len(name) + 1:], name)
			else:
				#warning raise exception: too many slashes
				return False
		else:
			break

	shorthand_start = len(name)

	# Expand/shrink shorthand_string
	shorthand_string = shorthand_string.replace('min', 'm')
	shorthand_string = shorthand_string.replace('mi', 'm')
	shorthand_string = shorthand_string.replace('-', 'm')

	shorthand_string = shorthand_string.replace('maj', 'M')
	shorthand_string = shorthand_string.replace('ma', 'M')

	# Return chord
	short_chord = shorthand_string[shorthand_start:]
	if shorthand.has_key(short_chord):
		# Take care of slashes
		res = shorthand[short_chord](name)
		if slash != None:
			if notes.is_valid_note(slash):
				res = [slash] + res
			else:
				raise NoteFormatError, "Unrecognised note '%s' in slash chord'%s'" % (slash, slash + shorthand_string)
		return res
		
	else:
		#warning raise exception: shorthand not known
		return False




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
