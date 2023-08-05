# powerline.output - Output and formatting functions
# (c) 2008 Pianohacker, licensed under the GPLv3

from functools import wraps
import types
from os import path
from genshi.template.loader import TemplateLoader
from . import json as jsonlib
import cherrypy

"""Output and formatting functions.

Functions
=========
expose is a decorator that replaces CherryPy's @expose and the x.exposed = True idiom. It renders output to a template, and performs JSON serialization of results and errors.

get_ordinal and join_list are both for string formatting. Both currently only work with English, unfortunately.

Configuration Globals
=====================

template_dir (output.template_dir): Where the templates are loaded from.
"""

template_dir = ''

def expose(template = None, method = 'xhtml', **render_kwargs):
	"""A decorator that renders the return value of its wrapped function in a template, or serializes it to a template..

	Templates are loaded from the templates directory in the directory of the module.

	The return value of the function is transformed into a variables dict for the template in the following ways:
		* If the function is a generator, it is expected to yield 'key', 'value' tuples to be fed into dict().
		* If the value is a string, it is used unmodified.
		* If the value is a dict, it is used verbatim.
		* Anything else is an error.
		* If 'destination' is in the result dict, a redirect is fired with that value.
		* `method` and **render_kwargs are both passed to Genshi's render.

	If this is an XMLHttpRequest, it is serialized to JSON as follows:
		* A dict is directly serialized, with 'success': True added if not present.
		* Anything else is placed into a dict like {'result': result, 'success': True}
		* If an error occurs, it is serialized to {'success': False, 'error_type': type(e).__name__, 'error': str(e).
	"""

	def decorator(func):
		loader = None
		if not path.exists(template_dir):
			cherrypy.log('Template directory not valid')
			raise SystemExit(1)

		loader = TemplateLoader(template_dir, auto_reload = True)

		@wraps(func)
		def wrapper(*args, **kwargs):
			try: 
				result = func(*args, **kwargs)

				if isinstance(result, types.GeneratorType):
					result = dict(result)

				if cherrypy.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
					if isinstance(result, dict):
						if 'destination' in result:
							del result['destination']

						result.setdefault('success', True)
						return jsonlib.write(result)
					else:
						return jsonlib.write({'success': True, 'result': result})

				if isinstance(result, basestring):
					return result
				elif isinstance(result, dict):
					if 'destination' in result:
						raise cherrypy.HTTPRedirect(result['destination'])

					if template is None:
						return loader.load('dump.html').generate(result=result).render(method, **render_kwargs)
					else:
						return loader.load(template).generate(**result).render(method, **render_kwargs)
				else:
					raise ValueError(result)
			except Exception, e:
				if cherrypy.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
					if type(e) is cherrypy.HTTPRedirect:
						return {'success': True}

					if isinstance(e, cherrypy.HTTPError):
						cherrypy.response.status = e.status, ''

					return jsonlib.write({'success': False, 'error_type': type(e).__name__, 'error': str(e)})
				else:
					raise

		wrapper.exposed = True

		return wrapper
	
	return decorator

def require_login(login_page = '/manager/login'):
	"""A tool that requires a logged-in session for access; `login_page` is where it redirects to."""
	if not cherrypy.session.get('logged-in', False):
		raise cherrypy.HTTPRedirect(login_page + '?original_page=' + cherrypy.request.app.script_name + cherrypy.request.path_info)

cherrypy.tools.require_login = cherrypy.Tool('before_handler', require_login, priority = 70)

def get_ordinal(num):
	# FIXME: Port this to PyICU
	# Copied from http://vandahm.org/2006/10/03/cool-python-function/
	"""Transforms a number into its ordinal equivalent.

	>>> get_ordinal(1), get_ordinal(2), get_ordinal(3), get_ordinal(4)
	('1st', '2nd', '3rd', '4th')
	>>> get_ordinal(11), get_ordinal(21), get_ordinal(50002)
	('11th', '21st', '50002nd')
	"""
	
	special_suffixes = { '1': 'st', '2': 'nd', '3': 'rd' }
	default_return = 'th'

	digits = str(abs(num)) # To work with negative numbers
	last_digit = digits[-1:]

	if last_digit in special_suffixes.keys():
		# Numbers that end in 11, 12, and 13 just get 'th'
		if len(digits) == 1 or digits[-2] != '1':
			default_return = special_suffixes[last_digit]

	return str(num) + default_return

def join_list(list_, conjunction = 'or'):
	#FIXME: Port this to PyICU if possible
	"""Joins a list together in a readable form.

	>>> join_list(['a', 'b', 'c'])
	'a, b or c'
	>>> join_list(['a', 'b'])
	'a or b'
	>>> join_list(['a', 'b', 'c'], 'and')
	'a, b and c'
	"""

	if len(list_) == 0 or len(list_) == 1:
		return str(list_)
	elif len(list_) == 2:
		return (' %s ' % conjunction).join(list_)
	else:
		return ', '.join(list_[:-1]) + (' %s ' % conjunction) + list_[-1]
