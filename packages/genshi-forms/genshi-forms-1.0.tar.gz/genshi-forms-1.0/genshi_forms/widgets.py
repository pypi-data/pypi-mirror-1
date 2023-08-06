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

from genshi.builder import tag

__all__ = ['Widget', 'InputCheckbox', 'InputText', 'InputPassword', 'InputFile',
           'TextArea', 'Select']

class Widget (object):
	def __init__ (self, attrs = {}):
		self.attrs = attrs
		
	def render (self, name, value, attrs):
		"""Generate a Genshi markup stream.
		
		.. describe:: name
		
		   The field's name, which should be used for ``name``
		   HTML attributes.
		
		.. describe:: value
		
		   The default data value to render. This might also be text
		   the user entered on a form that failed validation.
		
		.. describe:: attrs
		
		   Extra attributes to include in the HTML element, if
		   appropriate to the widget type.
		
		"""
		raise NotImplementedError
		
	def _build_attrs (self, attrs, **kwargs):
		new_attrs = self.attrs.copy ()
		new_attrs.update (kwargs)
		new_attrs.update (attrs)
		return new_attrs
		
class _InputBase (Widget):
	def render (self, name, value, attrs):
		new_attrs = self._build_attrs (attrs,
			type = self.input_type,
			name = name,
			value = value,
		)
		return tag.input (**new_attrs)
		
class InputCheckbox (_InputBase):
	input_type = 'checkbox'
	
	def render (self, name, value, attrs):
		checked = 'checked' if value else None
		new_attrs = self._build_attrs (attrs, checked = checked)
		return super (InputCheckbox, self).render (name, None, new_attrs)
		
class InputText (_InputBase):
	input_type = 'text'
	
	def __init__ (self, size = None, max_size = None, **kwargs):
		super (InputText, self).__init__ (**kwargs)
		self.size = size
		self.max_size = max_size
		
	def render (self, name, value, attrs):
		new_attrs = self._build_attrs (attrs,
			size = self.size,
			maxlength = self.max_size)
		return super (InputText, self).render (name, value, new_attrs)
		
class InputPassword (_InputBase):
	input_type = 'password'
	
	def render (self, name, value, attrs):
		return super (InputPassword, self).render (name, None, attrs)
		
class InputFile (_InputBase):
	input_type = 'file'
	
class TextArea (Widget):
	def __init__ (self, rows = 10, columns = 40, **kwargs):
		super (TextArea, self).__init__ (**kwargs)
		self.rows = rows
		self.columns = columns
		
	def render (self, name, value, attrs):
		new_attrs = self._build_attrs (attrs,
			rows = self.rows,
			cols = self.columns,
			name = name)
		return tag.textarea (value, **new_attrs)
		
class Select (Widget):
	def __init__ (self, choices, **kwargs):
		super (Select, self).__init__ (**kwargs)
		self.choices = list (choices)
		
	def _get_options (self, choices, selected):
		for value, text in choices:
			if isinstance (text, (list, tuple)):
				options = list (self._get_options (text, selected))
				yield tag.optgroup (options, label = value)
			else:
				if unicode (value) in selected:
					s_attr = 'selected'
				else:
					s_attr = None
				yield tag.option (text, value = value, selected = s_attr)
				
	def render (self, name, selected, attrs):
		new_attrs = self._build_attrs (attrs, name = name)
		selected = map (unicode, selected)
		options = list (self._get_options (self.choices, selected))
		return tag.select (options, **new_attrs)
		
