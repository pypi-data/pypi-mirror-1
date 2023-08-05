# powerline.main - Main controllers and entry point
# (c) 2008 Pianohacker, licensed under the GPLv3

import cherrypy
from powerline import output, database, json, manager, xmlrpc, location
from powerline.database import user_model, system_model, session_model, settings_model, connect
import time
from sys import argv

class root(object):
	data = cherrypy.tools.staticdir.handler(section = '/data', dir = 'templates/data')

	def __init__(self):
		self.XMLRPC = xmlrpc.api()
		self.manager = manager.interface()

		cherrypy.config.update({
			'tools.sessions.on': True,
			'tools.decode.on': True,
			'tools.encode.on': True,
			'tools.staticdir.root': location,
		})

	@output.expose(template = 'index.html')
	def index(self, barcode = ''):
		"""/ - The main page. Also where reservation requests are POSTed to."""
		database = connect()
		user = user_model(database)
		session = session_model(database)
		system = system_model(database)
		settings = settings_model(database)

		yield 'reservation_entry_prefill', settings['reservation_entry_prefill']

		if cherrypy.session.get('logged-in', False):
			del cherrypy.session['logged-in']

		if not barcode:
			return

		try:
			if not user.exists(barcode):
				raise RuntimeError('User %s does not exist' % barcode)

			try:
				sessions_per_user = settings['sessions_per_user']
				if session.rows('date(timestamp) = current_date AND user = %s', barcode).select_value('count(*)') >= sessions_per_user:
					raise RuntimeError('You have already logged on %d times today' % sessions_per_user)
			except KeyError:
				pass

			session.create(user.get(barcode))
			reservation = session.get(barcode)
			reservation.update(dict(open_computers = system.get_open(), line_position = user.get_line_position(barcode), open_time = session.get_open_time()))

			yield 'error', ''
			yield 'reservation', reservation
		except RuntimeError, e:
			yield 'error', e.message
			yield 'reservation', None
			yield 'success', False

	@output.expose()
	def sessions(self):
		"""/sessions - Returns the list of sessions."""
		database = connect()

		cherrypy.response.headers['Content-Type'] = 'application/json'

		session = session_model(database)
		user = user_model(database)
		system = system_model(database)

		results = session.get_unended()
		open_computers = system.get_open()

		for i, result in enumerate(results):
			result = results[i]
			result.line_position = user.get_line_position(result.user)
			if result.line_position != 0: result.line_position = output.get_ordinal(result.line_position)
			result.timestamp = time.mktime(result.timestamp.timetuple())
			if result.end_time: result.end_time = time.mktime(result.end_time.timetuple())
			if result.start_time: result.start_time = time.mktime(result.start_time.timetuple())
			del result.user
			results[i] = dict(result)

		return {'result': results}
	
	@classmethod
	def start(klass, config_files):
		"""Starts powerline, and loads up each config file in `config_files`."""
		for config_file in config_files:
			cherrypy.config.update(config_file)

		cherrypy.quickstart(klass(), '/')


if __name__ == '__main__':
	if len(argv) == 1:
		print 'Usage: python -m powerline config_file [config_file...]'
		raise SystemExit(1)

	root.start(argv[1:])
