# Copyright (C) 2009 John Millikin <jmillikin@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from datetime import date, time

from .. import parsers
from . import common

class TestDate (common.TestCase):
	def check_date (self, text, expected):
		self.assertEqual (parsers.date (text), expected)
		
	def test_ymd (self):
		self.check_date ("2000-01-02", date (2000, 1, 2))
		
	def test_mdy (self):
		self.check_date ("02/01/2000", date (2000, 2, 1))
		
	def test_mdy_short (self):
		self.check_date ("02/01/00", date (2000, 2, 1))
		
	def test_no_format (self):
		with self.check_exception (ValueError,
		                           "Can't parse date 'bad date'."):
			parsers.date ("bad date")
			
	def test_invalid (self):
		with self.check_exception (ValueError,
		                           "Can't parse date '2000-20-20'."):
			parsers.date ("2000-20-20")
			
class TestTime (common.TestCase):
	def check_time (self, text, expected):
		self.assertEqual (parsers.time (text), expected)
		
	def test_hms_12 (self):
		self.check_time ("5:13:14 PM", time (17, 13, 14))
		
	def test_hms_24 (self):
		self.check_time ("17:13:14", time (17, 13, 14))
		
	def test_hm_12 (self):
		self.check_time ("5:13 PM", time (17, 13))
		
	def test_hm_24 (self):
		self.check_time ("17:13", time (17, 13))
		
	def test_no_format (self):
		with self.check_exception (ValueError,
		                           "Can't parse time 'bad time'."):
			parsers.time ("bad time")
			
	def test_invalid (self):
		with self.check_exception (ValueError,
		                           "Can't parse time '12:70 PM'."):
			parsers.time ("12:70 PM")
			
