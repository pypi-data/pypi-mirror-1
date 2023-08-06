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

from .. import widgets
from . import common

class TestCase (common.TestCase):
	def render (self, widget, *args, **kwargs):
		rendered = widget.render (*args, **kwargs)
		return common.sorted_stream (rendered)
		
class TestWidget (TestCase):
	def test_render (self):
		widget = widgets.Widget ()
		with self.check_exception (NotImplementedError, ''):
			widget.render ('name', '', {})
			
	def test_build_attrs_empty (self):
		widget = widgets.Widget ()
		self.assertEqual (widget._build_attrs ({}), {})
		
	def test_build_attrs (self):
		widget = widgets.Widget ()
		self.assertEqual (widget._build_attrs ({}, a = 1), {'a': 1})
		
	def test_build_attrs_preset (self):
		widget = widgets.Widget ({'a': 1})
		self.assertEqual (widget._build_attrs ({}), {'a': 1})
		
class TestInputCheckbox (TestCase):
	def test_render (self):
		widget = widgets.InputCheckbox ()
		self.assertEqual (
			self.render (widget, 'name', None, {}),
			'<input name="name" type="checkbox"/>',
		)
		
	def test_render_value (self):
		widget = widgets.InputCheckbox ()
		self.assertEqual (
			self.render (widget, 'name', True, {}),
			'<input checked="checked" name="name" type="checkbox"/>',
		)
		
class TestInputText (TestCase):
	def test_render (self):
		widget = widgets.InputText ()
		self.assertEqual (
			self.render (widget, 'name', None, {}),
			'<input name="name" type="text"/>',
		)
		
	def test_render_value (self):
		widget = widgets.InputText ()
		self.assertEqual (
			self.render (widget, 'name', "value", {}),
			'<input name="name" type="text" value="value"/>',
		)
		
	def test_set_size (self):
		widget = widgets.InputText (size = 10)
		self.assertEqual (widget.size, 10)
		self.assertEqual (
			self.render (widget, 'name', None, {}),
			'<input name="name" size="10" type="text"/>',
		)
		
	def test_set_maxsize (self):
		widget = widgets.InputText (max_size = 10)
		self.assertEqual (widget.max_size, 10)
		self.assertEqual (
			self.render (widget, 'name', None, {}),
			'<input maxlength="10" name="name" type="text"/>',
		)
		
class TestInputPassword (TestCase):
	def test_render (self):
		widget = widgets.InputPassword ()
		self.assertEqual (
			self.render (widget, 'name', None, {}),
			'<input name="name" type="password"/>',
		)
		
	def test_render_value (self):
		widget = widgets.InputPassword ()
		self.assertEqual (
			self.render (widget, 'name', "value", {}),
			'<input name="name" type="password"/>',
		)
		
class TestInputFile (TestCase):
	def test_render (self):
		widget = widgets.InputFile ()
		self.assertEqual (
			self.render (widget, 'name', None, {}),
			'<input name="name" type="file"/>',
		)
		
class TestTextArea (TestCase):
	def test_init_defaults (self):
		widget = widgets.TextArea ()
		self.assertEqual (widget.rows, 10)
		self.assertEqual (widget.columns, 40)
		
	def test_set_rows_columns (self):
		widget = widgets.TextArea (rows = 2, columns = 4)
		self.assertEqual (widget.rows, 2)
		self.assertEqual (widget.columns, 4)
		
	def test_render (self):
		widget = widgets.TextArea (rows = 2, columns = 4)
		self.assertEqual (
			self.render (widget, 'name', None, {'foo': 'bar'}),
			'<textarea cols="4" foo="bar" name="name" rows="2"/>',
		)
		
	def test_render_value (self):
		widget = widgets.TextArea (rows = 2, columns = 4)
		self.assertEqual (
			self.render (widget, 'name', "value", {}),
			'<textarea cols="4" name="name" rows="2">value</textarea>',
		)
		
class TestSelect (TestCase):
	def test_init_defaults (self):
		widget = widgets.Select (())
		self.assertEqual (widget.choices, [])
		
	def test_render_empty (self):
		widget = widgets.Select ([])
		self.assertEqual (
			self.render (widget, 'name', [], {}),
			'<select name="name"/>'
		)
		
	def test_render (self):
		widget = widgets.Select ([(1, "a"), ('2', "b")])
		self.assertEqual (
			self.render (widget, 'name', [], {}),
			'<select name="name">'
			'<option value="1">a</option>'
			'<option value="2">b</option>'
			'</select>'
		)
		
	def test_render_selected_1 (self):
		widget = widgets.Select ([(1, "a"), ('2', "b")])
		self.assertEqual (
			self.render (widget, 'name', ['1'], {}),
			'<select name="name">'
			'<option selected="selected" value="1">a</option>'
			'<option value="2">b</option>'
			'</select>'
		)
		
	def test_render_selected_2 (self):
		widget = widgets.Select ([(1, "a"), ('2', "b")])
		self.assertEqual (
			self.render (widget, 'name', [2], {}),
			'<select name="name">'
			'<option value="1">a</option>'
			'<option selected="selected" value="2">b</option>'
			'</select>'
		)
		
	def test_render_many_selected (self):
		widget = widgets.Select ([(1, "a"), ('2', "b")])
		self.assertEqual (
			self.render (widget, 'name', [1, 2], {}),
			'<select name="name">'
			'<option selected="selected" value="1">a</option>'
			'<option selected="selected" value="2">b</option>'
			'</select>'
		)
		
	def test_render_attr_passthrough (self):
		widget = widgets.Select ([])
		self.assertEqual (
			self.render (widget, 'name', [], {'a': 'b'}),
			'<select a="b" name="name"/>'
		)
		
	def test_render_groups (self):
		choices = [
			("label", [
				(1, "a"),
				(2, "b"),]),
			("label 2", (
 				(3, "c"),)),
			(4, "d")]
		widget = widgets.Select (choices)
		self.assertEqual (
			self.render (widget, 'name', [], {}),
			'<select name="name">'
			'<optgroup label="label">'
			'<option value="1">a</option>'
			'<option value="2">b</option>'
			'</optgroup>'
			'<optgroup label="label 2">'
			'<option value="3">c</option>'
			'</optgroup>'
			'<option value="4">d</option>'
			'</select>'
		)
		
		
