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

class MockRecorder (object):
	def __init__ (self, attrs):
		self.__attrs = attrs
		
	def __getattr__ (self, name):
		try:
			return self.__attrs[name]
		except KeyError:
			print self.__attrs
			raise AttributeError (name)
			
class PlaybackProxyMethod (object):
	def __init__ (self, name, calls):
		self.__name = name
		self.__calls = calls
		
	def __call__ (self, *args, **kwargs):
		try:
			call = self.__calls.pop (0)
		except IndexError:
			raise AssertionError ("Didn't record enough method calls.")
			
		this_call = (self.__name, args, kwargs)
		if call != this_call:
			raise AssertionError ("Call match failed: %r != %r" % (call, this_call))
			
class PlaybackProxy (object):
	def __init__ (self, calls):
		self.__calls = calls
		
	def __getattr__ (self, name):
		return PlaybackProxyMethod (name, self.__calls)
		
class MockPlayback (object):
	def __init__ (self, calls):
		self.__calls = calls
		
	def __enter__ (self):
		return PlaybackProxy (self.__calls)
		
	def __exit__ (self, exc_type, exc_value, exc_tb):
		if exc_type:
			return
		if self.__calls:
			raise AssertionError ("Recorded too many method calls.")
			
class MockMethod (object):
	def __init__ (self, calls, name, value):
		self.__name = name
		self.__value = value
		self.__calls = calls
		
	def __call__ (self, *args, **kwargs):
		self.__calls.append ((self.__name, args, kwargs))
		return self.__value
		
class MockController (object):
	def __init__ (self):
		self.__attrs = {}
		self.__method_calls = []
		self.recorder = MockRecorder (self.__attrs)
		
	def attrs (self, **kwargs):
		self.__attrs.update (kwargs)
		
	def methods (self, **kwargs):
		for key, value in kwargs.items ():
			self.__attrs[key] = MockMethod (self.__method_calls, key, value)
			
	def playback (self):
		return MockPlayback (list (self.__method_calls))
		
class StubbedMethod (object):
	def __init__ (self, value):
		self.calls = []
		self.value = value
		
	def __call__ (self, *args, **kwargs):
		self.calls.append ((args, kwargs))
		return self.value
		
