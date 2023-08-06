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

import datetime
import re
import pytz

from .. import fields, errors, widgets
from . import common

class RecordingWidget (object):
	def __init__ (self):
		self.render_calls = []
		
	def render (self, *args):
		self.render_calls.append (args)
		return len (self.render_calls)
		
class TestField (common.TestCase):
	def test_init_defaults (self):
		field = fields.Field ()
		self.assert_ (field.required is True)
		self.assert_ (field.label is None)
		self.assert_ (field.default is None)
		self.assertEqual (field.error_overrides, {})
		
	def test_sort_key (self):
		# ``Field.sort_key`` is a function that takes two fields and
		# determines in which order they should be rendered.
		a = fields.Field ()
		b = fields.Field ()
		self.assertEqual (
			sorted ([a, b], key = fields.Field.sort_key),
			[a, b])
		self.assertEqual (
			sorted ([b, a], key = fields.Field.sort_key),
			[a, b])
			
	def test_error_message (self):
		field = fields.Field ()
		self.assertEqual (
			field.error_message ('required'),
			"This field is required.")
		
	def test_custom_error_message (self):
		overrides = {'required': "Custom error message"}
		field = fields.Field (error_overrides = overrides)
		self.assertEqual (
			field.error_message ('required'),
			"Custom error message")
			
	def test_error_message_formatting (self):
		overrides = {'required': "Custom error message: %(text)s"}
		field = fields.Field (error_overrides = overrides)
		self.assertEqual (
			field.error_message ('required', text = "test"),
			"Custom error message: test")
			
	def test_get_label (self):
		field = fields.Field ()
		self.assertEqual (field.get_label ('name'), "Name")
		
	def test_get_label_multiword (self):
		field = fields.Field ()
		self.assertEqual (field.get_label ('my_name'), "My name")
		
	def test_get_label_override (self):
		field = fields.Field (label = "My label")
		self.assertEqual (field.get_label ('name'), "My label")
		
	def test_get_label_empty (self):
		field = fields.Field (label = "")
		self.assertEqual (field.get_label ('name'), "Name")
		
	def test_default_attrs (self):
		field = fields.Field ()
		self.assertEqual (field.default_attrs (), {})
		
	def test_id_for_label (self):
		field = fields.Field ()
		self.assertEqual (field.id_for_label (''), '')
		
	def test_clean_empty (self):
		field = fields.Field (required = False)
		self.assertEqual (field.clean ('name', {}, {}), '')
		
	def test_clean_empty_required (self):
		field = fields.Field ()
		with self.check_exception (errors.ValidationError,
		                           "This field is required."):
			field.clean ('name', {}, {})
			
	def test_clean_value (self):
		field = fields.Field ()
		cleaned = field.clean ('name', {'name': ["value"]}, {})
		self.assertEqual (cleaned, "value")
		
	def test_render_default (self):
		field = fields.Field ()
		with self.check_exception (NotImplementedError, ''):
			field.render ('name', None, {})
			
	def test_render_request_default (self):
		field = fields.Field ()
		with self.check_exception (NotImplementedError, ''):
			field.render_request ('name', {}, {}, {})
			
	def test_render (self):
		widget = RecordingWidget ()
		field = fields.Field (widget = widget)
		field.render ('name', "value", {})
		self.assertEqual (widget.render_calls, [('name', "value", {})])
		
	def test_render_request (self):
		widget = RecordingWidget ()
		field = fields.Field (widget = widget)
		field.render_request ('name', {'name': ["value"]}, {}, {})
		self.assertEqual (widget.render_calls, [('name', "value", {})])
		
	def test_render_request_empty (self):
		widget = RecordingWidget ()
		field = fields.Field (widget = widget)
		field.render_request ('name', {}, {}, {})
		self.assertEqual (widget.render_calls, [('name', "", {})])
		
class TestBooleanField (common.TestCase):
	def test_init_defaults (self):
		field = fields.BooleanField ()
		self.assert_ (isinstance (field.widget, widgets.InputCheckbox))
		
	def test_clean (self):
		field = fields.BooleanField ()
		cleaned = field.clean ('name', {'name': ['on']}, {})
		self.assert_ (cleaned is True)
		
	def test_clean_empty (self):
		field = fields.BooleanField ()
		cleaned = field.clean ('name', {}, {})
		self.assert_ (cleaned is False)
		
class TestTextField (common.TestCase):
	def test_init_defaults (self):
		field = fields.TextField ()
		self.assert_ (isinstance (field.widget, widgets.InputText))
		
	def test_clean_empty (self):
		field = fields.TextField (required = False)
		self.assertEqual (field.clean ('name', {}, {}), '')
		
	def test_clean_empty_required (self):
		field = fields.TextField ()
		with self.check_exception (errors.ValidationError,
		                           "This field is required."):
			field.clean ('name', {}, {})
			
	def test_clean_value (self):
		field = fields.TextField ()
		cleaned = field.clean ('name', {'name': ["value"]}, {})
		self.assertEqual (cleaned, "value")
		
class TestIntegerField (common.TestCase):
	def test_init_defaults (self):
		field = fields.IntegerField ()
		self.assert_ (isinstance (field.widget, widgets.InputText))
		self.assert_ (field.minimum is None)
		self.assert_ (field.maximum is None)
		
	def test_clean_empty (self):
		field = fields.IntegerField (required = False)
		self.assert_ (field.clean ('name', {}, {}) is None)
		self.assert_ (field.clean ('name', {'name': ['']}, {}) is None)
		
	def test_clean_empty_required (self):
		field = fields.IntegerField ()
		with self.check_exception (errors.ValidationError,
		                           "This field is required."):
			field.clean ('name', {}, {})
			
	def test_clean_value (self):
		field = fields.IntegerField ()
		self.assertEqual (field.clean ('name', {'name': ['10']}, {}), 10)
		
	def test_clean_invalid (self):
		field = fields.IntegerField (minimum = 0)
		with self.check_exception (errors.ValidationError,
		                           "\"test\" is not a number."):
			field.clean ('name', {'name': ['test']}, {})
			
	def test_clean_error_minimum (self):
		field = fields.IntegerField (minimum = 0)
		with self.check_exception (errors.ValidationError,
		                           "This number must be at least 0."):
			field.clean ('name', {'name': ['-1']}, {})
			
	def test_clean_error_maximum (self):
		field = fields.IntegerField (maximum = 0)
		with self.check_exception (errors.ValidationError,
		                           "This number must be at most 0."):
			field.clean ('name', {'name': ['1']}, {})
			
class TestPasswordField (common.TestCase):
	def test_init_defaults (self):
		field = fields.PasswordField ()
		self.assert_ (isinstance (field.widget, widgets.InputPassword))
		
class TestFileField (common.TestCase):
	class FakeFile (object):
		def __init__ (self, **kwargs):
			self.__dict__.update (kwargs)
			
	def test_init_defaults (self):
		field = fields.FileField ()
		self.assert_ (isinstance (field.widget, widgets.InputFile))
		
	def test_clean_empty (self):
		field = fields.FileField (required = False)
		self.assert_ (field.clean ('name', {}, {}) is None)
		
	def test_clean_empty_required (self):
		field = fields.FileField ()
		with self.check_exception (errors.ValidationError,
		                           "This field is required."):
			field.clean ('name', {}, {})
			
	def test_clean_missing_name (self):
		field = fields.FileField ()
		info = self.FakeFile ()
		with self.check_exception (ValueError,
			"Invalid uploaded file. Check the form's encoding."):
			field.clean ('name', {}, {'name': info})
			
	def test_clean_invalid_name (self):
		field = fields.FileField ()
		info = self.FakeFile (name = '')
		with self.check_exception (ValueError,
			"Invalid uploaded file. Check the form's encoding."):
			field.clean ('name', {}, {'name': info})
			
	def test_clean_missing_size (self):
		field = fields.FileField ()
		info = self.FakeFile (name = 'name')
		with self.check_exception (ValueError,
			"Invalid uploaded file. Check the form's encoding."):
			field.clean ('name', {}, {'name': info})
			
	def test_clean_empty_data (self):
		field = fields.FileField ()
		info = self.FakeFile (name = 'name', size = 0)
		with self.check_exception (errors.ValidationError,
		                           "The uploaded file is empty."):
			field.clean ('name', {}, {'name': info})
			
	def test_clean_value (self):
		field = fields.FileField ()
		info = self.FakeFile (name = 'name', size = 10)
		self.assertEqual (field.clean ('name', {}, {'name': info}), info)
		
class TestDateField (common.TestCase):
	def test_init_defaults (self):
		field = fields.DateField ()
		self.assert_ (isinstance (field.widget, widgets.InputText))
		self.assertEqual (field.widget.size, 10)
		self.assertEqual (field.widget.max_size, 10)
		
	def test_default_attrs (self):
		field = fields.DateField ()
		self.assertEqual (field.default_attrs (), {'class': 'date'})
		
	def test_clean_empty (self):
		field = fields.DateField (required = False)
		self.assert_ (field.clean ('name', {}, {}) is None)
		self.assert_ (field.clean ('name', {'name': ['']}, {}) is None)
		
	def test_clean_empty_required (self):
		field = fields.DateField ()
		with self.check_exception (errors.ValidationError,
		                           "This field is required."):
			field.clean ('name', {}, {})
			
		with self.check_exception (errors.ValidationError,
		                           "This field is required."):
			field.clean ('name', {'name': ['']}, {})
			
	def test_clean_value (self):
		field = fields.DateField ()
		cleaned = field.clean ('name', {'name': ['2000-2-3']}, {})
		self.assertEqual (cleaned, datetime.date (2000, 2, 3))
		
	def test_clean_invalid (self):
		field = fields.DateField ()
		with self.check_exception (errors.ValidationError,
		                           "\"12345\" is not a recognizable date."):
			field.clean ('name', {'name': ['12345']}, {})
			
	def test_render_empty (self):
		widget = RecordingWidget ()
		field = fields.DateField (widget = widget)
		field.render ('name', None, {})
		self.assertEqual (widget.render_calls, [
			('name', None, {}),
		])
		
	def test_render (self):
		widget = RecordingWidget ()
		field = fields.DateField (widget = widget)
		field.render ('name', datetime.date (2001, 2, 3), {})
		self.assertEqual (widget.render_calls, [
			('name', '2001-02-03', {}),
		])
		
class TestTimeField (common.TestCase):
	def test_init_defaults (self):
		field = fields.TimeField ()
		self.assert_ (isinstance (field.widget, widgets.InputText))
		self.assertEqual (field.widget.size, 11)
		self.assertEqual (field.widget.max_size, 11)
		
	def test_default_attrs (self):
		field = fields.TimeField ()
		self.assertEqual (field.default_attrs (), {'class': 'time'})
		
	def test_clean_empty (self):
		field = fields.TimeField (required = False)
		self.assert_ (field.clean ('name', {}, {}) is None)
		self.assert_ (field.clean ('name', {'name': ['']}, {}) is None)
		
	def test_clean_empty_required (self):
		field = fields.TimeField ()
		with self.check_exception (errors.ValidationError,
		                           "This field is required."):
			field.clean ('name', {}, {})
			
		with self.check_exception (errors.ValidationError,
		                           "This field is required."):
			field.clean ('name', {'name': ['']}, {})
			
	def test_clean_value (self):
		field = fields.TimeField ()
		cleaned = field.clean ('name', {'name': ['10:11:12']}, {})
		self.assertEqual (cleaned, datetime.time (10, 11, 12))
		
	def test_clean_invalid (self):
		field = fields.TimeField ()
		with self.check_exception (errors.ValidationError,
		                           "\"12345\" is not a recognizable time."):
			field.clean ('name', {'name': ['12345']}, {})
			
	def test_render_empty (self):
		widget = RecordingWidget ()
		field = fields.TimeField (widget = widget)
		field.render ('name', None, {})
		self.assertEqual (widget.render_calls, [
			('name', None, {})
		])
		
	def test_render (self):
		widget = RecordingWidget ()
		field = fields.TimeField (widget = widget)
		field.render ('name', datetime.time (14, 13, 12), {})
		self.assertEqual (widget.render_calls, [
			('name', '14:13:12', {})
		])
		
class TestChoiceField (common.TestCase):
	def test_init_defaults (self):
		field = fields.ChoiceField ((('1', "a"), ('2', "b")),)
		self.assert_ (isinstance (field.widget, widgets.Select))
		self.assertEqual (field.choices, [('1', "a"), ('2', "b")])
		self.assert_ (field.size is None)
		
	def test_clean_empty (self):
		field = fields.ChoiceField ([('1', "a"), ('2', "b")],
		                            required = False)
		self.assert_ (field.clean ('name', {}, {}) is None)
		self.assert_ (field.clean ('name', {'name': ['']}, {}) is None)
		
	def test_clean_empty_required (self):
		field = fields.ChoiceField ([('1', "a"), ('2', "b")])
		with self.check_exception (errors.ValidationError,
		                           "This field is required."):
			field.clean ('name', {}, {})
			
		with self.check_exception (errors.ValidationError,
		                           "This field is required."):
			field.clean ('name', {'name': ['']}, {})
			
	def test_clean_value (self):
		field = fields.ChoiceField ([('1', "a"), ('2', "b")])
		cleaned = field.clean ('name', {'name': ['1']}, {})
		self.assertEqual (cleaned, ('1', "a"))
		
	def test_clean_value_nonstring (self):
		field = fields.ChoiceField ([(1, "a"), (2, "b")])
		cleaned = field.clean ('name', {'name': ['1']}, {})
		self.assertEqual (cleaned, (1, "a"))
		
	def test_clean_value_invalid (self):
		field = fields.ChoiceField ([('1', "a"), ('2', "b")])
		
		with self.check_exception (errors.ValidationError,
		                           "No such choice."):
			field.clean ('name', {'name': ['3']}, {})
			
	def test_clean_value_in_optgroup (self):
		choices = [("a", ((1, "c"),)), ("d", [(2, "e")])]
		field = fields.ChoiceField (choices)
		
		cleaned = field.clean ('name', {'name': ['1']}, {})
		self.assertEqual (cleaned, (1, "c"))
		
		cleaned = field.clean ('name', {'name': ['2']}, {})
		self.assertEqual (cleaned, (2, "e"))
		
	def test_render (self):
		widget = RecordingWidget ()
		choices = [(1, "a"), ('2', "b")]
		field = fields.ChoiceField (choices, widget = widget)
		field.render ('name', None, {})
		self.assertEqual (widget.render_calls, [('name', [], {})])
		
	def test_render_pre_selected (self):
		widget = RecordingWidget ()
		choices = [(1, "a"), ('2', "b")]
		field = fields.ChoiceField (choices, widget = widget)
		field.render ('name', 1, {})
		self.assertEqual (widget.render_calls, [('name', [1], {})])
		
	def test_render_with_size (self):
		widget = RecordingWidget ()
		field = fields.ChoiceField ([], size = 10, widget = widget)
		field.render ('name', None, {})
		self.assertEqual (widget.render_calls, [('name', [], {'size': 10})])
		
	def test_render_selected_list (self):
		widget = RecordingWidget ()
		choices = [(1, "a"), ('2', "b")]
		field = fields.ChoiceField (choices, widget = widget)
		field.render ('name', [], {})
		self.assertEqual (widget.render_calls, [('name', [], {})])
		
	def test_render_request (self):
		widget = RecordingWidget ()
		choices = [(1, "a"), ('2', "b")]
		field = fields.ChoiceField (choices, widget = widget)
		field.render_request ('name', {'name': ["1"]}, {}, {})
		self.assertEqual (widget.render_calls, [('name', ["1"], {})])
		
	def test_render_request_empty (self):
		widget = RecordingWidget ()
		choices = [(1, "a"), ('2', "b")]
		field = fields.ChoiceField (choices, widget = widget)
		field.render_request ('name', {}, {}, {})
		self.assertEqual (widget.render_calls, [('name', [], {})])
		
	def test_render_request_with_size (self):
		widget = RecordingWidget ()
		field = fields.ChoiceField ([], size = 10, widget = widget)
		field.render_request ('name', {}, {}, {})
		self.assertEqual (widget.render_calls, [('name', [], {'size': 10})])
		
class TestMultipleChoiceField (common.TestCase):
	def test_init_defaults (self):
		field = fields.MultipleChoiceField ((('1', "a"), ('2', "b")),)
		self.assert_ (isinstance (field.widget, widgets.Select))
		self.assertEqual (field.choices, [('1', "a"), ('2', "b")])
		self.assert_ (field.size is None)
		
	def test_clean_empty (self):
		field = fields.MultipleChoiceField ([('1', "a"), ('2', "b")],
		                            required = False)
		self.assertEqual (field.clean ('name', {}, {}), [])
		self.assertEqual (field.clean ('name', {'name': ['']}, {}), [])
		
	def test_clean_empty_required (self):
		field = fields.MultipleChoiceField ([('1', "a"), ('2', "b")])
		with self.check_exception (errors.ValidationError,
		                           "This field is required."):
			field.clean ('name', {}, {})
			
		with self.check_exception (errors.ValidationError,
		                           "This field is required."):
			field.clean ('name', {'name': ['']}, {})
			
	def test_clean_value (self):
		field = fields.MultipleChoiceField ([('1', "a"), ('2', "b")])
		cleaned = field.clean ('name', {'name': ['1']}, {})
		self.assertEqual (cleaned, [('1', "a")])
		
	def test_clean_value_nonstring (self):
		field = fields.MultipleChoiceField ([(1, "a"), (2, "b")])
		cleaned = field.clean ('name', {'name': ['1']}, {})
		self.assertEqual (cleaned, [(1, "a")])
		
	def test_clean_multiple_values (self):
		field = fields.MultipleChoiceField ([(1, "a"), (2, "b"), (3, "c")])
		cleaned = field.clean ('name', {'name': ['1', '2']}, {})
		self.assertEqual (cleaned, [(1, "a"), (2, "b")])
		
	def test_clean_value_invalid (self):
		field = fields.MultipleChoiceField ([('1', "a"), ('2', "b")])
		
		with self.check_exception (errors.ValidationError,
		                           "No such choice."):
			field.clean ('name', {'name': ['3']}, {})
			
	def test_render (self):
		widget = RecordingWidget ()
		field = fields.MultipleChoiceField ([], widget = widget)
		field.render ('name', [], {})
		self.assertEqual (widget.render_calls, [
			('name', [], {'multiple': 'multiple'}),
		])
		
	def test_render_none (self):
		widget = RecordingWidget ()
		field = fields.MultipleChoiceField ([], widget = widget)
		field.render ('name', None, {})
		self.assertEqual (widget.render_calls, [
			('name', [], {'multiple': 'multiple'}),
		])
		
	def test_render_request (self):
		widget = RecordingWidget ()
		field = fields.MultipleChoiceField ([], widget = widget)
		field.render_request ('name', {}, {}, {})
		self.assertEqual (widget.render_calls, [
			('name', [], {'multiple': 'multiple'}),
		])
		
	def test_render_with_size (self):
		widget = RecordingWidget ()
		field = fields.MultipleChoiceField ([], size = 5, widget = widget)
		field.render ('name', [], {})
		self.assertEqual (widget.render_calls, [
			('name', [], {'multiple': 'multiple', 'size': 5}),
		])
		
	def test_render_request_with_size (self):
		widget = RecordingWidget ()
		field = fields.MultipleChoiceField ([], size = 5, widget = widget)
		field.render_request ('name', {}, {}, {})
		self.assertEqual (widget.render_calls, [
			('name', [], {'multiple': 'multiple', 'size': 5}),
		])
		
class TestMultiValueField (common.TestCase):
	def test_init_defaults (self):
		field = fields.MultiValueField ([])
		self.assert_ (isinstance (field.widget, widgets.Widget))
		
	def test_init_fields (self):
		subfields = [
			fields.TextField (),
			fields.TextField (),
		]
		field = fields.MultiValueField (subfields)
		self.assertEqual (field.fields, subfields)
		self.assert_ (field.required is True)
		
	def test_init_fields_not_required (self):
		subfields = [
			fields.TextField (required = False),
			fields.TextField (required = False),
		]
		field = fields.MultiValueField (subfields)
		self.assert_ (field.required is False)
		
	def test_id_for_label (self):
		field = fields.MultiValueField ([])
		self.assertEqual (field.id_for_label (''), '.0')
		
	def test_clean_empty (self):
		subfields = [
			fields.TextField (required = False),
			fields.TextField (required = False),
		]
		field = fields.MultiValueField (subfields)
		cleaned = field.clean ('name', {}, {})
		self.assertEqual (cleaned, ['', ''])
		
	def test_clean_empty_required (self):
		subfields = [
			fields.TextField (),
			fields.TextField (),
		]
		field = fields.MultiValueField (subfields)
		with self.check_exception (errors.ValidationError,
		                           "This field is required."):
			field.clean ('name', {}, {})
			
	def test_clean (self):
		subfields = [
			fields.TextField (required = False),
			fields.TextField (required = False),
		]
		field = fields.MultiValueField (subfields)
		cleaned = field.clean ('name', {'name.0': ['a'], 'name.1': ['b']}, {})
		self.assertEqual (cleaned, ['a', 'b'])
		
	def test_compress (self):
		field = fields.MultiValueField ([])
		self.assertEqual (field.compress ([]), [])
		self.assertEqual (field.compress ([1, 2, 3]), [1, 2, 3])
		
	def test_decompress (self):
		field = fields.MultiValueField ([])
		self.assertEqual (field.decompress (None), [])
		self.assertEqual (field.decompress ([]), [])
		self.assertEqual (field.decompress (""), [""])
		self.assertEqual (field.decompress ("value"), ["value"])
		
	def test_render (self):
		widget = RecordingWidget ()
		subfields = [
			fields.TextField (widget = widget),
			fields.TextField (widget = widget),
		]
		field = fields.MultiValueField (subfields)
		field.format_output = lambda o,n,a: o
		rendered = field.render ('name', None, {})
		
		self.assertEqual (rendered, [1, 2])
		self.assertEqual (widget.render_calls, [
			('name.0', None, {}),
			('name.1', None, {}),
		])
		
	def test_render_with_id (self):
		widget = RecordingWidget ()
		subfields = [
			fields.TextField (widget = widget),
			fields.TextField (widget = widget),
		]
		field = fields.MultiValueField (subfields)
		field.format_output = lambda o,n,a: o
		rendered = field.render ('name', None, {'id': 'id'})
		
		self.assertEqual (rendered, [1, 2])
		self.assertEqual (widget.render_calls, [
			('name.0', None, {'id': 'id.0'}),
			('name.1', None, {'id': 'id.1'}),
		])
		
	def test_render_with_values (self):
		widget = RecordingWidget ()
		subfields = [
			fields.TextField (widget = widget),
			fields.TextField (widget = widget),
		]
		field = fields.MultiValueField (subfields)
		field.format_output = lambda o,n,a: o
		rendered = field.render ('name', ['a', 'b'], {})
		
		self.assertEqual (rendered, [1, 2])
		self.assertEqual (widget.render_calls, [
			('name.0', 'a', {}),
			('name.1', 'b', {}),
		])
		
		
	def test_render_request_empty (self):
		widget = RecordingWidget ()
		subfields = [
			fields.TextField (widget = widget),
			fields.TextField (widget = widget),
		]
		field = fields.MultiValueField (subfields)
		field.format_output = lambda o,n,a: o
		rendered = field.render_request ('name', {}, {}, {})
		
		self.assertEqual (rendered, [1, 2])
		self.assertEqual (widget.render_calls, [
			('name.0', '', {}),
			('name.1', '', {}),
		])
		
	def test_render_request (self):
		widget = RecordingWidget ()
		subfields = [
			fields.TextField (widget = widget),
			fields.TextField (widget = widget),
		]
		field = fields.MultiValueField (subfields)
		field.format_output = lambda o,n,a: o
		post = {'name.0': ['a'], 'name.1': ['b']}
		rendered = field.render_request ('name', post, {}, {})
		
		self.assertEqual (rendered, [1, 2])
		self.assertEqual (widget.render_calls, [
			('name.0', 'a', {}),
			('name.1', 'b', {}),
		])
		
	def test_render_request_with_id (self):
		widget = RecordingWidget ()
		subfields = [
			fields.TextField (widget = widget),
			fields.TextField (widget = widget),
		]
		field = fields.MultiValueField (subfields)
		field.format_output = lambda o,n,a: o
		rendered = field.render_request ('name', {}, {}, {'id': 'id'})
		
		self.assertEqual (rendered, [1, 2])
		self.assertEqual (widget.render_calls, [
			('name.0', '', {'id': 'id.0'}),
			('name.1', '', {'id': 'id.1'}),
		])
		
class TestDateTimeField (common.TestCase):
	def test_init_defaults (self):
		field = fields.DateTimeField ()
		self.assertEqual (field.timezone, pytz.utc)
		self.assertEqual (field.required, True)
		
	def test_init (self):
		tz = pytz.timezone ('America/Los_Angeles')
		field = fields.DateTimeField (tz)
		self.assertEqual (field.timezone, tz)
		
	def test_clean (self):
		field = fields.DateTimeField ()
		
		post = {'name.0': ['2001-2-3'], 'name.1': ['10:11:12 AM']}
		expected = datetime.datetime (2001, 2, 3, 10, 11, 12, 0, pytz.utc)
		cleaned = field.clean ('name', post, {})
		
		self.assertEqual (cleaned, expected)
		self.assertEqual (cleaned.tzinfo, pytz.utc)
		
	def test_clean_empty (self):
		field = fields.DateTimeField (required = False)
		self.assertEqual (field.clean ('name', {}, {}), None)
		post = {'name.0': [''], 'name.1': ['']}
		self.assertEqual (field.clean ('name', post, {}), None)
		
	def test_clean_empty_required (self):
		field = fields.DateTimeField ()
		with self.check_exception (errors.ValidationError,
		                           "This field is required."):
			field.clean ('name', {}, {})
			
		with self.check_exception (errors.ValidationError,
		                           "This field is required."):
			field.clean ('name', {'name.0': [''], 'name.1': ['']}, {})
			
	def test_clean_value_timezone (self):
		tz = pytz.timezone ('America/Los_Angeles')
		field = fields.DateTimeField (tz)
		post = {'name.0': ['2001-2-3'], 'name.1': ['10:11:12 AM']}
		expected = datetime.datetime (2001, 2, 3, 10, 11, 12, 0, tz)
		cleaned = field.clean ('name', post, {})
		self.assertEqual (cleaned, expected)
		self.assertEqual (cleaned.tzinfo, pytz.utc)
		
	def test_clean_invalid_date (self):
		field = fields.DateTimeField ()
		post = {'name.0': ['testing'], 'name.1': ['10:11:12 AM']}
		error_msg = "\"testing\" is not a recognizable date."
		with self.check_exception (errors.ValidationError, error_msg):
			field.clean ('name', post, {})
			
	def test_clean_invalid_time (self):
		field = fields.DateTimeField ()
		post = {'name.0': ['2001-2-3'], 'name.1': ['testing']}
		error_msg = "\"testing\" is not a recognizable time."
		with self.check_exception (errors.ValidationError, error_msg):
			field.clean ('name', post, {})
			
	def test_decompress_none (self):
		field = fields.DateTimeField ()
		self.assertEqual (field.decompress (None), [])
		
	def test_decompress_date (self):
		field = fields.DateTimeField ()
		value = datetime.date (2001, 2, 3)
		self.assertEqual (field.decompress (value), [value, None])
		
	def test_decompress_time (self):
		field = fields.DateTimeField ()
		value = datetime.time (10, 11, 12)
		self.assertEqual (field.decompress (value), [None, value])
		
	def test_decompress_naive_datetime (self):
		field = fields.DateTimeField ()
		value = datetime.datetime (2001, 2, 3, 10, 11, 12, 0)
		date = datetime.date (2001, 2, 3)
		time = datetime.time (10, 11, 12)
		self.assertEqual (field.decompress (value), [date, time])
		
	def test_decompress_full_datetime (self):
		field = fields.DateTimeField ()
		value = datetime.datetime (2001, 2, 3, 10, 11, 12, 0, pytz.utc)
		date = datetime.date (2001, 2, 3)
		time = datetime.time (10, 11, 12)
		self.assertEqual (field.decompress (value), [date, time])
		
	def test_decompress_naive_datetime_nonlocal (self):
		tz = pytz.timezone ('America/Los_Angeles')
		field = fields.DateTimeField (tz)
		value = datetime.datetime (2001, 2, 3, 10, 11, 12, 0)
		date = datetime.date (2001, 2, 3)
		time = datetime.time (2, 11, 12)
		self.assertEqual (field.decompress (value), [date, time])
		
	def test_decompress_full_datetime_nonlocal (self):
		tz = pytz.timezone ('America/Los_Angeles')
		field = fields.DateTimeField (tz)
		value = datetime.datetime (2001, 2, 3, 10, 11, 12, 0, pytz.utc)
		date = datetime.date (2001, 2, 3)
		time = datetime.time (2, 11, 12)
		self.assertEqual (field.decompress (value), [date, time])
		
class TestEMailField (common.TestCase):
	def test_init_defaults (self):
		field = fields.EMailField ()
		self.assert_ (isinstance (field.widget, widgets.InputText))
		
	def test_clean_empty (self):
		field = fields.EMailField (required = False)
		self.assertEqual (field.clean ('name', {}, {}), '')
		
	def test_clean (self):
		field = fields.EMailField ()
		post = {'name': ['jdoe@example.com']}
		self.assertEqual (field.clean ('name', post, {}), 'jdoe@example.com')
		
	def test_clean_invalid (self):
		field = fields.EMailField ()
		with self.check_exception (errors.ValidationError,
		                           "\"invalid\" doesn't look like an"
		                           " e-mail address."):
			field.clean ('name', {'name': ["invalid"]}, {})
			
		with self.check_exception (errors.ValidationError,
		                           "\"@invalid\" doesn't look like an"
		                           " e-mail address."):
			field.clean ('name', {'name': ["@invalid"]}, {})
			
		with self.check_exception (errors.ValidationError,
		                           "\"invalid@\" doesn't look like an"
		                           " e-mail address."):
			field.clean ('name', {'name': ["invalid@"]}, {})
			
		with self.check_exception (errors.ValidationError,
		                           "\"inv@alid@\" doesn't look like an"
		                           " e-mail address."):
			field.clean ('name', {'name': ["inv@alid@"]}, {})
			
