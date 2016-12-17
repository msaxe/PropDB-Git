try:
	import tkinter as tk
except:
	import Tkinter as tk

import bcrypt
import MySQLdb
from getpass import getpass

import ProduceError as PE

main_bg_color = '#E0E0E0'

class Security(tk.Frame):
	global main_bg_color
	def __init__(self, master, dbconn, full_edit, main_app):
		self.master = master
		self.db = dbconn
		self.app = main_app
		
		self.frame = tk.Frame(self.master,bg=main_bg_color)
		
		# Pack Frames
		self.frame.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
		
		self._createWidgets(full_edit)
		
	def _createWidgets(self,full_edit):
		lb = tk.Label(self.frame,text="Host",bg=main_bg_color)
		lb.grid(row=0,column=0,sticky="w",padx=2)
		lb = tk.Label(self.frame,text="Database",bg=main_bg_color)
		lb.grid(row=1,column=0,sticky="w",padx=2)
		lb = tk.Label(self.frame,text="Username",bg=main_bg_color)
		lb.grid(row=2,column=0,sticky="w",padx=2)
		lb = tk.Label(self.frame,text="Password",bg=main_bg_color)
		lb.grid(row=3,column=0,sticky="w",padx=2)
		
		# Entries
		self.host_entry = tk.Entry(self.frame,width=30)
		self.host_entry.grid(row=0,column=1,columnspan=2,pady=2,padx=(2,6))
		self.dbse_entry = tk.Entry(self.frame,width=30)
		self.dbse_entry.grid(row=1,column=1,columnspan=2,pady=2,padx=(2,6))
		self.user_entry = tk.Entry(self.frame,width=30)
		self.user_entry.grid(row=2,column=1,columnspan=2,pady=2,padx=(2,6))
		self.pwrd_entry = tk.Entry(self.frame,show="*",width=30)
		self.pwrd_entry.grid(row=3,column=1,columnspan=2,pady=2,padx=(2,6))
		self.pwrd_entry.bind('<Return>',lambda e : self.save_connection(full_edit))
		
		# fill data
		if not full_edit:
			self.host_entry.insert(tk.END,self.db.HOST)
			self.dbse_entry.insert(tk.END,self.db.DBSE)
		
		# Buttons
		cancel = tk.Button(self.frame,text="Cancel",command=self.master.destroy)
		cancel.grid(row=4,column=2,pady=2,padx=2,sticky="ew")
		savecn = tk.Button(self.frame,text="Save",command=lambda : self.save_connection(full_edit))
		savecn.grid(row=4,column=1,pady=2,padx=2,sticky="ew")
		savecn.bind('<Return>',lambda : self.save_connection(full_edit))
		
	def test_connection(self):
		try:
			dbconn = MySQLdb.connect(self.host_entry.get(),self.user_entry.get(),self.pwrd_entry.get(),self.dbse_entry.get())
			dbconn.close()
			return True
		except MySQLdb.Error, e:
			print "Failed to connect to database"
			print "MySQL Error [%d]\n%s" % (e.args[0], e.args[1])
			return False
		
	def save_connection(self,full_edit):
		if self.test_connection():
			self.db.HOST = self.host_entry.get()
			self.db.DBSE = self.dbse_entry.get()
			self.db.USER = self.user_entry.get()
			self.db.PWRD = self.pwrd_entry.get()
			self.db.refresh_connection()
			self.app.clear_botframe_info()
			if full_edit:
				try:
					if self.app.mlb:
						self.app.mlb.remove()
				except:
					pass
				self.app.raise_table_buttons()
			self.master.destroy()
		else:
			failed = tk.Label(self.frame,text="Failed",fg="red",bg=main_bg_color)
			failed.grid(row=4,column=0,padx=2,sticky="ew")
		
		
		#master_secret_key = getpass('tell me the master secret key you are going to use')
		#salt = bcrypt.gensalt()
		#combo_password = raw_password + salt + master_secret_key
		#hashed_password = bcrypt.hashpw(combo_password, salt)