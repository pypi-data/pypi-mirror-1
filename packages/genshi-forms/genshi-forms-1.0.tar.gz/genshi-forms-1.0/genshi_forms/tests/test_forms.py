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

from unittest import TestCase
from functools import partial

from .. import form, fields, ValidationError
from . import common, mocking

def record_render (form):
	"""Used to test that fields are rendered in the correct order."""
	render_calls = []
	def record_render (field_name, layout = 'table'):
		render_calls.append ((field_name, layout))
		return ()
		
	for key, value in form.fields.items ():
		value.render = partial (record_render, key)
	list (form.render ('table'))
	return render_calls
	
def FieldMock (default = None, needs_multipart = False, required = False):
	field = mocking.MockController ()
	field.attrs (default = default,
	             needs_multipart = needs_multipart,
	             required = required)
	return field
	
class EmptyForm (form.Form):
	pass
	
class BasicForm (form.Form):
	a = fields.TextField ()
	
class TwoFieldForm (form.Form):
	b = fields.TextField ()
	a = fields.TextField ()
	
class FormWithFile (form.Form):
	a = fields.FileField ()
	
class FormWithDefault (form.Form):
	a = fields.TextField (default = 'def')
	
class FirstBaseForm (form.Form):
	c = fields.TextField ()
	
class SecondBaseForm (form.Form):
	b = fields.TextField ()
	
class DerivedForm (FirstBaseForm, SecondBaseForm):
	a = fields.TextField ()
	
class CustomValidation (form.Form):
	a = fields.TextField ()
	def clean_a (self, value):
		if value == 'test1':
			return "Cleaned test1"
		raise ValidationError ("Error " + value)
		
class CustomGlobalValidation (form.Form):
	a = fields.TextField ()
	def clean (self, post, files):
		cleaned_data, errors = super (CustomGlobalValidation, self).clean (post, files)
		if cleaned_data['a'] == 'test1':
			return {'a': "Cleaned test1"}, {}
		return None, {'a': ["Global error"]}
		
class TestFormAttributes (TestCase):
	def test_attributes (self):
		self.assert_ (isinstance (BasicForm.a, fields.TextField))
		
	def test_field_list (self):
		self.assertEqual (list (BasicForm.fields),
		                  [('a', BasicForm.a)])
		
	def test_unbound_default (self):
		form = BasicForm.unbound ({'a': 'test'})
		self.assertEqual (form.fields['a'].default, 'test')
		
	def test_unbound_default_2 (self):
		form = FormWithDefault.unbound ()
		self.assertEqual (form.fields['a'].default, 'def')
		
	def test_default (self):
		self.assertEqual (FormWithDefault.a.default, 'def')
		
class BoundFormTests (TestCase):
	def test_build_empty (self):
		bound = EmptyForm.bound ({}, {})
		self.assertEqual (bound.is_valid, True)
		self.assertEqual (bound.is_bound, True)
		self.assertEqual (bound.errors, {})
		self.assertEqual (bound.cleaned_data, {})
		self.assertEqual (bound.fields, {})
		
	def test_valid (self):
		form = BasicForm.bound ({'a': ['test']}, {})
		self.assertEqual (form.is_valid, True)
		self.assertEqual (form.is_bound, True)
		self.assertEqual (form.errors, {})
		self.assertEqual (form.cleaned_data, {'a': 'test'})
		
	def test_invalid (self):
		form = BasicForm.bound ({}, {})
		self.assertEqual (form.is_valid, False)
		self.assertEqual (form.is_bound, True)
		self.assertEqual (form.errors, {'a': ["This field is required."]})
		self.assert_ (not hasattr (form, 'cleaned_data'))
		
	def test_render_empty (self):
		form = EmptyForm.bound ({}, {})
		self.assertEqual (record_render (form), [])
		
	def test_render (self):
		form = BasicForm.bound ({}, {})
		self.assertEqual (record_render (form),
		[
			('a', 'table'),
		])
		
	def test_render_in_order (self):
		form = TwoFieldForm.bound ({}, {})
		self.assertEqual (record_render (form),
		[
			('b', 'table'),
			('a', 'table'),
		])
		
	def test_render_inherited (self):
		form = DerivedForm.bound ({}, {})
		self.assertEqual (record_render (form),
		[
			('c', 'table'),
			('b', 'table'),
			('a', 'table'),
		])
		
class UnboundFormTests (TestCase):
	def test_build_empty (self):
		unbound = EmptyForm.unbound ()
		self.assertEqual (unbound.is_valid, False)
		self.assertEqual (unbound.is_bound, False)
		self.assertEqual (unbound.errors, {})
		self.assert_ (not hasattr (unbound, 'cleaned_data'))
		self.assertEqual (unbound.fields, {})
		
	def test_with_fields (self):
		form = BasicForm.unbound ()
		self.assertEqual (form.is_valid, False)
		self.assertEqual (form.is_bound, False)
		self.assertEqual (form.errors, {})
		self.assertEqual (form.fields['a'].default, None)
		self.assert_ (not hasattr (form, 'cleaned_data'))
		
	def test_render_empty (self):
		form = EmptyForm.unbound ()
		self.assertEqual (record_render (form), [])
		
	def test_render (self):
		form = BasicForm.unbound ()
		self.assertEqual (record_render (form),
		[
			('a', 'table'),
		])
		
	def test_render_in_order (self):
		form = TwoFieldForm.unbound ()
		self.assertEqual (record_render (form),
		[
			('b', 'table'),
			('a', 'table'),
		])
		
	def test_render_inherited (self):
		form = DerivedForm.unbound ()
		self.assertEqual (record_render (form),
		[
			('c', 'table'),
			('b', 'table'),
			('a', 'table'),
		])
		
class EncodingTypeTests (TestCase):
	def test_empty (self):
		expected = 'application/x-www-form-urlencoded'
		self.assertEqual (EmptyForm.enctype, expected)
		self.assertEqual (EmptyForm.bound ({}, {}).enctype, expected)
		self.assertEqual (EmptyForm.unbound ().enctype, expected)
		
	def test_normal (self):
		expected = 'application/x-www-form-urlencoded'
		self.assertEqual (BasicForm.enctype, expected)
		self.assertEqual (BasicForm.bound ({}, {}).enctype, expected)
		self.assertEqual (BasicForm.unbound ().enctype, expected)
		
	def test_with_file (self):
		expected = 'multipart/form-data'
		self.assertEqual (FormWithFile.enctype, expected)
		self.assertEqual (FormWithFile.bound ({}, {}).enctype, expected)
		self.assertEqual (FormWithFile.unbound ().enctype, expected)
		
class CustomValidationTests (TestCase):
	def test_custom_valid (self):
		form = CustomValidation.bound ({'a': ['test1']}, {})
		self.assertEqual (form.is_valid, True)
		self.assertEqual (form.errors, {})
		self.assertEqual (form.cleaned_data, {'a': "Cleaned test1"})
		
	def test_custom_invalid (self):
		form = CustomValidation.bound ({'a': ['test2']}, {})
		self.assertEqual (form.is_valid, False)
		self.assertEqual (form.errors, {'a': ["Error test2"]})
		
	def test_global_clean (self):
		form = CustomGlobalValidation.bound ({'a': ['test1']}, {})
		self.assertEqual (form.is_valid, True)
		self.assertEqual (form.errors, {})
		self.assertEqual (form.cleaned_data, {'a': "Cleaned test1"})
		
	def test_global_clean_invalid (self):
		form = CustomGlobalValidation.bound ({'a': ['test']}, {})
		self.assertEqual (form.is_valid, False)
		self.assertEqual (form.errors, {'a': ["Global error"]})
		
class UnboundFieldTests (TestCase):
	def test_attrs (self):
		field = FieldMock ()
		unbound = form.UnboundField ('name', field.recorder, '')
		self.assertEqual (unbound.name, 'name')
		self.assert_ (unbound.field is field.recorder)
		self.assertEqual (unbound.id_prefix, '')
		
	def test_default (self):
		field = FieldMock ()
		unbound = form.UnboundField ('name', field.recorder, '')
		self.assert_ (unbound.default is None)
		
	def test_field_default (self):
		field = FieldMock (default = "foo")
		unbound = form.UnboundField ('name', field.recorder, '')
		self.assertEqual (unbound.default, "foo")
		
	def test_default_override (self):
		field = FieldMock (default = "foo")
		unbound = form.UnboundField ('name', field.recorder, '', "bar")
		self.assertEqual (unbound.default, "bar")
		
	def test_needs_multipart (self):
		field = FieldMock (needs_multipart = True)
		unbound = form.UnboundField ('name', field.recorder, '')
		self.assertEqual (unbound.needs_multipart, True)
		
	def test_render (self):
		field = FieldMock ()
		field.methods (get_label = "label_text")
		field.methods (id_for_label = "id_for_label")
		field.methods (default_attrs = {})
		field.methods (render = "rendered")
		unbound = form.UnboundField ('name', field.recorder, 'id_prefix_')
		unbound.render_layout = mocking.StubbedMethod ((1, 2, 3))
		unbound.get_label = mocking.StubbedMethod ("label")
		rendered = unbound.render ()
		
		self.assertEqual (rendered, (1, 2, 3))
		self.assertEqual (unbound.get_label.calls, [
			(('label_text', 'id_for_label'), {}),
		])
		self.assertEqual (unbound.render_layout.calls, [
			(('table', 'label', "rendered"), {}),
		])
		
		with field.playback () as p:
			p.get_label ('name')
			p.id_for_label ('id_prefix_name')
			p.default_attrs ()
			p.render ('name', None, {'id': 'id_prefix_name'})
			
	def test_render_layout_table (self):
		field = FieldMock ()
		unbound = form.UnboundField ('name', field.recorder, '')
		rendered = unbound.render_layout ('table', "label", "stream")
		self.assertEqual (common.sorted_stream (rendered),
			'<tr><th>label</th><td>stream</td></tr>')
			
	def test_render_layout_div (self):
		field = FieldMock ()
		unbound = form.UnboundField ('name', field.recorder, '')
		rendered = unbound.render_layout ('div', "label", "stream")
		self.assertEqual (common.sorted_stream (rendered),
			'<div>label<div>stream</div></div>')
			
	def test_get_label (self):
		field = FieldMock ()
		unbound = form.UnboundField ('name', field.recorder, '')
		label = unbound.get_label ("label text", "id_for_label")
		self.assertEqual (common.sorted_stream (label),
			'<label for="id_for_label">label text</label>')
			
	def test_get_label_required (self):
		field = FieldMock (required = True)
		unbound = form.UnboundField ('name', field.recorder, '')
		label = unbound.get_label ("label text", "id_for_label")
		self.assertEqual (common.sorted_stream (label),
			'<label class="required" for="id_for_label">'
			'label text</label>')
			
class BoundFieldTests (TestCase):
	def test_attrs (self):
		field = FieldMock ()
		bound = form.BoundField ('name', field.recorder, '', [], {}, {})
		self.assertEqual (bound.name, 'name')
		self.assert_ (bound.field is field.recorder)
		self.assertEqual (bound.id_prefix, '')
		
	def test_needs_multipart (self):
		field = FieldMock (needs_multipart = True)
		bound = form.BoundField ('name', field.recorder, '', [], {}, {})
		self.assertEqual (bound.needs_multipart, True)
		
	def test_render (self):
		field = FieldMock ()
		field.methods (get_label = "label_text")
		field.methods (id_for_label = "id_for_label")
		field.methods (default_attrs = {})
		field.methods (render_request = "rendered")
		bound = form.BoundField ('name', field.recorder, 'id_prefix_', [], {}, {})
		bound.render_layout = mocking.StubbedMethod ((1, 2, 3))
		bound.get_label = mocking.StubbedMethod ("label")
		bound.get_error_list = mocking.StubbedMethod ("error_list")
		rendered = bound.render ()
		
		self.assertEqual (rendered, (1, 2, 3))
		self.assertEqual (bound.get_label.calls, [
			(('label_text', 'id_for_label'), {}),
		])
		self.assertEqual (bound.render_layout.calls, [
			(('table', 'label', ("error_list", "rendered")), {}),
		])
		self.assertEqual (bound.get_error_list.calls, [
			((), {}),
		])
		
		with field.playback () as p:
			p.get_label ('name')
			p.id_for_label ('id_prefix_name')
			p.default_attrs ()
			p.render_request ('name', {}, {}, {'id': 'id_prefix_name'})
			
	def test_render_layout_table (self):
		field = FieldMock ()
		bound = form.BoundField ('name', field.recorder, '', [], {}, {})
		rendered = bound.render_layout ('table', "label", "stream")
		self.assertEqual (common.sorted_stream (rendered),
			'<tr><th>label</th><td>stream</td></tr>')
			
	def test_render_layout_div (self):
		field = FieldMock ()
		bound = form.BoundField ('name', field.recorder, '', [], {}, {})
		rendered = bound.render_layout ('div', "label", "stream")
		self.assertEqual (common.sorted_stream (rendered),
			'<div>label<div>stream</div></div>')
			
	def test_get_label (self):
		field = FieldMock ()
		bound = form.BoundField ('name', field.recorder, '', [], {}, {})
		label = bound.get_label ("label text", "id_for_label")
		self.assertEqual (common.sorted_stream (label),
			'<label for="id_for_label">label text</label>')
			
	def test_get_label_required (self):
		field = FieldMock (required = True)
		bound = form.BoundField ('name', field.recorder, '', [], {}, {})
		label = bound.get_label ("label text", "id_for_label")
		self.assertEqual (common.sorted_stream (label),
			'<label class="required" for="id_for_label">'
			'label text</label>')
			
	def test_with_errors_empty (self):
		field = FieldMock (required = True)
		bound = form.BoundField ('name', field.recorder, '', [], {}, {})
		errors = bound.get_error_list ()
		self.assertEqual (common.sorted_stream (errors),
			'<div class="form_errors errors_for_name"/>')
			
	def test_with_errors (self):
		field = FieldMock (required = True)
		error_list = ['a', 'b']
		bound = form.BoundField ('name', field.recorder, '', error_list, {}, {})
		errors = bound.get_error_list ()
		self.assertEqual (common.sorted_stream (errors),
			'<div class="form_errors errors_for_name">'
			'<ul><li>ab</li><li>ab</li></ul></div>')
			
