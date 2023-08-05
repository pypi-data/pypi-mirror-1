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
# $Id: catalog.py 116 2007-07-17 03:46:07Z mccosar $

"""
catalog.py -- version 2.0 -- Bruce H. McCosar
"""

__metaclass__ = type

__all__ = ['SetCatalog']

import pickle

from pcset import *
from pcops import *

PICKLE_FILE = 'catalog.pkl'

def all_possible_pcsets():
    for n in xrange(4096):
        result = []
        for bit in range(12):
            if n & (2**bit):
                result.append(bit)
        yield PcSet(result)

def any_match(p,page):
    for entry in page:
        if exact_equality(p,entry):
            return True
    return False


class SetCatalog:

    """
    Class docs.
    """

    def rewrite(self):
        storage = open(PICKLE_FILE,'wb')
        pickle.dump(self.catalog,storage,-1)
        storage.close()

    def rebuild(self):
        # self.catalog[n] = a 'page' listing primes with cardinality n
        self.catalog = [ [] for page in range(13) ]
        # Warning: if the above is defined with the shortcut
        #     self.catalog = [[]] * 13
        # this ends up as a list of references to the same empty set!
        for s in all_possible_pcsets():
            p = s.prime()
            page = self.catalog[len(p)]
            if not any_match(p,page):
                page.append(p)
        if self.store:
            try:
                self.rewrite()
            except IOError:
                if not self.failsafe:
                    raise

    def retrieve(self):
        storage = open(PICKLE_FILE,'rb')
        self.catalog = pickle.load(storage)
        storage.close()

    def __init__(self,rebuild=False,store=True,failsafe=False):
        self.store = store
        self.failsafe = failsafe
        if rebuild:
            self.rebuild()
        else:
            try:
                self.retrieve()
            except IOError:
                self.rebuild()
    
    def page(self,n):
        return self.catalog[n]

    def __iter__(self):
        for n in range(13):
            for entry in self.catalog[n]:
                yield entry

    def __len__(self):
        result = 0
        for n in range(13):
            result += len(self.catalog[n])
        return result


def showcatalog():
    r = SetCatalog(rebuild=True,store=False)
    print "Pitch Class Set Catalog: %d prime sets total\n" % len(r)
    for n in range(13):
        size = len(r.page(n))
        if size > 1:
            w = 'sets'
        else:
            w = 'set'
        print "Cardinality %d: %d prime %s" % (n,size,w)
        position = 0
        for entry in r.page(n):
            if position == 0:
                print "    ",
                position = 4
            if len(entry) == 0:
                print '[]',
            else:
                print entry,
            position += len(entry) + 1
            if position > 60:
                print
                position = 0
        print
        if position > 0:
            print

if __name__ == '__main__':
    showcatalog()
