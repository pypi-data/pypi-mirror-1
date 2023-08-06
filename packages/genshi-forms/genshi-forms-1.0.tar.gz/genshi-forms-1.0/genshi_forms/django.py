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
from django.conf import settings

from . import fields, errors

__all__ = ['ModelField', 'MultipleModelField', 'DateField', 'TimeField']

class ModelField (fields.ChoiceField):
	def __init__ (self, queryset, **kwargs):
		choices = self._get_choices (queryset)
		super (ModelField, self).__init__ (choices = choices, **kwargs)
		self.queryset = queryset
		
	def clean (self, name, post, files):
		text = post.get (name, [''])[0]
		if not text:
			if self.required:
				error = self.error_message ('required')
				raise errors.ValidationError (error)
			else:
				return None
		try:
			return self.queryset.get (pk = text)
		except self.queryset.model.DoesNotExist:
			error = self.error_message ('invalid')
			raise errors.ValidationError (error)
			
	def render (self, name, selected, attrs):
		selected_pk = getattr (selected, 'pk', None)
		return super (ModelField, self).render (name, selected_pk, attrs)
		
	def _get_choices (self, queryset):
		yield ('', "---------")
		for obj in queryset:
			yield (obj.pk, obj)
			
class MultipleModelField (fields.MultipleChoiceField):
	def __init__ (self, queryset, **kwargs):
		choices = self._get_choices (queryset)
		super (MultipleModelField, self).__init__ (choices = choices, **kwargs)
		self.queryset = queryset
		
	def clean (self, name, post, files):
		def _clean (key):
			try:
				return self.queryset.get (pk = key)
			except self.queryset.model.DoesNotExist:
				error = self.error_message ('invalid')
				raise errors.ValidationError (error)
				
		keys = [k for k in post.get (name, []) if k]
		cleaned = map (_clean, keys)
		if self.required and not cleaned:
			error = self.error_message ('required')
			raise errors.ValidationError (error)
			
		return cleaned
		
	def render (self, name, selected, attrs):
		if selected is None:
			selected = []
		try:
			iter (selected)
		except TypeError:
			try:
				selected_all = selected.all
			except AttributeError:
				raise TypeError ("'selected' must be an iterable or manager")
			selected = selected_all ()
		selected_pks = [obj.pk for obj in selected]
		return super (MultipleModelField, self).render (name, selected_pks, attrs)
		
	def _get_choices (self, queryset):
		for obj in queryset:
			yield (obj.pk, obj)
			
class DateField (fields.DateField):
	"""A subclass of :class:`genshi_forms.fields.DateField` that pulls
	its format string from :mod:`django.conf.settings`.
	
	"""
	@property
	def format (self):
		return settings.DATE_FORMAT
		
class TimeField (fields.TimeField):
	"""A subclass of :class:`genshi_forms.fields.TimeField` that pulls
	its format string from :mod:`django.conf.settings`.
	
	"""
	@property
	def format (self):
		return settings.TIME_FORMAT
		
