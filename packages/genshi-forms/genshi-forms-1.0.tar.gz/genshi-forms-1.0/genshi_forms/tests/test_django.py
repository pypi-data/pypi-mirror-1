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

from .. import django, errors, widgets
from . import common

class RecordingWidget (object):
	def __init__ (self):
		self.render_calls = []
		
	def render (self, *args):
		self.render_calls.append (args)
		return len (self.render_calls)
		
class FakeModel (object):
	def __init__ (self, pk, string):
		self.pk = pk
		self.__string = string
		
	def __unicode__ (self):
		return unicode (self.__string)
		
	class DoesNotExist (Exception):
		pass
		
class FakeQuerySet (list):
	def __init__ (self, model, **kwargs):
		super (FakeQuerySet, self).__init__ (**kwargs)
		self.model = model
		
	def filter (self):
		return self
		
	def get (self, **kwargs):
		pk = unicode (kwargs.pop ('pk'))
		filtered = [v for v in self if unicode (v.pk) == pk]
		if len (filtered) < 1:
			raise self.model.DoesNotExist
		assert len (filtered) == 1
		return filtered[0]
		
def build_qs (*values):
	qs = FakeQuerySet (FakeModel)
	for pk, string in values:
		qs.append (FakeModel (pk, string))
	return qs
	
class TestModelField (common.TestCase):
	qs = build_qs ((1, 'a'), (2, 'b'))
	
	def test_init_defaults (self):
		qs = build_qs ()
		field = django.ModelField (qs)
		self.assert_ (field.queryset is qs)
		self.assert_ (isinstance (field.widget, widgets.Select))
		self.assertEqual (field.choices, [('', "---------")])
		
	def test_clean_empty (self):
		field = django.ModelField (self.qs, required = False)
		cleaned = field.clean ('name', {'name': ['']}, {})
		self.assert_ (cleaned is None)
		
	def test_clean_empty_required (self):
		field = django.ModelField (self.qs)
		with self.check_exception (errors.ValidationError,
		                           "This field is required."):
			field.clean ('name', {'name': ['']}, {})
			
	def test_clean (self):
		field = django.ModelField (self.qs, required = False)
		cleaned = field.clean ('name', {'name': ['1']}, {})
		self.assertEqual (cleaned.pk, 1)
		
	def test_clean_multiple (self):
		field = django.ModelField (self.qs, required = False)
		cleaned = field.clean ('name', {'name': ['2', '1']}, {})
		self.assertEqual (cleaned.pk, 2)
		
	def test_invalid (self):
		field = django.ModelField (self.qs)
		with self.check_exception (errors.ValidationError,
		                           "No such choice."):
			field.clean ('name', {'name': ['3']}, {})
			
	def test_render (self):
		widget = RecordingWidget ()
		field = django.ModelField (self.qs, widget = widget)
		field.render ('name', self.qs[0], {})
		self.assertEqual (widget.render_calls, [
			('name', [1], {}),
		])
		
class TestMultipleModelField (common.TestCase):
	qs = build_qs ((1, 'a'), (2, 'b'))
	
	def test_init_defaults (self):
		qs = build_qs ()
		field = django.MultipleModelField (qs)
		self.assert_ (field.queryset is qs)
		self.assert_ (isinstance (field.widget, widgets.Select))
		self.assertEqual (field.choices, [])
		
	def test_clean_empty (self):
		field = django.MultipleModelField (self.qs, required = False)
		cleaned = field.clean ('name', {'name': ['']}, {})
		self.assertEqual (cleaned, [])
		
	def test_clean_empty_required (self):
		field = django.MultipleModelField (self.qs)
		with self.check_exception (errors.ValidationError,
		                           "This field is required."):
			field.clean ('name', {'name': ['']}, {})
			
	def test_clean (self):
		field = django.MultipleModelField (self.qs, required = False)
		cleaned = field.clean ('name', {'name': ['1']}, {})
		self.assertEqual (cleaned, [self.qs[0]])
		
	def test_clean_multiple (self):
		field = django.MultipleModelField (self.qs, required = False)
		cleaned = field.clean ('name', {'name': ['2', '1']}, {})
		self.assertEqual (cleaned, [self.qs[1], self.qs[0]])
		
	def test_invalid (self):
		field = django.MultipleModelField (self.qs)
		with self.check_exception (errors.ValidationError,
		                           "No such choice."):
			field.clean ('name', {'name': ['3']}, {})
			
	def test_render (self):
		widget = RecordingWidget ()
		field = django.MultipleModelField (self.qs, widget = widget)
		field.render ('name', self.qs, {})
		self.assertEqual (widget.render_calls, [
			('name', [1, 2], {'multiple': 'multiple'}),
		])
		
	def test_render_obj_with_all (self):
		widget = RecordingWidget ()
		field = django.MultipleModelField (self.qs, widget = widget)
		class FakeManager (object):
			def all (_self):
				return self.qs
		field.render ('name', FakeManager (), {})
		self.assertEqual (widget.render_calls, [
			('name', [1, 2], {'multiple': 'multiple'}),
		])
		
	def test_render_none (self):
		widget = RecordingWidget ()
		field = django.MultipleModelField (self.qs, widget = widget)
		field.render ('name', None, {})
		self.assertEqual (widget.render_calls, [
			('name', [], {'multiple': 'multiple'}),
		])
		
