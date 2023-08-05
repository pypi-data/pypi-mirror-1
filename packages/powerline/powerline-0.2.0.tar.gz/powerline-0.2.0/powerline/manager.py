# powerline.manager - Management interface
# (c) 2008 Pianohacker, licensed under the GPLv3

import cherrypy
from powerline import output
from powerline.database import user_model, settings_model, system_model, session_model, hours_model, connect
from datetime import datetime

class user_controller(object):
	@output.expose(template = 'manager/users.html')
	def index(self, **kwargs):
		"""/manager/users/ - User management.

		GET - Returns the main page.
		POST - Creates a user (username parameter).
		"""
		database = connect()
		user = user_model(database)

		if cherrypy.request.method == 'POST':
			user.create(kwargs['username'])
			raise cherrypy.HTTPRedirect('/manager/users/')
		else:
			return {}

	@output.expose(template = 'manager/user.html')
	def default(self, user_id, **kwargs):
		"""/manager/users/<user_id> - Manage a particular user.

		GET - Returns details on a user.
		PUT - Creates a user.
		DELETE - Deletes a user.
		POST - Modifies a user.
		"""
		database = connect()
		user = user_model(database)
		method = ''

		if 'method' in kwargs:
			method = kwargs['method']
		else:
			method = cherrypy.request.method

		if method == 'GET':
			if user.exists(user_id):
				return user.get(user_id)
			else:
				raise cherrypy.NotFound()
		elif method == 'PUT':
			if not user.exists(user_id):
				user.create(user_id)
			raise cherrypy.HTTPRedirect('/manager/users/' + user_id)
		elif method == 'DELETE':
			user.delete(user_id)
			raise cherrypy.HTTPRedirect('/manager/users/')
		elif method == 'POST':
			if not user.exists(user_id):
				raise cherrypy.NotFound()

			if 'barred' in kwargs:
				user.ban(user_id) if int(kwargs['barred']) else user.ban(user_id, '1970-01-01')
			elif 'ban_until' in kwargs:
				user.ban(user_id, datetime.strptime(kwargs['ban_until'], '%m/%d/%Y').strftime('%Y-%m-%d'))

			raise cherrypy.HTTPRedirect('/manager/users/' + user_id)

	@output.expose(template = 'manager/user-search.html')
	def search(self, query):
		"""/manager/users/search - Search names of users.

		Takes a single argument of `query`, which is search for anywhere in the username of a user.
		"""
		database = connect()
		user = user_model(database)

		yield 'query', query
		yield 'users', user.select('username LIKE %s', '%' + query + '%')

class settings_controller(object):
	@output.expose(template = 'manager/settings.html')
	def index(self, key = '', value = '', type = '', description = ''):
		"""/manager/settings/ - Manage settings.

		POST - Takes arguments `key`, `value`, `type`, and `description`, and creates or modifies setting `name` accordingly.
		"""
		database = connect()
		settings = settings_model(database)

		if cherrypy.request.method == 'POST':
			if key in settings:
				settings[key] = value
			else:
				settings.insert(name = key, value = value, type = type, description = description)
				database.commit()

			raise cherrypy.HTTPRedirect('/manager/settings/')
		else:
			yield 'settings', settings.all()
			yield 'setting_types', settings.types.keys()

class hours_controller(object):
	@output.expose(template = 'manager/hours.html')
	def index(self, **kwargs):
		"""/manager/hours/ - Manage hours.

		GET - Returns current hours.
		POST - Modifies hours, based on arguments of the form <weekday>_(open|close)time, e.g., 0_opentime or 6_closetime.
		"""
		database = connect()
		hours = hours_model(database)
		current_hours = hours.all()

		if cherrypy.request.method == 'POST':
			for i in xrange(7):
				sent_properties = dict((key[2:], value) for key, value in kwargs.items() if key.startswith(str(i)))
				if sent_properties != {}:
					current_hours[i] = (datetime.strptime(sent_properties['opentime'], '%I:%M %p').time(), datetime.strptime(sent_properties['closetime'], '%I:%M %p').time())

			hours.update(current_hours)

			raise cherrypy.HTTPRedirect('/manager/hours/')
		else:
			yield 'hours', current_hours

class system_controller(object):
	"""Systems management"""
	@output.expose(template = 'manager/systems.html')
	def index(self, name = '', title = '', method = ''):
		"""/manager/systems/ - Manage systems.

		POST - Takes an argument of name and title, and creates a system with those properties.
		DELETE - Deletes the system with `name`.
		"""
		database = connect()
		system = system_model(database)

		if not method:
			method = cherrypy.request.method
	
		if method == 'POST':
			if not title:
				return 'Systems must be given a title'
			if system.exists(name):
				system.update(name, title = title)
			else:
				system.create(name = name, title = title)

			raise cherrypy.HTTPRedirect('/manager/systems/')
		elif method == 'DELETE':
			if system.exists(name):
				system.delete(name)

			raise cherrypy.HTTPRedirect('/manager/systems/')
		else:
			return {'systems': system.all()}

class interface(object):
	def __init__(self):
		self.users = user_controller()
		self.settings = settings_controller()
		self.systems = system_controller()
		self.hours = hours_controller()

		self._cp_config = {
			'tools.require_login.on': True
		}

	@output.expose(template = 'manager/index.html')
	def index(self):
		"""/manager/ - Main manager page"""
		return {}
	
	@output.expose(template = 'manager/login-setup.html')
	def login_setup(self, username = '', password = '', confirm_password = ''):
		"""/manager/login_setup - Set up the manager username and password.
		
		GET - Returns current username.
		POST - Modifies username and/or password, based on arguments.
		"""
		database = connect()
		settings = settings_model(database)

		yield 'username', settings['manager_users'][0].split(':')[0]

		if cherrypy.request.method == 'POST':
			assert(username and password)
			if password != confirm_password:
				yield 'message', 'Passwords do not match'	
				return

			settings['manager_users'] = username + ':' + password

			raise cherrypy.HTTPRedirect('/manager/')
		else:
			yield 'message', ''
	
	@output.expose(template = 'manager/session-log.html')
	def session_log(self, session_id = None, **kwargs):
		"""/manager/session_log - A log of sessions for the day"""
		database = connect()
		session = session_model(database)

		if 'method' in kwargs:
			method = kwargs['method']
		else:
			method = cherrypy.request.method

		if method == 'GET': 
			yield 'sessions', session.select('date(timestamp) = current_date ORDER BY daily_id')
		elif method == 'DELETE':
			session_id = int(session_id)
			assert(session.exists(session_id = session_id))
			session.delete(session_id)

			raise cherrypy.HTTPRedirect('/manager/session_log')
	
	@output.expose(template = 'manager/login.html')
	def login(self, username = '', password = '', original_page = '/manager/'):
		"""/manager/login - Log in to the manager.

		GET - Returns the login page.
		POST - Checks username and password, and redirects to `original_page` if successful.
		"""
		database = connect()
		settings = settings_model(database)

		yield 'original_page', original_page

		if cherrypy.request.method == 'POST':
			if username + ':' + password in settings['manager_users']:
				cherrypy.session['logged-in'] = 'yes'
				raise cherrypy.HTTPRedirect(original_page)
			else:
				yield 'message', 'Username or password incorrect'
		else:
			yield 'message', ''
	
	@cherrypy.expose
	def logout(self):
		"""/manager/logout - Log out from the manager"""
		if cherrypy.session.get('logged-in', False):
			del cherrypy.session['logged-in']

		raise cherrypy.HTTPRedirect('/')
	
	login._cp_config = {'tools.require_login.on': False}

	@output.expose(template = 'manager/statistics.html')
	def statistics(self):
		"""/manager/statistics - Returns statistics on sessions and users"""
		database = connect()
		session = session_model(database)
		user = user_model(database)

		yield 'sessions_for_day', session.rows('date(timestamp) = current_date').select_value('count(end_time)')
		yield 'sessions_for_week', session.rows('week(timestamp) = week(current_date)').select_value('count(end_time)')
		yield 'sessions_for_month', session.rows('month(timestamp) = month(current_date)').select_value('count(end_time)')
		yield 'sessions_for_year', session.rows('year(timestamp) = year(current_date)').select_value('count(end_time)')
		yield 'sessions', session.rows('1').select_value('count(end_time)')
		yield 'registered_users', user.rows('1').select_value('count(*)')
