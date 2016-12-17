import MySQLdb, sys

import ProduceError as PE

class DataBase:
	def __init__(self,master):
		self.USER = ''
		self.DBSE = ''
		self.HOST = ''
		self.PWRD = ''
		self.master = master
		if self.HOST and self.DBSE and self.USER and self.PWRD:
			try:
				self.cursor = None
				self.dbconn = MySQLdb.connect(self.HOST,self.USER,self.PWRD,self.DBSE)
			except MySQLdb.Error, e:
				msg = e + "\nFailed to connect locally. Searching Globally"
				self.HOST = "138.229.134.128"
				self.print_error(msg)
				self.dbconn = None
				#sys.exit(-1)
		else:
			self.cursor = None
			self.dbconn = None
	
	def refresh_connection(self):
		try:
			self.close_db()
			self.cursor = None
			self.dbconn = MySQLdb.connect(self.HOST,self.USER,self.PWRD,self.DBSE)
		except:
			print 'failed to refresh'
			self.dbconn = None
	
	def reset_cursor(self):
		if self.cursor:
			self.cursor.close()
		self.cursor = self.dbconn.cursor()
	
	def executeSQL(self, sql, cmds=None):
		if self.dbconn:
			if cmds:
				try:
					self.reset_cursor()
					if not sql.startswith('select'):
						self.log_all_updates(sql,cmds)
					if self.cursor.execute(sql,cmds):
						return True
					return False
				except:
					self.refresh_connection()
					try:
						self.reset_cursor()
						if not sql.startswith('select'):
							self.log_all_updates(sql,cmds)
						if self.cursor.execute(sql,cmds):
							return True
						return False
					except MySQLdb.Error, e:
						print "Failed to execute with commands."
						self.print_error(e)
						#sys.exit(-1)
			else:
				try:
					self.reset_cursor()
					if not sql.startswith('select'):
						self.log_all_updates(sql)
					if self.cursor.execute(sql):
						return True
					return False
				except:
					self.refresh_connection()
					try:
						self.reset_cursor()
						if not sql.startswith('select'):
							self.log_all_updates(sql)
						if self.cursor.execute(sql):
							return True
						return False
					except MySQLdb.Error, e:
						print "Failed to execute with no commands."
						self.print_error(e)
						#sys.exit(-1)
	
	def fetchColumnNames(self):
		return [i for i in self.cursor.description]
	
	def fetchAliases(self,table):
		cur = self.dbconn.cursor()
		cur.execute("select fld,alias from property_aliases where table_name = %s order by in_order ASC", [table])
		return cur.fetchall()
		
	def fetchalldata(self):
		return self.cursor.fetchall()
	
	def printallresults(self):
		rows = self.cursor.fetchall()
		for row in rows:
			print row
			print "\n"
		return
	
	def describe_table(self,table):
		cur = self.dbconn.cursor()
		cur.execute('describe %s' % table)
		return cur.fetchall()
		
	def return_primary_key(self,table):
		cur = self.dbconn.cursor()
		cur.execute("SHOW KEYS FROM %s WHERE Key_name = 'PRIMARY'" % table)
		return cur.fetchall()[0][4]
		
	def log_all_updates(self,q,cmds=None):
		try:
			try:
				query = q % cmds
			except:
				query = q
			self.dbconn.cursor().execute("insert into property_log (sql_statement,date_time,user) values (%s,NOW(),%s)" , (query,self.USER))
		except:
			print 'Failed to log entry: %s' % q
		return
	
	def exists(self):
		return self.dbconn
	
	def close_db(self):
		#print 'db %s' % self.dbconn
		if self.dbconn:
			self.dbconn.close()

	def print_error(self,e):
		PE.produce_error_popup(self.master,"MySQL Error [%d]\n%s" % (e.args[0], e.args[1]))