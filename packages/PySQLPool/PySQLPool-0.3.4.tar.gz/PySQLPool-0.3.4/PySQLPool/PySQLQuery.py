"""
@author: Nick Verbeck
@since: date 5/12/2008
"""

import time
import MySQLdb
from PySQLPool import PySQLPool
import os.path

logging_path = None

class PySQLQuery(object):
	"""
	Front-End class used for interaction with the PySQLPool core
	
	This class is used to execute queries and to request a currently open connection from the pool. 
	If no open connections exist a new one is created by the pool.
	
	@author: Nick Verbeck
	@since: 5/12/2008
	@version: 0.1
	"""
	
	def __init__(self, PySQLConnectionObj, commitOnEnd = False):
		"""
		Constructor for PySQLQuery Class
		
		@param PySQLConnectionObj: PySQLConnection Object representing your connection string
		@param commitOnEnd: Default False, When query is complete do you wish to auto commit. This is a one time auto commit
		@author: Nick Verbeck
		@since: 5/12/2008
		"""
		self.Pool = PySQLPool()
		self.connInfo = PySQLConnectionObj
		self.commitOnEnd = commitOnEnd
		self.record = {}
		self.rowcount = 0
		self.affectedRows = 0
		self.conn = None
		self.lastError = None
		self.lastInsertID = None
		
	def __del__(self):
		"""
		On destruct make sure the current connection is returned back to the pool for use later
		
		@author: Nick Verbeck
		@since: 5/12/2008
		"""
		if self.conn is not None:
			self.Pool.returnConnection(self.conn)
		
	def Query(self, query, *args):
		"""
		Execute the passed in query against the database
		
		@param query: MySQL Query to execute. %s or %(key)s will be replaced by parameter args sequence
		@param args: Sequence of value to replace in your query. A mapping may also be used but your query must use %(key)s
		@author: Nick Verbeck
		@since: 5/12/2008
		"""
		
		self.lastError = None
		cursor = None
		
		if logging_path is not None:
			try:
				file = os.path.join(logging_path, 'PySQLPool.Query.log')
				fp = open(file, 'a+')
				fp.write("=== Query ===\n")
				fp.write(str(query)+"\n")
				fp.write("=== Args ===\n")
				fp.write(str(args)+"\n")
				fp.close()
			except Exception, e:
				pass
		
		try:
			self._GetConnection()
			
			self.conn.query = query
			
			#Execute query and store results
			cursor = self.conn.connection.cursor(MySQLdb.cursors.DictCursor)
			self.affectedRows = cursor.execute(query, *args)
			self.lastInsertID = self.conn.connection.insert_id()
			self.rowcount = cursor.rowcount
			
			self.record = cursor.fetchall()
			self.conn.updateCheckTime()
			
			if logging_path is not None:
				try:
					file = os.path.join(logging_path, 'PySQLPool.Query.log')
					fp = open(file, 'a+')
					fp.write("=== Affected Rows ===\n")
					fp.write(str(self.affectedRows)+"\n")
					fp.write("=== Row Count ===\n")
					fp.write(str(self.rowcount)+"\n")
					fp.close()
				except Exception, e:
					pass
		except Exception, e:
			self.lastError = e
			self.affectedRows = None
			if logging_path is not None:
				try:
					file = os.path.join(logging_path, 'PySQLPool.Query.log')
					fp = open(file, 'a+')
					fp.write("=== Error ===\n")
					fp.write(str(e.message)+"\n")
					fp.close()
				except Exception, e:
					pass
		finally:
			if cursor is not None:
				cursor.close()
			self._ReturnConnection()
			if self.lastError is not None:
				raise self.lastError
			else:
				return self.affectedRows
		
	def QueryOne(self, query, *args):
		"""
		Execute the passed in query against the database. 
		Uses a Generator & fetchone to reduce your process memory size.
		
		@param query: MySQL Query to execute. %s or %(key)s will be replaced by parameter args sequence
		@param args: Sequence of value to replace in your query. A mapping may also be used but your query must use %(key)s
		@author: Nick Verbeck
		@since: 5/12/2008
		"""
		
		self.lastError = None
		cursor = None
		try:
			self._GetConnection()
			self.conn.query = query
			#Execute query
			cursor = self.conn.connection.cursor(MySQLdb.cursors.DictCursor)
			self.affectedRows = cursor.execute(query, *args)
			self.conn.updateCheckTime()
			while 1:
				row = cursor.fetchone()
				if row is None:
					break
				else:
					self.record = row
					yield row
					
			self.rowcount = cursor.rowcount
		except Exception, e:
			self.lastError = e
			self.affectedRows = None
		finally:
			if cursor is not None:
				cursor.close()
			self._ReturnConnection()
			if self.lastError is not None:
				raise self.lastError
			else:
				raise StopIteration
			
	def executeMany(self, query, args):
		"""
		Executes a series of the same Insert Statments
		
		Each tuple in the args list will be applied to the query and executed.
		This is the equivilant of MySQLDB.cursor.executemany()
		
		@author: Nick Verbeck
		@since: 9/7/2008
		"""
		self.lastError = None
		self.affectedRows = None
		self.rowcount = None
		self.record = None
		cursor = None
		
		try:
			self._GetConnection()
			self.conn.query = query
			#Execute query and store results
			cursor = self.conn.connection.cursor(MySQLdb.cursors.DictCursor)
			cursor.executemany(query, args)
			self.conn.updateCheckTime()
		except Exception, e:
			self.lastError = e
		finally:
			if cursor is not None:
				cursor.close()
			self._ReturnConnection()
			if self.lastError is not None:
				raise self.lastError
			
	def executeMulti(self, queries):
		"""
		Execute a series of Deletes,Inserts, & Updates in the Queires List
		
		@author: Nick Verbeck
		@since: 9/7/2008
		"""
		self.lastError = None
		self.affectedRows = 0
		self.rowcount = None
		self.record = None
		cursor = None
		
		try:
			self._GetConnection()
			#Execute query and store results
			cursor = self.conn.connection.cursor(MySQLdb.cursors.DictCursor)
			for query in queries:
				self.conn.query = query
				if query.__class__ == [].__class__:
					self.affectedRows += cursor.execute(query[0], query[1])
				else:
					self.affectedRows += cursor.execute(query)
			self.conn.updateCheckTime()
		except Exception, e:
			self.lastError = e
		finally:
			if cursor is not None:
				cursor.close()
			self._ReturnConnection()
			if self.lastError is not None:
				raise self.lastError
	
	def _GetConnection(self):
		"""
		Retieves a prelocked connection from the Pool
		
		@author: Nick Verbeck
		@since: 9/7/2008
		"""
		#Attempt to get a connection. If all connections are in use and we have reached the max number of connections,
		#we wait 1 second and try again.
		while self.conn is None:
			self.conn = self.Pool.GetConnection(self.connInfo)
			if self.conn is not None:
				break
			else:
				time.sleep(1)
				
		#Acquire Connection Lock to be thread safe
		self.conn.lock.acquire()
		
		#Test if connection is still active. If not reconnect.
		if self.conn.TestConnection() is False:
			self.conn.ReConnect()
			
	def _ReturnConnection(self):
		"""
		Returns a connection back to the pool
		
		@author: Nick Verbeck
		@since: 9/7/2008
		"""
		if self.conn is not None:
			if self.connInfo.commitOnEnd is True or self.commitOnEnd is True:
				self.conn.Commit()
					
			self.Pool.returnConnection(self.conn)
			self.conn.lock.release()
			self.conn = None
			
	def escape_string(self, string):
		"""
		Escapes a string for use in a query
		
		This is the equivilate and MySQLdb.escape_string()
		
		@author: Nick Verbeck
		@since: 9/7/2008
		"""
		return MySQLdb.escape_string(string)
	
	def escape(self, string):
		"""
		Escapes a string for use in a query
		
		This is the equivilate and MySQLdb.escape()
		
		@author: Nick Verbeck
		@since: 9/7/2008
		"""
		return MySQLdb.escape(string)