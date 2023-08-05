##########################################################################
#    Copyright (C) 2007 William Waites <ww@styx.org>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as
#    published by the Free Software Foundation; either version 2 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public
#    License along with this program; if not, write to the
#    Free Software Foundation, Inc.,
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
##########################################################################

"""
###
### This is an example usage of the MetaOptions class to implement
### Comma Separated Value rendering of arbitrary django objects.
###
### To support this behaviour in your models it suffices to decorate
### the model with a CSV metaclass that has "separator" and "format"
### class attributes. "separator" is usually a character such as ";"
### or ",". Format is a list of two-tuples, the method or attribute
### from which to fetch the value on each instance, and the name to
### give this column in the CSV header. The django convention of using
### two underscores, "__" in order to reference values on related 
### objects is supported.
###
### Example:
###
### from django.db import models
### from django.contrib.options import MetaOptions
### 
### class ExampleNamedObject(models.Model):
### 	class CSV(MetaOptions):
### 		separator = ';'
### 		format = (
### 			('name', 'Name'),
### 			('describe', 'Description'),
### 		)
### 	name = models.CharField(maxlength=32)
### 	def describe(self):
### 		return str(self)
### 
### from django.contrib.options.csv import csv
### for row in csv(ExampleNamedObject):
### 	print row
###
"""

__all__ = ['Unimplemented', 'csv', 'csv_view']

class Unimplemented(Exception):
	"""CSV rendering unimplemented"""

def getattr_anyhow(obj, attr):
	"""
	Utility function to get the named attribute from the object,
	if the attribute is a callable, call it, and follow references
	using the django "__" convention.
	"""
        parts = attr.split('__')
        cur = obj
        for part in parts:
                cur = getattr(cur, part)
                if callable(cur):
                        cur = cur()
        return cur
	
def _clean(val):
	"""
	Utility function to clean and quote the value for rendering as CSV
	"""
	from datetime import datetime, date, time
	from decimal import Decimal
	if isinstance(val, datetime):
		val = val.strftime('%Y-%m-%d %H:%M:%S')
	elif isinstance(val, date):
		val = val.strftime('%Y-%m-%d')
	elif isinstance(val, time):
		val = val.strftime('%H:%M:%S')
	elif isinstance(val, Decimal) or isinstance(val, float):
		val = "%.04f" % (val,)
	elif isinstance(val, int):
		val = str(val)
	else:
		val = '"%s"' % (str(val).replace('"', "'"),)
	return val

def csv(model, where = [], tables = [], **kw):
	"""
	Return a generator of rows in a CSV file, terminated with "\r\n".
	"where" and/or "tables" are passed to the model's manager's extra
	method after any filters present in "kw" are applied.
	"""
	if not hasattr(model._meta, 'csv') or not hasattr(model._meta.csv, 'format'):
		raise Unimplemented("%s has missing or incomplete CSV options class" % (model,))
	
	separator = model._meta.csv.separator
	format = model._meta.csv.format

	manager = model.objects
	if kw:
		manager = manager.filter(**kw)
	if where or tables:
		manager = manager.extra(where = where, tables = tables)

	yield separator.join(map(lambda x: str(x[1]), format)) + '\r\n'
	for obj in manager.all():
		row = map(lambda x: _clean(getattr_anyhow(obj, x[0])), format)
		yield separator.join(row) + '\r\n'

from django.contrib.admin.views.decorators import staff_member_required
@staff_member_required
def csv_view(request, app_label, model_name):
	"""
	Generic CSV View that can be enabled in the django admin, by adding
	the following to your urls.py:

	(r'^admin/([^/]+)/([^/]+)/csv/', 'django.contrib.options.csv.csv_view')

	Results are then filtered according to the supplied GET string.
	"""
	from django.http import Http404, HttpResponse
	from django.db.models.loading import get_model

	model = get_model(app_label, model_name)
	if not model:
		raise Http404("No such model %s.%s" % (app_label, model_name))

        response = HttpResponse(csv(model, **request.GET), mimetype="text/csv")
        response['Content-Disposition'] = "attachment; filename=%s.%s.csv" % (app_label, model_name)
        return response
