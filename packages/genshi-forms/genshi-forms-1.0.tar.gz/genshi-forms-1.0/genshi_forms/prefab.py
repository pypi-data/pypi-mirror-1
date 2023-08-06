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

from . import fields, errors, widgets, parsers

__all__ = ['ImageField', 'NewPasswordField', 'SubformField']

class ImageField (fields.FileField):
	def clean (self, name, post, files):
		from cStringIO import StringIO
		from PIL import Image
		
		file_data = super (ImageField, self).clean (name, post, files)
		if file_data is None:
			return
		if hasattr (file_data, 'temporary_file_path'):
			file_obj = open (file_data.temporary_file_path (), 'rb')
		else:
			file_obj = StringIO (file_data.read ())
			
		# verify() is the only method that can spot a corrupt PNG,
		#  but it must be called immediately after the constructor
		trial_image = Image.open (file_obj)
		trial_image.verify ()
		
		file_obj.reset ()
		
		# load() is the only method that can spot a truncated JPEG,
		#  but it cannot be called sanely after verify()
		trial_image = Image.open (file_obj)
		trial_image.load ()
		
		return trial_image.convert ('RGB')
		
class SubformField (fields.MultiValueField):
	def __init__ (self, subfields, required = True, **kwargs):
		subfield_list = [f for n, f in subfields]
		super (SubformField, self).__init__ (subfields = subfield_list, **kwargs)
		self.__subfields = subfields
		self.__field_names = [n for n, f in subfields]
		
	def compress (self, cleaned):
		return dict (zip (self.__field_names, cleaned))
		
	def decompress (self, values):
		if values is None:
			values = {}
			
		return [values.get (name, None) for name in self.__field_names]
		
	def format_output (self, rendered_fields, name, attrs):
		from genshi.builder import tag
		id_base = attrs.get ('id', None)
		def _make_tr (field_name_idx, stream):
			index, (name, field) = field_name_idx
			if id_base is None:
				f_id = None
			else:
				f_id = '%s.%d' % (id_base, index)
			label = tag.label (field.get_label (name), for_ = f_id)
			return tag.tr (tag.td (label), tag.td (stream))
			
		error_div = tag.div (class_ = "form_errors errors_for_" + name),
		rows = map (_make_tr, enumerate (self.__subfields), rendered_fields)
		return tag (error_div, tag.table (*rows, **attrs))
		
class NewPasswordField (SubformField):
	default_error_messages = dict (
		no_match = "The passwords do not match. Please enter the same"
		           " password twice.",
		need_both = "Please fill both fields.",
	)
	
	def __init__ (self, required = True, **kwargs):
		subfields = [
			('set', fields.PasswordField (required = required)),
			('confirm', fields.PasswordField (required = required)),
		]
		super (NewPasswordField, self).__init__ (subfields = subfields, **kwargs)
		
	def compress (self, cleaned):
		set_text, confirm_text = cleaned
		if set_text and confirm_text:
			if set_text == confirm_text:
				return set_text
			error = self.error_message ('no_match')
			raise errors.ValidationError (error)
		if set_text or confirm_text:
			error = self.error_message ('need_both')
			raise errors.ValidationError (error)
		if self.required:
			error = self.error_message ('required')
			raise errors.ValidationError (error)
		return ''
		
	def decompress (self, value):
		return []
		
	def format_output (self, rendered, name, attrs):
		attrs.setdefault ('class', 'new-password')
		return super (NewPasswordField, self).format_output (rendered, name, attrs)
		
