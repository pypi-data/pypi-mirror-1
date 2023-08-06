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

from contextlib import contextmanager
import unittest
from genshi.core import START, Attrs, Stream

class TestCase (unittest.TestCase):
	@contextmanager
	def check_exception (self, exc_type, message):
		try:
			yield
			self.fail ("No exception raised.")
		except exc_type, exc:
			self.assertEqual (unicode(exc), message)
			
def sort_attr_filter (stream):
	for kind, data, pos in stream:
		if kind is START:
			tag, attributes = data
			yield (kind, (tag, Attrs (sorted (attributes))), pos)
		else:
			yield (kind, data, pos)
			
def sorted_stream (stream_or_tag):
	return unicode (Stream (stream_or_tag).filter (sort_attr_filter))
	
