#!/usr/bin/env python

# pcsets 2.0.0b2 -- Pitch Class Sets for Python.
#
# Copyright 2007 Bruce H. McCosar
#
# This file is part of the package 'pcsets'
#
# The package 'pcsets' is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3 of
# the License, or (at your option) any later version.
#
# The package 'pcsets' is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# $Id: setup.py 138 2007-07-20 00:32:56Z mccosar $

"""
setup.py

If you run this script, it should install the pcsets library
to your Python distribution's site libraries.
"""

__metaclass__ = type

from distutils.core import setup


DESCRIPTION = 'Pitch Class Sets for Python.'


# Edited version of README
LONG_DESCRIPTION ="""
Pitch Class Sets are a mathematical model for analyzing and composing
music. Each note 'C' through 'B' has an equivalent pitch class number
0 through 11. Sets of these numbers may be operated on by mathematical
functions such as transpose and invert.

The goal of this project is to, eventually, have:

  * A Python library capable of fully implementing Pitch Class Sets
    and their common operations, as well as several convenience
    functions to bring these abstract concepts to the real world.
    (Mapping pitch classes to note names, for instance).

  * A tool for composition.  Some applications are harmonization,
    chord voicing generation, and melodic motif creation.

  * More exotic goals -- creation of new chordal elements, musical
    progressions, and harmonic relationships.

As you can see, these goals range from easy (already implemented) to
insanely difficult!


                                 Why
                                 ===

I became interested in pitch class sets as an offshoot of my earlier
work in jazz. At the end of this file is a list of text and Web
references that might provide an introduction to the theory.

I decided to write a Python module after finding most of the programs
available online were GUI-only / interactive only (or worse . . .
applets). For various reasons, I needed to be able to set up long
computational chains on a group of pitch class sets. Typing them into
a web browser one at a time and poking buttons was not an option!


                          About this Package
                          ==================

This is a beta release. The API will not change for any of the
included modules. Bugs will be fixed and new modules will be added,
but these four make up the core:


    pcsets.pcset

        The base class. Includes methods that operate on single sets,
        such as inversion and transposition.

    pcsets.pcops

        Operations on two or more sets, such as subset_of(a,b).

    pcsets.catalog

        Generates the entire catalog of 224 prime sets as a Python
        object. Since this takes a while to generate, it saves the
        catalog in a pickle file (catalog.pkl) for future use.

    pcsets.noteops

        The 'universal translator' from PcSets to named notes and
        vice versa.


Barring a flood of bug reports, this is likely the last beta version
before the actual 2.0.0 release. New modules are being worked on
(operations on the familiar chords and scales -- sort of a noteops for
the common language of chord-scale theory). However, these new modules
will be experimental until the 2.1 release.

--BMC


                              References
                              ==========

Web

 * I posted a lot of the earlier Pitch Class Set code to my blog (bad
   idea ... it mangled the \n type characters). Nevertheless, there's
   some good discussion and examples.  Check under the tags 'music
   theory' or 'python'.

                    http://bmccosar.wordpress.com/


 * If you want a short introduction or tutorial, Jay Tomlin's site is
   the best. Sort of the 'Classics Illustrated' of Pc theory.

          http://www.jaytomlin.com/music/settheory/help.html


 * If you want a LOT of information without chasing down a book,
   well... here's the next best thing. The author does get upset about
   the old '037' vs '047' issue. You'll see.

                http://solomonsmusic.net/setheory.htm


Text

  * The classic of the field, "The Structure of Atonal Music", by
    Allen Forte (1973).

  * A relatively new (but extremely thourough and readable) work,
    "Introduction to Post-Tonal Theory", by Joseph Straus (3rd ed.,
    2005).
"""


CLASSIFIERS = """
Development Status :: 4 - Beta
Intended Audience :: Education
License :: OSI Approved :: GNU General Public License (GPL)
Programming Language :: Python
Topic :: Software Development :: Libraries :: Python Modules
""".strip().split('\n')


parameters = {
    'name' : 'pcsets',
    'version' : '2.0.0b2',
    'author' : 'Bruce H. McCosar',
    'author_email' : 'bmccosar@gmail.com',
    'description' : DESCRIPTION,
    'long_description' : LONG_DESCRIPTION,
    'url' : 'http://code.google.com/p/pcsets/',
    'download_url' :
        'http://pcsets.googlecode.com/files/pcsets-2.0.0b2.tar.gz',
    'classifiers' : CLASSIFIERS,
    'packages' : ['pcsets']
    }

if __name__ == '__main__':
    setup(**parameters)
