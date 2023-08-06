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

from __future__ import absolute_import
import random, string
from itertools import imap
from genshi.builder import tag

from . import fields as fields_module, errors as error_module

__all__ = ['Form']

class OrderedDict (dict):
	def __init__ (self, pairs):
		pairs_seq = list (pairs)
		super (OrderedDict, self).__init__ (pairs_seq)
		self.ordered_keys = [k for k, v in pairs_seq]
		
	def __iter__ (self):
		return iter (self.ordered_keys)
		
	def keys (self):
		return self.ordered_keys
		
	def values (self):
		return [self[k] for k in self.keys()]
		
	def items (self):
		return [(k, self[k]) for k in self.keys ()]
		
	def iterkeys (self):
		return (k for k in self.ordered_keys)
		
	def itervalues (self):
		return (self[k] for k in self.ordered_keys)
		
	def iteritems (self):
		return ((k, self[k]) for k in self.ordered_keys)
		
	def __repr__ (self):
		def format (pair):
			return "%r: %r" % pair
		return "{%s}" % ", ".join (imap (format, self.iteritems()))
		
def random_alphanum (count):
	"""Generate a string containing ``count`` random alphanumeric
	characters.
	
	"""
	choices = string.ascii_letters + string.digits
	return ''.join (random.choice (choices) for ii in xrange (20))
	
def get_enctype (fields):
	for _, field in fields:
		if field.needs_multipart:
			return 'multipart/form-data'
	return 'application/x-www-form-urlencoded'
	
class RenderableField (object):
	"""A field that can be rendered to a Genshi markup stream.
	
	.. describe:: name
	
	.. describe:: field
	
	.. describe:: id_prefix
	
	.. describe:: needs_multipart
	
	"""
	def __init__ (self, name, field, id_prefix):
		self.name = name
		self.field = field
		self.id_prefix = id_prefix
		self.needs_multipart = field.needs_multipart
		
	def render_layout (self, layout, label, stream):
		if layout == 'table':
			return tag.tr (tag.th (label), tag.td (stream))
		if layout == 'div':
			return tag.div (label, tag.div (stream))
		raise NotImplementedError ()
		
	def get_label (self, text, id_):
		label = tag.label (text, for_ = id_)
		if self.field.required:
			label (class_ = 'required')
		return label
		
	def _render_common (self, layout, _render):
		label_text = self.field.get_label (self.name)
		field_id = "%s%s" % (self.id_prefix, self.name)
		id_for_label = self.field.id_for_label (field_id)
		label = self.get_label (label_text, id_for_label)
		attrs = self.field.default_attrs ()
		attrs['id'] = field_id
		return self.render_layout (layout, label, _render (attrs))
		
class BoundField (RenderableField):
	"""A :class:`RenderableField` which has been bound to user-defined
	data.
	
	.. describe:: post
	
	.. describe:: files
	
	.. describe:: errors
	
	"""
	def __init__ (self, name, field, id_prefix, errors, post, files):
		super (BoundField, self).__init__ (name, field, id_prefix)
		self.errors = errors
		self.post = post
		self.files = files
		
	def get_error_list (self):
		error_class = 'form_errors errors_for_' + self.name
		error_div = tag.div (class_ = error_class)
		if self.errors:
			errors = map (tag.li, self.errors)
			error_div (tag.ul (errors))
		return error_div
		
	def render (self, layout = "div"):
		def _render (attrs):
			get_stream = self.field.render_request
			stream = get_stream (self.name, self.post, self.files, attrs)
			errors = self.get_error_list ()
			return (errors, stream)
			
		return self._render_common (layout, _render)
		
class UnboundField (RenderableField):
	"""A :class:`RenderableField` which doesn't have any user-supplied data.
	
	.. describe:: default
	  
	"""
	def __init__ (self, name, field, id_prefix, default = None):
		super (UnboundField, self).__init__ (name, field, id_prefix)
		if default is None:
			default = field.default
		self.default = default
		
	def render (self, layout = "div"):
		def _render (attrs):
			return self.field.render (self.name, self.default, attrs)
			
		return self._render_common (layout, _render)
		
class RenderableForm (object):
	"""A form that can be rendered into a Genshi markup stream.
	
	.. describe:: enctype
	
	   The string to use for the ``enctype`` attribute in a ``<form>``
	   element.
	
	.. describe:: fields
	
	   A dictionary of :class:`BoundField` objects, indexed by field name.
	
	.. describe:: errors
	
	   A dictionary of lists of error messages. If the form is valid, this
	   will be an empty dictionary.
	
	.. describe:: is_valid
	
	   Boolean: whether or not the form is valid. A form is valid if no
	   errors were encountered when cleaning its data.
	
	.. describe:: cleaned_data
	
	   A dictionary of processed data values. This attribute will not
	   be present if the form is invalid.
	
	Once a :class:`RenderableForm` has been created from a :class:`Form`,
	pass it to a template and render it::
	
		<form enctype="${myform.enctype}">${myform.render ()}</form>
	
	"""
	def __init__ (self, fields, _bind, errors, cleaned):
		prefix = 'id_%s_' % (random_alphanum (10),)
		self.enctype = get_enctype (fields)
		self.fields = OrderedDict (_bind (prefix, *f) for f in fields)
		self.errors = errors
		self.is_valid = (not errors) and (cleaned is not None)
		
	def render (self, layout = "div"):
		"""Render a form into a Genshi markup stream, using the given
		*layout* type. Available layouts are ``div`` and ``table``.
		
		"""
		for field in self.fields.values ():
			for event in field.render (layout):
				yield event
				
class BoundForm (RenderableForm):
	"""Inherits from :class:`RenderableForm`."""
	is_bound = True
	
	def __init__ (self, fields, post, files, errors, cleaned_data):
		def _bind (id_prefix, name, field):
			field_errors = errors.get (name)
			field = BoundField (name, field, id_prefix,
			                    field_errors,
			                    post, files)
			return name, field
			
		super (BoundForm, self).__init__ (fields, _bind, errors, cleaned_data)
		if self.is_valid:
			self.cleaned_data = cleaned_data
			
class UnboundForm (RenderableForm):
	"""Inherits from :class:`RenderableForm`."""
	is_bound = False
	
	def __init__ (self, fields, defaults):
		def _bind (id_prefix, name, field):
			default = defaults.get (name)
			return name, UnboundField (name, field, id_prefix,
			                           default)
			
		super (UnboundForm, self).__init__ (fields, _bind, {}, None)
		
class _Form (object):
	fields = ()
	
	def clean (self, post, files):
		"""Convert *post* and *files* into a tuple (*cleaned*, *errors*).
		
		*post* is a map of (FieldName -> [POST Value]). *files* is a
		map of Django-style file objects, also indexed by field name.
		
		*cleaned* is a mapping of processed data, indexed by field name.
		*errors* is a map of (FieldName -> [Error messages]).
		
		"""
		default_clean = lambda v: v
		errors = {}
		cleaned_data = {}
		for name, field in self.fields:
			custom_clean = getattr (self, 'clean_' + name,
			                        default_clean)
			try:
				value = field.clean (name, post, files)
				value = custom_clean (value)
			except error_module.ValidationError, error:
				err_list = errors.setdefault (name, [])
				err_list.append (unicode (error))
			else:
				cleaned_data[name] = value
				
		return cleaned_data, errors
		
	@classmethod
	def unbound (cls, defaults = {}):
		"""Create an :class:`UnboundForm`, with the given defaults.
		
		"""
		return UnboundForm (cls.fields, defaults)
		
	@classmethod
	def bound (cls, post, files):
		"""Create a :class:`BoundForm` object, with the given uploaded user
		data.
		
		"""
		form = cls ()
		cleaned_data, errors = form.clean (post, files)
		return BoundForm (cls.fields, post, files, errors, cleaned_data)
		
	@classmethod
	def from_request (cls, request):
		"""Creating a :class:`BoundForm` from a Django request object.
		
		"""
		return cls.bound (dict (request.POST.lists ()), request.FILES)
		
def get_fields (bases, attrs):
	Field = fields_module.Field
	def key_func (pair):
		return Field.sort_key (pair[1])
		
	for base in bases:
		if issubclass (base, _Form):
			for field in base.fields:
				yield field
				
	unsorted = ((n, a) for n, a in attrs.items () if isinstance (a, Field))
	for field in sorted (unsorted, key = key_func):
		yield field
		
class FormType (type):
	def __new__ (mcs, name, bases, attrs):
		fields = tuple (get_fields (bases, attrs))
		attrs['fields'] = fields
		attrs['enctype'] = get_enctype (fields)
		return super (FormType, mcs).__new__ (mcs, name, bases, attrs)
		
class Form (_Form):
	"""Create a subclass of :class:`Form` to define custom forms::
	
		class MyForm (Form):
			name = genshi_forms.TextField ()
			age = genshi_forms.IntegerField ()
	
	Then call the :meth:`bound` or :meth:`unbound` methods to create a
	:class:`RenderableForm`, which can be rendered into a Genshi template.
	
	"""
	__metaclass__ = FormType
	
