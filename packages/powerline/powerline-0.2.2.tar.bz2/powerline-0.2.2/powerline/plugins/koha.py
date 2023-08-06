from powerline import database
from powerline.database import user_checker
from datetime import date
import MySQLdb
import dbwrap

class koha_checker(user_checker):
	def __init__(self, connection):
		try:
			self.connection = dbwrap.wrapper(MySQLdb.connect(
					user = database.koha_user,
					host = getattr(database, 'koha_host', 'localhost'),
					passwd = database.koha_password,
					db = getattr(database, 'koha_db', 'Koha'),
					use_unicode = True, charset = 'utf8'),
				placeholder = '%s')
		except AttributeError, e:
			raise AttributeError('koha.py not configured; %s' % e)
	
	def verify(self, username):
		if not self.exists(username):
			raise KeyError(username)

		fines = self.connection.accountlines.rows('borrowernumber = (SELECT borrowernumber FROM borrowers WHERE cardnumber = %s)', username).select_value('SUM(amountoutstanding)')

		if fines:
			return False, 'You have $%.2f in fines' % fines
		else:
			return True, ''

	def exists(self, username):
		return self.connection.borrowers.rows(cardnumber = username).exist()

