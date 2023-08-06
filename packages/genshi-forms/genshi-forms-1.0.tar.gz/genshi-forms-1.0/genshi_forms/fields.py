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

"""Basic field classes"""

import datetime

from . import errors, widgets, parsers

__all__ = ['Field', 'BooleanField', 'TextField', 'IntegerField', 'PasswordField',
           'FileField', 'DateField', 'TimeField', 'ChoiceField', 'MultipleChoiceField',
           'MultiValueField', 'DateTimeField', 'EMailField']

def pretty_name (name):
	name = name[0].upper() + name[1:]
	return name.replace('_', ' ')
	
class Field (object):
	"""Base class for all form fields.
	
	.. describe:: needs_multipart
	
		Whether this field requires a form to be submitted in
		``multipart/form-data`` encoding. Set this attribute
		to ``True`` if the field renders an ``<input type="file">``.
	
	.. describe:: default_error_messages
	
		A dictionary of field-specific error messages. Messages
		may be overridden by passing a dictionary as the
		*error_overrides* parameter of :meth:`__init__`.
	
	.. describe:: widget
	
		The :class:`widgets.Widget` to render the field with. A field
		does not need a widget, but the default implementations
		of :meth:`render` and :meth:`render_request` require one.
	
	"""
	
	needs_multipart = False
	
	# Internal use, used to order fields
	__creation_counter = 0
	
	default_error_messages = dict (
		required = "This field is required.",
	)
	
	widget = widgets.Widget
	
	def __init__ (self, required = True, widget = None, label = None,
	              default = None, error_overrides = None, **kwargs):
		"""Base field constructor.
		
		.. describe:: required
		
			Whether this field must be filled out for the form to
			be considered valid.
		
		.. describe:: widget
		
			A widget instance to be used instead of this field's
			default widget.
		
		.. describe:: label
		
			If set, this will override the automatically generated
			label for this field.
		
		.. describe:: default
		
			Provides a default value for use in unbound forms.
		
		.. describe:: error_overrides
		
			A dictionary of key -> message values that will
			override the error messages for this field.
		
		"""
		super (Field, self).__init__ (**kwargs)
		self.required = required
		self.label = label
		self.default = default
		
		if error_overrides is None:
			error_overrides = {}
		self.error_overrides = error_overrides
		
		if widget is None:
			widget = type (self).widget ()
		self.widget = widget
		
		self.__creation_counter = Field.__creation_counter
		Field.__creation_counter += 1
		
		self.__error_messages = None
		
	def __build_error_messages (self):
		def set_class_error_messages (messages, klass):
			for base_class in klass.__bases__:
				set_class_error_messages (messages, base_class)
			messages.update (getattr (klass, 'default_error_messages', {}))
			
		messages = {}
		set_class_error_messages (messages, self.__class__)
		return messages
		
	@classmethod
	def sort_key (cls, field):
		return field.__creation_counter
		
	def error_message (self, key, **kwargs):
		"""Find the full error message for an error key.
		
		This will search in the field's default and overridden
		error messages for a message matching *key*. If no
		message can be found, raises :exc:`KeyError`. Once the
		template has been found, it will be formatted using *kwargs*.
		
		"""
		if self.__error_messages is None:
			self.__error_messages = self.__build_error_messages ()
			
		try:
			tmpl = self.error_overrides[key]
		except KeyError:
			tmpl = self.__error_messages[key]
			
		return tmpl % kwargs
		
	def get_label (self, name):
		"""Retrieve the label for this field.
		
		If no label has been specified, attempts to generate one
		using the field's assigned *name* in the form.
		
		This method should not be overridden. Instead, pass a value
		for the *label* parameter of :meth:`__init__`.
		
		"""
		if self.label:
			return self.label
		return pretty_name (name)
		
	def default_attrs (self):
		return {}
		
	def id_for_label (self, base_id):
		"""Retrieve what ID labels for this field should use.
		
		By default, returns *base_id* unchanged. Fancier
		implementations could append text to *base_id* before
		returning it.
		
		For use with fields that render multiple widgets. In
		such fields, this method should be overridden to return
		the ID used for the first widget.
		
		"""
		return base_id
		
	def clean (self, name, post, files):
		"""Convert data in an HTTP request to a Python value.
		
		.. describe:: name
		
			The name this field should use for lookup in
			*post* or *files*.
		
		.. describe:: post
		
			A dictionary of lists of unicode strings. For
			a Django request object, you can retrieve
			an appropriately formatted dictionary using
			``dict (request.POST.lists ())``.
		
		.. describe:: files
		
			A dictionary of Django file objects, in the same
			format as ``request.FILES``.
		
		If there is an error converting the data, an instance of
		:exc:`genshi_forms.errors.ValidationError` will be raised.
		
		"""
		value = post.get (name, [''])[0]
		if self.required and (not value):
			error = self.error_message ('required')
			raise errors.ValidationError (error)
		return value
		
	def render (self, name, value, attrs):
		"""Render this field into a Genshi markup stream.
		
		.. describe:: name
		
			The name this field has been assigned within
			the form.
		
		.. describe:: value
		
			The Python value bound to this field, or ``None``.
		
		.. describe:: attrs
		
			Extra attributes to be rendered in the final
			widget, if applicable.
		
		"""
		return self.widget.render (name, value, attrs)
		
	def render_request (self, name, post, files, attrs):
		"""Render this field into a Genshi markup stream,
		using data from an HTTP request.
		
		This method is used because a user might enter invalid
		data into the form, but when the form is rendered their
		data should still be the default values for the fields.
		
		*name*, and *attrs* are used as
		in :meth:`render`. *post* and *files* are used as in
		:meth:`clean`.
		
		"""
		value = post.get (name, [''])[0]
		return self.widget.render (name, value, attrs)
		
class BooleanField (Field):
	"""A field whose values are ``True`` or ``False``.
	
	When cleaning, this field assumes that ``False`` values will not be
	present in the ``POST`` dictionary.
	
	"""
	widget = widgets.InputCheckbox
	
	def clean (self, name, post, files):
		return (name in post)
		
class TextField (Field):
	"""A field that cleans to a Python :class:`unicode` object.
	
	If this field is not present in the ``POST`` data,
	it will be cleaned to ``''``.
	
	"""
	widget = widgets.InputText
	
class IntegerField (Field):
	"""A field that cleans to an integer object.
	
	Returns the result of :func:`int`, or ``None`` on empty data.
	
	"""
	widget = widgets.InputText
	default_error_messages = dict (
		below_minimum = "This number must be at least %(min)d.",
		above_maximum = "This number must be at most %(max)d.",
		invalid = "\"%(text)s\" is not a number.",
	)
	
	def __init__ (self, minimum = None, maximum = None, **kwargs):
		super (IntegerField, self).__init__ (**kwargs)
		self.minimum = minimum
		self.maximum = maximum
		
	def clean (self, name, post, files):
		text = super (IntegerField, self).clean (name, post, files)
		if not text:
			return None
		try:
			value = int (text)
		except ValueError:
			error = self.error_message ('invalid', text = text)
			raise errors.ValidationError (error)
		if (self.minimum is not None) and value < self.minimum:
			error = self.error_message ('below_minimum',
			                            min = self.minimum)
			raise errors.ValidationError (error)
		if (self.maximum is not None) and value > self.maximum:
			error = self.error_message ('above_maximum',
			                            max = self.maximum)
			raise errors.ValidationError (error)
		return value
		
class PasswordField (Field):
	"""Like :class:`TextField`, but for passwords.
	
	By default, renders with an :class:`genshi_forms.widgets.InputPassword`
	widget. This blocks existing password data from being rendered.
	
	"""
	widget = widgets.InputPassword
	
class FileField (Field):
	"""A field for uploaded files.
	
	By default, renders with an :class:`genshi_forms.widgets.InputFile`
	widget. If this field is present in a form, that form's ``enctype``
	attribute will be set to ``multipart/form-data``.
	
	Data is cleaned to a valid Django file object.
	
	"""
	needs_multipart = True
	widget = widgets.InputFile
	default_error_messages = dict (
		invalid = "Invalid uploaded file. Check the form's encoding.",
		empty = "The uploaded file is empty.",
	)
	
	def clean (self, name, post, files):
		info = files.get (name)
		if not info:
			if self.required:
				error = self.error_message ('required')
				raise errors.ValidationError (error)
			return None
		invalid = False
		file_name = getattr (info, 'name', '')
		if not file_name:
			invalid = True
		try:
			file_size = info.size
		except AttributeError:
			invalid = True
			
		if invalid:
			error = self.error_message ('invalid')
			# Raise a value error instead of a validation error because
			# invalid uploaded files are not something the user can prevent.
			raise ValueError (error)
			
		if not file_size:
			error = self.error_message ('empty')
			raise errors.ValidationError (error)
		return info
		
class DateField (Field):
	"""Field for inputting dates.
	
	Data is cleaned to an instance of :class:`datetime.date`. Any format
	supported by :func:`genshi_forms.parsers.date` is supported by this field. When
	rendered, it will set ``class="date"`` on its widget.
	
	"""
	widget = widgets.InputText
	format = "%Y-%m-%d"
	default_error_messages = dict (
		invalid = "\"%(value)s\" is not a recognizable date.",
	)
	
	def __init__ (self, widget = None, **kwargs):
		if widget is None:
			widget = type (self).widget (size = 10, max_size = 10)
		super (DateField, self).__init__ (widget = widget, **kwargs)
		
	def default_attrs (self):
		return {'class': 'date'}
		
	def clean (self, name, post, files):
		text = super (DateField, self).clean (name, post, files)
		if not text:
			return None
		try:
			return parsers.date (text)
		except ValueError:
			error = self.error_message ('invalid', value = text)
			raise errors.ValidationError (error)
			
	def render (self, name, value, attrs):
		if isinstance (value, datetime.date):
			value = value.strftime (self.format)
		return super (DateField, self).render (name, value, attrs)
		
class TimeField (Field):
	"""Field for inputting times.
	
	Data is cleaned to an instance of :class:`datetime.time`. Any format
	supported by :class:`genshi_forms.parsers.time` is supported by this field. When
	rendered, it will set ``class="time"`` on its widget.
	
	"""
	widget = widgets.InputText
	format = "%H:%M:%S"
	default_error_messages = dict (
		invalid = "\"%(value)s\" is not a recognizable time.",
	)
	
	def __init__ (self, widget = None, **kwargs):
		if widget is None:
			widget = type (self).widget (size = 11, max_size = 11)
		super (TimeField, self).__init__ (widget = widget, **kwargs)
		
	def default_attrs (self):
		return {'class': 'time'}
		
	def clean (self, name, post, files):
		text = super (TimeField, self).clean (name, post, files)
		if not text:
			return None
		try:
			return parsers.time (text)
		except ValueError:
			error = self.error_message ('invalid', value = text)
			raise errors.ValidationError (error)
			
	def render (self, name, value, attrs):
		if isinstance (value, datetime.time):
			value = value.strftime (self.format)
		return super (TimeField, self).render (name, value, attrs)
		
class ChoiceField (Field):
	"""A field for choosing between a series of key-value options.
	
	When comparing, keys are normalized to strings using :func:`unicode`.
	
	Cleans data to a ``(key, value)`` tuple.
	
	"""
	widget = widgets.Select
	default_error_messages = dict (
		invalid = "No such choice.",
	)
	
	def __init__ (self, choices, size = None, widget = None, **kwargs):
		choices = list (choices)
		if widget is None:
			widget = type (self).widget (choices)
		super (ChoiceField, self).__init__ (widget = widget, **kwargs)
		self.choices = choices
		self.__choice_dict = None
		self.size = size
		
	def _get_choice_dict (self):
		def _get_pairs (choices):
			for choice in choices:
				key, value = choice
				if isinstance (value, (list, tuple)):
					for pair in _get_pairs (value):
						yield pair
				else:
					yield unicode (key), choice
					
		if self.__choice_dict is None:
			self.__choice_dict = dict (_get_pairs (self.choices))
		return self.__choice_dict
		
	def clean (self, name, post, files):
		text = super (ChoiceField, self).clean (name, post, files)
		if text:
			try:
				return self._get_choice_dict ()[text]
			except KeyError:
				error = self.error_message ('invalid')
				raise errors.ValidationError (error)
				
	def render (self, name, value, attrs):
		if value is None:
			selected = []
		elif isinstance (value, (list, tuple)):
			selected = value
		else:
			selected = [value]
		if self.size is not None:
			attrs.setdefault ('size', self.size)
		return self.widget.render (name, selected, attrs)
		
	def render_request (self, name, post, files, attrs):
		if self.size is not None:
			attrs.setdefault ('size', self.size)
		return self.widget.render (name, post.get (name, []), attrs)
		
class MultipleChoiceField (ChoiceField):
	"""Like :class:`ChoiceField`, but for more than one choice.
	
	Data is cleaned to a list of ``(key, value)`` tuples.
	
	"""
	def clean (self, name, post, files):
		def _clean (value):
			try:
				return self._get_choice_dict ()[value]
			except KeyError:
				error = self.error_message ('invalid')
				raise errors.ValidationError (error)
				
		values = post.get (name, [])
		cleaned = [_clean (v) for v in values if v]
		if (not cleaned) and self.required:
			error = self.error_message ('required')
			raise errors.ValidationError (error)
		return cleaned
		
	def render (self, name, value, attrs):
		if value is None:
			value = []
		if self.size is not None:
			attrs.setdefault ('size', self.size)
		attrs.setdefault ('multiple', 'multiple')
		return self.widget.render (name, value, attrs)
		
	def render_request (self, name, post, files, attrs):
		if self.size is not None:
			attrs.setdefault ('size', self.size)
		attrs.setdefault ('multiple', 'multiple')
		selected = post.get (name, [])
		return self.widget.render (name, selected, attrs)
		
class MultiValueField (Field):
	"""A field that contains multiple sub-fields
	
	Instead of overriding :meth:`Field.clean` and :meth:`Field.render`,
	subclasses may implement the :meth:`compress` and :meth:`decompress`
	methods.
	
	Subclasses *must* implement the :meth:`format_output` method.
	
	"""
	def __init__ (self, subfields, required = True, **kwargs):
		required = not all (f.required == False for f in subfields)
		super (MultiValueField, self).__init__ (required = required, **kwargs)
		self.fields = subfields
		
	def id_for_label (self, id_):
		return id_ + '.0'
		
	def compress (self, cleaned):
		"""Convert a list of cleaned values into a single value.
		
		*cleaned* is a list of values from the :meth:`Field.clean`
		methods of each subfield, in order. The return value may be
		of any type appropriate for the field.
		
		By default, returns *cleaned* unchanged.
		
		"""
		return cleaned
		
	def decompress (self, value):
		"""Convert a compressed value into a list of values.
		
		The returned list may be shorter than the list of subfields,
		in which case it will be padded with ``None``.
		
		By default, returns:
			* ``None`` -> ``[]``
			* sequence -> sequence
			* value -> [value]
		
		"""
		if value is None:
			return []
		if isinstance (value, (list, tuple)):
			return value
		return [value]
		
	def clean (self, name, post, files):
		def _clean_field (field_and_idx):
			index, field = field_and_idx
			f_name = '%s.%d' % (name, index)
			return field.clean (f_name, post, files)
			
		cleaned = map (_clean_field, enumerate (self.fields))
		return self.compress (cleaned)
		
	def __render_common (self, each, name, attrs, *extra):
		def id_override (index):
			if 'id' not in attrs:
				return attrs
			new_attrs = attrs.copy ()
			new_attrs['id'] = '%s.%d' % (attrs['id'], index)
			return new_attrs
			
		def _render_field (field_and_idx, *each_extra):
			index, field = field_and_idx
			f_name = '%s.%d' % (name, index)
			return each (field, f_name, id_override (index), *each_extra)
		rendered = map (_render_field, enumerate (self.fields), *extra)
		return self.format_output (rendered, name, attrs)
		
	def render (self, name, values, attrs):
		def _each (field, f_name, new_attrs, value):
			return field.render (f_name, value, new_attrs)
		decompressed = self.decompress (values)
		return self.__render_common (_each, name, attrs, decompressed)
		
	def render_request (self, name, post, files, attrs):
		def _each (field, f_name, new_attrs):
			return field.render_request (f_name, post, files, new_attrs)
		return self.__render_common (_each, name, attrs)
		
	def format_output (self, rendered_fields, name, attrs):
		"""Generate a Genshi markup stream.
		
		*rendered_fields* is a list of markup streams from subfields.
		*name* and *attrs* are as in :meth:`Field.render`.
		
		"""
		raise NotImplementedError
		
class DateTimeField (MultiValueField):
	"""Field for inputting combined date/times.
	
	Data is cleaned to an instance of :class:`datetime.datetime`.
	Any formats supported by :func:`genshi_forms.parsers.date` and
	:func:`genshi_forms.parsers.time` are supported. Values are returned 
	in the UTC timezone. If the input should be assumed to use a different
	timezone, one may be passed to the constructor. By default, all times
	are assumed to be in UTC.
	
	"""
	def __init__ (self, timezone = None, required = True, **kwargs):
		import pytz
		self.__utc = pytz.utc
		if timezone is None:
			timezone = pytz.utc
			
		subfields = [
			DateField (required = required),
			TimeField (required = required),
		]
		super (DateTimeField, self).__init__ (subfields = subfields, **kwargs)
		self.timezone = timezone
		
	def compress (self, cleaned):
		date, time = cleaned
		if not (date and time):
			return None
			
		naive_dt = datetime.datetime.combine (date, time)
		return self.timezone.localize (naive_dt).astimezone (self.__utc)
		
	def decompress (self, value):
		if value is None:
			return []
		if isinstance (value, datetime.datetime):
			if not value.tzinfo:
				value = self.__utc.localize (value)
			value = value.astimezone (self.timezone)
			return [value.date (), value.time ()]
		if isinstance (value, datetime.date):
			return [value, None]
		if isinstance (value, datetime.time):
			return [None, value]
		return [unicode (value)]
		
	def format_output (self, rendered_fields, name, attrs):
		from genshi.builder import tag
		return tag (*rendered_fields)
		
class EMailField (TextField):
	"""Field for inputting e-mail addresses.
	
	This field performs only basic validation, that there is a single
	``@`` sign in the text.
	
	"""
	default_error_messages = dict (
		invalid = "\"%(text)s\" doesn't look like an e-mail address.",
	)
	
	def clean (self, name, post, files):
		text = super (EMailField, self).clean (name, post, files)
		if not text:
			return text
		split = text.split ('@')
		if len (split) != 2 or (not split[0]) or (not split[1]):
			error = self.error_message ('invalid', text = text)
			raise errors.ValidationError (error)
		return text
		
