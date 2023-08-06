# -*- coding: utf-8 -*-
## Copyright (C)2007 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
""" Add on tests
"""
import unittest
import os
import shutil

from ingeniskel.addon import AddOn

curdir = os.path.dirname(__file__)

class AddOnTest(unittest.TestCase):

    def test_diff_1(self):
        #    
        # case 1 normal injection (no file)
        #
        adder = AddOn('xx')

        path = os.path.join(curdir, 'src')
        dirname = os.path.join(curdir, 'dest')
        filename = 'configure.zcml'
        waited = os.path.join(curdir, 'waited', filename)
        result = os.path.join(curdir, 'dest', filename)
        src = os.path.join(path, filename) 
        self.assert_(not os.path.exists(result))
        try:
            # first injection
            adder._check_file(filename, path, dirname)
            self.assert_(os.path.exists(result))
            
            # second injection 
            adder._check_file(filename, path, dirname)

            # checking the result
            result = os.path.join(curdir, 'dest', filename)
            self.assertEquals(open(result).read(), open(src).read())  
        finally:
            # removing dest
            os.remove(result)

    def test_diff_2(self):
        """testing file injection"""
        #    
        # case 2 diff injection (no exists)
        #
        adder = AddOn('xx')

        path = os.path.join(curdir, 'src')
        dirname = os.path.join(curdir, 'dest')
        filename = 'configure2.zcml'
        waited = os.path.join(curdir, 'waited', filename)
        result = os.path.join(curdir, 'dest', filename)

        # copying result before change
        shutil.copyfile(result, os.path.join(dirname, 'old'))

        try:
            # first injection, this should merge
            adder._check_file(filename, path, dirname)
            self.assert_(os.path.exists(result))
            
            # second injection, this should not merge anymore
            adder._check_file(filename, path, dirname)

            # checking the result
            result = os.path.join(curdir, 'dest', filename)
            waited = os.path.join(curdir, 'waited', filename)

            self.assertEquals(open(result).read(), open(waited).read())  
        
        # cleaning
        finally:
            os.remove(result)
            shutil.move(os.path.join(dirname, 'old'), result)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AddOnTest))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

