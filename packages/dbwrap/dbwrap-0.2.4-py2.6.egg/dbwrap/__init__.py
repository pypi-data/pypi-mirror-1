# dbwrap - Simple convenience methods for Python DB-API 2.0 connections
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
#

from cStringIO import StringIO

__all__ = ['bag', 'rows_ref', 'table_ref', 'wrapper']
__version__ = '0.2.4'

class bag(dict):
	"""A simple dict-derived class that allows bag.key and bag['key']"""
	def __getattr__(self, key):
		try:
			return self[key]
		except KeyError:
			raise AttributeError

	def __setattr__(self, key, value):
		self[key] = value
	
	def __delattr__(self, key):
		del self[key]
	
	def __reduce__(self):
		return (bag, (dict(self),))

class rows_ref(object):
	"""A lazy reference to a set of rows.

	Again, this should not be instantiated by hand; use table.rows(...)
	"""
	def __init__(self, con, table, where_clause, args):
		self.con, self.table, self.where_clause, self.args = con, table, where_clause, args
	
	def _set_clause(self, **kwargs):
		return ', '.join('%s = %s' % (column, self.con.placeholder) for column in kwargs.keys())

	def select(self, *args):
		"""Returns all rows in this rows_ref. If arguments are given, they are the columns selected."""
		return self.con.query('SELECT %s FROM %s WHERE %s' % (
				', '.join(args) if args else '*',
				self.table.name,
				self.where_clause,
			),
			*self.args
		)
	
	def select_one(self, *args):
		"""Returns the first row in this rows_ref. If arguments are given, they are the columns selected."""
		return self.con.query_one('SELECT %s FROM %s WHERE %s' % (
				', '.join(args) if args else '*',
				self.table.name,
				self.where_clause,
			),
			*self.args
		)

	def select_column(self, column):
		"""Returns the values in the specified column as a list."""
		results = self.con.query('SELECT %s FROM %s WHERE %s' % (
				column,
				self.table.name,
				self.where_clause,
			),
			*self.args
		)

		if not results:
			return []

		return [row[column] for row in result]

	def select_value(self, column):
		"""Returns the value in the specified column."""
		result = self.con.query_one('SELECT %s FROM %s WHERE %s' % (
				column,
				self.table.name,
				self.where_clause,
			),
			*self.args
		)

		if not result:
			return None

		return result[column]

	def update(self, _clause = '', *args, **values):
		"""Updates rows in this rows_ref.
		
		Note: this uses similar arguments to table.select()"""
		self.con.execute('UPDATE %s SET %s WHERE %s' % (
				self.table.name,
				_clause if _clause else self._set_clause(**values),
				self.where_clause),
			*((args if _clause else tuple(values.values())) + tuple(self.args))
		)

	def delete(self):
		"""Deletes all rows in this rows_ref"""
		self.con.execute('DELETE FROM %s WHERE %s' % (self.table.name, self.where_clause), *self.args)
	
	def exist(self):
		"""Returns whether this is an empty set"""
		return self.table.select_one(self.where_clause, *self.args) != None
	
class table_ref(object):
	"""A reference to a table.

	Note that you shouldn't instantiate this yourself; use wrapper['table-name'] or wrapper.table_name instead.
	"""

	def __init__(self, con, name):
		self.con, self.name = con, name
	
	def _where_clause(self, *args, **criteria):
		return ' AND '.join(('%s = ' + ('%' + self.con.placeholder if self.con.placeholder.startswith('%') else self.con.placeholder) if value is not None else '%s IS NULL') % column for column, value in zip(criteria.keys(), args or criteria.values()))

	def _create_clause(self, _query, args, criteria):
		return _query if _query else self._where_clause(*args, **criteria)

	def insert(self, _columns = [], _clause = '', *args, **values):
		"""INSERTs a row into the table.

		If columns and _clause are given, they will be placed into the SQL statement; otherwise, the columns and VALUES will be automatically generated.
		Note that columns _must_ be given if clause is.
		"""

		self.con.execute('INSERT INTO %s(%s) %s' % (self.name, ', '.join(_columns if _columns else values.keys()), _clause if _clause else 'VALUES(%s)' % ', '.join([self.con.placeholder] * len(args if args else values))), *(values.values() if values else args))

	def all(self):
		"""Returns the whole table"""

		return self.con.query('SELECT * FROM %s' % self.name)

	def select(self, _query = '', *args, **criteria):
		"""SELECTs from the table.

		If _query is specified, it will be used as the where clause; otherwise, one will be generated from the keyword arguments.
		"""

		return self.rows(_query, *args, **criteria).select()

	def select_one(self, _query = '', *args, **criteria):
		"""SELECTs from the table.

		If _query is specified, it will be used as the where clause; otherwise, one will be generated from the keyword arguments.
		"""
		return self.rows(_query, *args, **criteria).select_one()

	def rows(self, _query = '', *args, **criteria):
		"""Returns a rows_ref object; uses same arguments as select()."""
		return rows_ref(self.con, self, self._create_clause(_query, args, criteria), (args if _query else tuple(x for x in criteria.values() if x is not None)))

class wrapper(object):
	"""A wrapper for a DB-API connection. You MUST specify the placeholder for parameters in the call to __init__; this is ? for most libraries and %s for MySQLdb.

	If models is specified, it must be a dict of classes that dbwrap will use instead of table_ref for those tables. Notes:
		* The class must take a single argument, which is a reference to the parent wrapper.
		* The class is only instantiated once per wrapper, and cached thereafter.

	NOTE: If your table names are not valid Python identifiers, use wrapper['table-name'].
	"""
	def __init__(self, con, placeholder, models = None, debug = False):
		self.con, self.debug = con, debug
		self.placeholder = placeholder
		self.models = models or {}
		self._created_models = {}
	
	def __getattr__(self, key):
		"""Returns a table object"""

		if key in self.__dict__:
			return self.__dict__[key]
		elif key in self.models:
			return self._created_models[key] if key in self._created_models else self._created_models.setdefault(key, self.models[key](self))
		else:
			 return table_ref(self, key)

	def commit(self):
		"""Commits the transaction"""
		self.con.commit()

	def execute(self, query, *args):
		"""Runs self.con.cursor().execute(query, *args), and returns the cursor"""

		if self.debug: print query, args

		cur = self.con.cursor()
		cur.execute(query, args)
		return cur

	def execute_script(self, script):
		"""Execute the SQL in `script` (can be a fileobj or string)"""
		if isinstance(script, basestring):
			script = StringIO(script)

		while True:
			command = ''
			while not command.rstrip().endswith(';'):
				data = script.readline()
				if data == '': break

				command += data

			command = command.strip()

			if command:
				self.execute(command)
			if data == '': return

	def execute_script_file(self, filename):
		"""Runs the SQL script in 'filename'"""

		self.execute_script(file(filename, 'r'))

	def query(self, query, *args):
		"""Wrapper similar to execute for SELECT statements, that returns a list of dicts."""

		cur = None
		sets = []

		if self.debug:
			print query, args
			self.debug = False
			cur = self.execute(query, *args)
			self.debug = True
		else:
			cur = self.execute(query, *args)

		def add_result():
			results = cur.fetchall()
			if cur.description and results:
				# all SELECTs should have a description, but we shouldn't choke as the result of idiots
				columns = [desc[0] for desc in cur.description]
				sets.append([bag(zip(columns, result)) for result in results])
			else: sets.append([])

		add_result()
		while cur.nextset():
			add_result()

		return sets[0] if len(sets) == 1 else sets

	def query_one(self, query, *args):
		"""Derivative of query for one-row SELECTs."""

		cur = None

		if self.debug:
			print query, args
			self.debug = False
			cur = self.execute(query, *args)
			self.debug = True
		else:
			cur = self.execute(query, *args)

		result = cur.fetchone()
		while result is None:
			if not cur.nextset(): break
			result = cur.fetchone()
		if cur.description and result:
			columns = (desc[0] for desc in cur.description)
			return bag(zip(columns, result))
		else:
			return None

	__getitem__ = __getattr__

	def __del__(self):
		del self.con

