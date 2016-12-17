import MySQLdb, os
try:
	import tkinter as tk
except:
	import Tkinter as tk
import tkFileDialog as tkf

import DataBase as DB
import MultiListBox as MLB
import ProduceError as PE
import paths

main_bg_color = '#E0E0E0'

class ViewFiles():
	global main_bg_color
	def __init__(self,master,dbconn,selection,table):
		self.master = master
		self.db = dbconn
		self.selection = selection
		self.foreign_key = selection[0]
		self.base_table = table
		self.files_table = table + '_files'
		self.del_buts = []
		
		# Create Frames
		self.frame = tk.Frame(self.master,bg=main_bg_color)
		
		# Pack Frames
		self.frame.pack(side=tk.TOP, expand=tk.YES, fill=tk.Y)
		
		row_num = self.load_table()
		if row_num > 0:
			self.load_entry( row_num )
		
		self.master.grab_set() # Forces user to interact here
		return
		
	def fetch_file_data(self):
		try:
			query = "select pkeyID,file_name,file_addr from %s where fkey = %%s and active = 'Yes'" % self.files_table
			self.db.executeSQL( query, (self.foreign_key,) ) # selection[0] refers to the primary key in the property table, which is the foreign key in the files table
			data = self.db.fetchalldata()
		except MySQLdb.Error, e:
			#PE.produce_error_popup(self.master,"MySQL Error [%d]\n%s" % (e.args[0], e.args[1]))
			PE.produce_error_frame(self.master,"%s does not allow files to be linked to it.\nPlease request the change under the 'Requests' tab." % self.base_table )
			#self.master.destroy()
			return -1
			
		return data
	
	def load_table(self):
		
		redx   = tk.PhotoImage(file=paths.resource_path(r"icons\redx.gif"))
		
		def shorten_text(s):
			if len(s) > 50:
				return s[0:8]+' ... '+s[len(s)-40:len(s)]
			return s
		
		grid_row = 0
		data = self.fetch_file_data()
		if data != -1 and len(data) > 0:
			for d in data:
				tk.Label(self.frame,text=d[1],bg=main_bg_color).grid(row=grid_row,column=0,sticky='w')
				tk.Button(self.frame,text=shorten_text(d[2]),command=lambda file_link=d[2]: self.open_file_link(file_link),bg=main_bg_color,fg='blue',relief=tk.FLAT,bd=0,anchor="w",cursor='hand1').grid(row=grid_row,column=1,sticky='we')
				rx = tk.Button(self.frame,image=redx,command=lambda obj_id=d[0],gr=grid_row: self.del_file_db(obj_id,gr),width=20,height=20,relief=tk.FLAT,bg=main_bg_color)
				self.del_buts.append(rx)
				rx.image = redx
				rx.grid(row=grid_row,column=3,sticky='w')
				grid_row += 1
		elif data != -1 and len(data) == 0:
			tk.Label(self.frame,text='No files associated with this entry',bg=main_bg_color).grid(row=grid_row,column=1)
			grid_row += 1
		return grid_row
	
	def load_entry(self,grid_row):
		gplus  = tk.PhotoImage(file=paths.resource_path(r"icons\greenplus.gif"))
		fileop = tk.PhotoImage(file=paths.resource_path(r"icons\fileopen.gif"))
		
		def get_file_loc():
			self.eloc.insert(tk.END,tkf.askopenfilename())
			self.ename.delete(0,tk.END)
			file_name = self.eloc.get().split("/")[-1]
			file_name = file_name.split(" ")[0]
			file_name = file_name.split("_")[0]
			file_name = file_name.split("-")[0]
			self.ename.insert(tk.END,file_name.split('.')[0])
			self.master.focus()
		
		self.ename = tk.Entry(self.frame)
		self.ename.insert(tk.END,'Document')
		self.ename.grid(row=grid_row,column=0,sticky='w',padx=4)
		
		self.eloc  = tk.Entry(self.frame,width=60)
		self.eloc.grid(row=grid_row,column=1,sticky='w')
		
		fo = tk.Button(self.frame,image=fileop,command=get_file_loc,width=20,height=20,relief=tk.FLAT,bg=main_bg_color)
		fo.image = fileop
		fo.grid(row=grid_row,column=2,sticky='w')
		
		gp = tk.Button(self.frame,image=gplus,command=self.add_file_db,width=20,height=20,relief=tk.FLAT,bg=main_bg_color)
		gp.image = gplus
		gp.grid(row=grid_row,column=3,sticky='w')
		
		return
	
	def add_file_db(self):
		fn = self.ename.get().replace("'","")
		fl = self.eloc.get().replace("'","''").replace("\\","/")
		if fn and fl:
			query = "insert into %s (fkey,file_name,file_addr) values (%%s,%%s,%%s)" % self.files_table
			try:
				if self.db.executeSQL(query,(self.foreign_key,fn,fl)):
					self.db.dbconn.commit()
					self.ename.delete(0,tk.END)
					self.eloc.delete(0,tk.END)
					for w in self.frame.winfo_children():
						w.destroy()
					self.frame.destroy()
					self.__init__(self.master,self.db,self.selection,self.base_table)
			except MySQLdb.Error, e:
				PE.produce_error_popup(self.master,"MySQL Error [%d]\n%s" % (e.args[0], e.args[1]))
		return
	
	def del_file_db(self,id,gridrow):
		query = "update %s set active = 'No', deleted_by = %%s, deleted_on = NOW() where pkeyID = %%s" % self.files_table
		try:
			if self.db.executeSQL(query,(self.db.USER,id)):
				self.db.dbconn.commit()
				for w in self.frame.winfo_children():
					w.destroy()
				self.frame.destroy()
				self.__init__(self.master,self.db,self.selection,self.base_table)
		except MySQLdb.Error, e:
			PE.produce_error_popup(self.master,"MySQL Error [%d]\n%s" % (e.args[0], e.args[1]))
			
	def open_file_link(self,file_link):
		try:
			os.startfile(file_link)
		except:
			PE.produce_error_popup(self.master,'Error: Invalid Link')
