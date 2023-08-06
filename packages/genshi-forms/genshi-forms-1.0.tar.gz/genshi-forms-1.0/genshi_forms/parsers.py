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

import re
import datetime
from time import strptime

__all__ = ['date', 'time']

DATE_PARSERS = (
	(re.compile ('^(\d{4})-(\d{1,2})-(\d{1,2})$'),
	 lambda y, m, d: (y, m, d)),
	(re.compile ('^(\d{1,2})/(\d{1,2})/(\d{4})$'),
	 lambda m, d, y: (y, m, d)),
	(re.compile ('^(\d{1,2})/(\d{1,2})/(\d{2})$'),
	 lambda m, d, y: ('20' + y, m, d)),
)

TIME_FORMATS = ('%I:%M:%S %p', '%H:%M:%S', '%I:%M %p', '%H:%M')

def date (string):
	"""Parse dates in various formats into a :class:`datetime.date` object.
	If the string doesn't match a known format, or is an invalid date,
	a :exc:`ValueError` will be raised.
	
	"""
	def _to_date (mapper, match):
		return datetime.date (*map (int, mapper (*match.groups ())))
		
	for regex, mapper in DATE_PARSERS:
		match = regex.match (string)
		if match:
			try:
				value = _to_date (mapper, match)
			except ValueError:
				pass
			else:
				return value
				
	# Unparsable date
	raise ValueError ("Can't parse date %r." % (string,))
	
def time (string):
	"""Parse times in various formats into a :class:`datetime.time` object.
	If the string doesn't match a known format, or is an invalid time,
	a :exc:`ValueError` will be raised.
	
	"""
	for format in TIME_FORMATS:
		try:
			value = datetime.time (*strptime (string, format)[3:6])
		except ValueError:
			pass
		else:
			return value
			
	# Unparsable time
	raise ValueError ("Can't parse time %r." % (string,))
	
