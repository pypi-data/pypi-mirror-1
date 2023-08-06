#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Unit test for _interfaces.py"""

# --------------------------------------------------------------------
# pyspread is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyspread is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------

import types

import gmpy
import numpy

import pyspread._interfaces as _interfaces
import vartypes as v

gmpy.rand('seed', 2)

class Test(object):
    """Test of free functions"""
    
    def test_sniff(self):
        """csv import sniffer"""
  
        dialect, header = _interfaces.sniff("test/BUG2037662.csv")
        assert not header
        assert dialect.delimiter == ','
        assert dialect.doublequote == 0
        assert dialect.quoting == 0
        assert dialect.quotechar == '"'
        assert dialect.lineterminator == "\r\n"
        assert dialect.skipinitialspace == 0
    
    def test_fill_numpyarray(self):
        """Fill the target with values from an array"""
        
        src_it = [(1, (1, 2), [1, 2], "1", 345, 1.0), \
                  ("67857", ['a'], 435, "1", 34534, 1.0)]

        digest_types = [types.IntType, types.ObjectType, types.StringType, \
                        types.IntType, types.ObjectType, types.FloatType]
        
        target = numpy.zeros((10, 7, 4), dtype="O")
        
        key = (0, 1, 0)
        
        _interfaces.fill_numpyarray(target, src_it, digest_types, key)
        
        expected_res = numpy.array( \
               [[1, (1, 2), '[1, 2]', 1, 345, 1.0],
               [67857, ['a'], '435', 1, 34534, 1.0]], dtype=object)
        
        for resele, expele in zip(target[:2, 1:, 0].flat, expected_res.flat):
            assert resele == repr(expele)
    
    def test_fill_wxgrid(self):
        """No idea how to create wx.grid on the fly for testing"""
        
        pass

class TestCsvInterfaces(object):
    """Unit test for CsvInterfaces"""
    
    def setup_method(self, method):
        """Creates a CsvImport class from a csv file"""
        csvfilenames = ["test/BUG2037662.csv", "test/not_there.csv"]
        
        self.csvfiles = []
        
        for filename in csvfilenames:
            try:
                dialect, header = _interfaces.sniff(filename)
            except IOError:
                assert filename == "test/not_there.csv"
            finally:
                csvfile = _interfaces.CsvInterfaces(filename, dialect, \
                    types.StringType, header)
                self.csvfiles.append(csvfile)
        
    def test_open_csv(self):
        """Test open all files with all different flags."""
        
        flags = []
        
        for csvfile in self.csvfiles:
            pass
    
    def test_close_csv(self):
        """Test for ."""
        
        pass
    
    def test_fill_target(self):
        """Test for ."""
        
        pass
    
    
class TestClipboard(object):
    """Unit test for Clipboard"""

    def setup_method(self, method):
        """???"""
        
        pass
        
    def test_convert_clipboard(self):
        """Test for ."""
        
        pass
    
    def test_get_clipboard(self):
        """Test for ."""
        
        pass
    
    def test_set_clipboard(self):
        """Test for ."""
        
        pass
    
    def test_grid_paste(self):
        """Test for ."""
        
        pass
    
    
class TestCommandline(object):
    """Unit test for Commandline"""
    
    def setup_method(self, method):
        """???"""
        
        pass
        
    def test_init(self):
        """Test for ."""
        
        pass
    
    def test_parse(self):
        """Test for ."""
        
        pass
