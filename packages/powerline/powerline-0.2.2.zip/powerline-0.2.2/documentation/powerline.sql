CREATE TABLE users (
	username VARCHAR(255) PRIMARY KEY,
	allowed_after DATE NOT NULL DEFAULT '1970-01-01' -- For banning and barring
);

CREATE TABLE systems (
	name VARCHAR(255) PRIMARY KEY, -- The internal name; used by the client
	title VARCHAR(255) NOT NULL -- The title of the system; what is actually displayed
);

CREATE TABLE settings (
	name VARCHAR(255) PRIMARY KEY,
	value VARCHAR(255),
	description VARCHAR(255),
	type VARCHAR(255) -- See powerline/manager.py for a list of valid types
);
INSERT INTO settings VALUES ('session_time', '35', 'Time in minutes that a session can last', 'int';
INSERT INTO settings VALUES ('overrides', 'override', 'Override codes', 'list');
INSERT INTO settings VALUES ('hours', '00:00-00:00,00:00-00:00,00:00-00:00,00:00-00:00,00:00-00:00,00:00-00:00,00:00-00:00', 'Opening and closing times, starting on Sunday', 'list');
INSERT INTO settings VALUES ('sessions_per_user', '4', 'Sessions per user per day', 'int');
INSERT INTO settings VALUES ('manager_users', 'admin:', 'Users that can access the management interface', 'list');
INSERT INTO settings VALUES ('session_expire_time', '5', 'Session expiration time, when a line exists', 'int');
INSERT INTO settings VALUES ('reservation_entry_prefill', '', 'The first common digits on all cards; this will be put in the barcode box on the main page', 'none');

-- The session log.
-- Note that this contains all sessions, including unstarted and ended ones.
CREATE TABLE sessions (
	session_id INTEGER PRIMARY KEY AUTO_INCREMENT,
	daily_id INTEGER NOT NULL, -- An id number with a sequence that restarts daily.
	user VARCHAR(255) NOT NULL,
	system VARCHAR(255),
	start_time DATETIME,
	end_time DATETIME,
	timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
