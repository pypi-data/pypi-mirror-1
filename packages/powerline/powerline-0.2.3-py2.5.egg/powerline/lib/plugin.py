from os import path, listdir
from cherrypy import log
import imp

class mount_point(type):
	known = set()

	def __init__(cls, name, bases, attrs):
		if hasattr(cls, '_plugins'):
			cls.add(cls)
		else:
			cls._plugins = set()
			if 'add' not in attrs:
				cls.add = classmethod(lambda cls, plugin: cls.plugins.add(plugin))
				cls.plugins = cls._plugins

			mount_point.known.add(cls)

def load(*paths):
	for path in paths:
		load_path(path)

def load_path(location):
	found = []
	for file in set([path.splitext(x)[0] for x in listdir(location) if not x.startswith('.')]):
		found += load_file(location, file)

	return found

def load_file(location, filename):
	found = []

	mod_name = path.splitext(filename)[0]
	new_mod = None

	try:
		fp, pathname, desc = imp.find_module(mod_name,[location])
		try:
			new_mod = imp.load_module(mod_name, fp, pathname, desc)
		finally:
			if fp: fp.close()
	except ImportError, err:
		log('Failed to import %s, %s' % (mod_name, err))

	if not new_mod:
		return []

	return load_module(new_mod)

def load_module(mod):
	if type(mod) is str:
		mod = _import(mod)

	objects = getattr(mod, "__all__", None) or [getattr(mod, x) for x in dir(mod)]

	return [obj for obj in objects if type(obj.__class__) in mount_point.known]
