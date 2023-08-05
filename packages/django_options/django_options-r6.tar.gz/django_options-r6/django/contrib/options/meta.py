############################################################################
#    Copyright (C) 2007 by William Waites <ww@styx.org>                    #
#                                                                          #
#    This program is free software; you can redistribute it and/or modify  #
#    it under the terms of the GNU General Public License as               #
#    published by the Free Software Foundation; either version 2 of the    #
#    License, or (at your option) any later version.                       #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public             #
#    License along with this program; if not, write to the                 #
#    Free Software Foundation, Inc.,                                       #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
############################################################################

__all__ = ['MetaOptions']

class MetaOptions:
	"""
	>>> from django.db import models
	>>> class Test(models.Model):
	...     class TestOptions(MetaOptions):
	...         something = 'this'
	...         a_list = (1,2,3)
        ...
	>>> print Test._meta.testoptions.something
	this
	>>> print Test._meta.testoptions.a_list
	(1, 2, 3)
	>>>
	"""
	def _contribute_to_class(opt, cls, name):
		from django.db.models.fields import FieldDoesNotExist
		class _MetaOptions(object):
			def __init__(self, name, kw):
				self.__dict__ = kw
			def __str__(self):
				return '%sOptions(%s)' % (name, cls)
		options = {}
		for attr in dir(opt):
			if attr[0] != '_' and attr != 'contribute_to_class':
				options[attr] = getattr(opt, attr)
		options = _MetaOptions(name, options)
		setattr(cls._meta, name.lower(), options)
		return options
	contribute_to_class = classmethod(_contribute_to_class)
	_contribute_to_class = staticmethod(_contribute_to_class)

	@staticmethod
	def setdefault(cls, options, key, value):
		"""
		Used by subclasses, to set default values onto cls if they are
		not otherwise specified either in the options or in the class
		definition itself. Typically as in,

		class MyOptions(MetaOptions):
			def _contribute_to_class(opt, cls, name):
				options = MetaOptions._contribute_to_class(opt, cls, name)
				opt.setdefault(cls, options, 'myvar', 'default value')
				return options
			contribute_to_class = classmethod(_contribute_to_class)
			_contribute_to_class = staticmethod(_contribute_to_class)
		"""
		from django.db.models.fields import FieldDoesNotExist
		if hasattr(options, key) or hasattr(cls, key):
			return
		try: cls._meta.get_field(key)
		except FieldDoesNotExist:
			cls.add_to_class(key, value)
