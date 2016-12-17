try:
	import Tkinter as tk
except:
	import tkinter as tk
import tkFont
import tkFileDialog as tkf
import PIL.Image
import PIL.ImageTk
import os, sys, csv, MySQLdb, datetime

os.chdir(os.path.dirname(os.path.realpath(sys.argv[0])))

import MultiListBox as MLB
import SendMailNotify as SM
import DataBase as DB
import Add_Edit as AE
import ViewParcel as VP
import ViewFiles as VF
import ProduceError as PE
import ToolTip as TT
import Security as SC

main_bg_color = '#E0E0E0'
bot_info_color= '#fcfbea'

# MySQL field identifiers
field_type = {
 0: 'Decimal',
 1: 'Tiny',
 2: 'Short',
 3: 'Number',
 4: 'Float',
 5: 'Double',
 6: 'NULL',
 7: 'Timestamp',
 8: 'Longlong',
 9: 'INT24',
 10: 'Date (yyyy-mm-dd)',
 11: 'Time',
 12: 'Datetime',
 13: 'Year',
 14: 'NewDate',
 15: 'VARCHAR',
 16: 'Bit',
 246: 'Decimal',
 247: 'INTERVAL',
 248: 'SET',
 249: 'TINY_BLOB',
 250: 'MEDIUM_BLOB',
 251: 'LONG_BLOB',
 252: 'BLOB',
 253: 'String',
 254: 'Set',
 255: 'GEOMETRY' 
}

field_type1 = {
 'var': 'Text',
 'cha': 'Text',
 'int': 'Number',
 'dat': 'YYYY-MM-DD',
 'dec': 'Decimal',
 'enu': 'Yes/No or Lease/License',
}

# Main application window
class Application(tk.Frame):
	global main_bg_color
	global bot_info_color
	
	#initializes format of the windows and the layout of the frames
	def __init__(self, master=None):
		tk.Frame.__init__(self, master)
		tkFont.nametofont("TkDefaultFont").configure(size=11)
		self.master.grid()
		self.master.columnconfigure(0,weight=1)
		self.master.rowconfigure(1,weight=10)
		self.mlb = None							# varibale to reference the listboxes(table)
		self.aed_window = None					# pointer to Add/edit/delete windows
		self.vrf_window = None					# poitner to view rows files window
		
		self.db = DB.DataBase(self.master)  	# initialize a connection to the database

		self.selected_table = ""				# set the initial table to ""
		self.selected_table_pkey = ""			# set the initial pkey to ""
												# initialize table info
		self.field_names = []					# contains a list of field info as a list
		self.table_rows = []					# contains a list of lists of what is currently showing in the app table
		self.top_button_tables = []				# list of button widgets on top of application
		
		#create frames for options
		self.topframe = tk.Frame(self.master)
		self.topframe.pack(side=tk.TOP, fill=tk.X)
		self.topframe.configure(bg=main_bg_color,bd=1,relief=tk.SUNKEN)
		
		self.midframe = tk.Frame(self.master)
		self.midframe.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
		self.midframe.pack_propagate(0)
		self.midframe.configure(bg=main_bg_color,bd=3,relief=tk.SUNKEN)
		
		self.botframe = tk.Frame(self.master)
		self.botframe.pack(side=tk.TOP, fill=tk.X)
		self.botframe.configure(bg=main_bg_color,bd=1,relief=tk.SUNKEN)
		
		self.botinfoframe = tk.Frame(self.master)
		self.botinfoframe.pack(side=tk.TOP, fill=tk.X)
		self.botinfoframe.configure(bg=bot_info_color,bd=1,relief=tk.SUNKEN)
		
		self.createMenu()
		self.createWidgets()
	
		self.LnLs_flds = ['pkeyID','L_or_L','name','address','suite','city','L_L','T_L','sdate','edate','redate','monthly','comments']
		self.LnLs_table = 'property_LnLs'
		self.reserve_flds = ['pkeyID','cname','ucr_id','date_aq','landuse','book_val','area_acres']
		self.reserve_table = 'property_reserves'
		try:
			self.load_table(self.LnLs_flds,self.LnLs_table,"where active = 'Yes'", but=1)
		except:
			pass

	# creates the top menu options of the main application window
	def createMenu(self):
		self.menu = tk.Menu(self)
		self.master.config(menu=self.menu)
		filemenu = tk.Menu(self.menu, tearoff=0)
		self.menu.add_cascade(label="File", menu=filemenu)
		#filemenu.add_command(label="Send Mail Notifications", command=self.send_notify_mail_window)
		filemenu.add_separator()
		filemenu.add_command(label="Change User", command=self.edit_connection )
		filemenu.add_command(label="Change Database", command=lambda : self.edit_connection(full_edit=True))
		filemenu.add_separator()
		filemenu.add_command(label="Exit", command=self.quit)
		
		viewmenu = tk.Menu(self.menu, tearoff=0)
		self.menu.add_cascade(label="View", menu=viewmenu)
		viewmenu.add_command(label="All Contracts",		command=lambda : self.load_table("*",self.LnLs_table))
		viewmenu.add_command(label="All Reserves",			command=lambda : self.load_table("*",self.reserve_table))
		viewmenu.add_command(label="Inactive Leases",		command=lambda : self.load_table(self.LnLs_flds,self.LnLs_table,"where active='No' and L_or_L='Lease'"))
		viewmenu.add_command(label="Inactive Licenses",	command=lambda : self.load_table(self.LnLs_flds,self.LnLs_table,"where active='No' and L_or_L='License'"))
		viewmenu.add_command(label="Inactive Reserves",	command=lambda : self.load_table(self.reserve_flds,self.reserve_table,"where active='No'"))
		
		today = datetime.date.today()
		interval = today + datetime.timedelta(days=180)		#today + 180 days
		dateQuery = "where edate < '%s' and monthly = 'No' and active = 'Yes' and (redate IS NULL or '%s' > redate)" % (interval,interval)
	
		fis_yr_str = str(today.year-1) + '-07-01'
		annualReport = "where sdate >= '%s' and active = 'Yes'" % datetime.datetime.strptime(fis_yr_str,'%Y-%m-%d')
		
		# premade reports follow format to add more
		statsmenu = tk.Menu(self.menu, tearoff=0)
		self.menu.add_cascade(label="Reports", menu=statsmenu)
		statsmenu.add_command(label="Upcoming End Dates",	command=lambda : self.load_table(self.LnLs_flds,self.LnLs_table,dateQuery,check_date=True))
		statsmenu.add_command(label="Report UCOP",			command=lambda : self.load_table(self.LnLs_flds,self.LnLs_table,"where ucop = 'Yes'"))
		statsmenu.add_command(label="Possessory Interest",	command=lambda : self.load_table(self.LnLs_flds,self.LnLs_table,"where poss_int = 'Yes'"))
		statsmenu.add_command(label="Monthly Properties",	command=lambda : self.load_table(self.LnLs_flds,self.LnLs_table,"where monthly = 'Yes'",check_date=False))
		statsmenu.add_command(label="Annual Report",		command=lambda : self.load_table(self.LnLs_flds,self.LnLs_table,annualReport,check_date=True))
		
		helpmenu = tk.Menu(self.menu, tearoff=0)
		self.menu.add_cascade(label="Requests", menu=helpmenu)
		#helpmenu.add_command(label="Help Document", command=self.open_help_document)
		helpmenu.add_command(label="Report Bug", 		command=lambda : self.send_requests_reports_window("Bug"))
		helpmenu.add_command(label="Request Change", 	command=lambda : self.send_requests_reports_window("Request"))
		
		docmenu = tk.Menu(self.menu, tearoff=0)
		self.menu.add_cascade(label="Help", menu=docmenu)
		docmenu.add_command(label="Help Document", command=lambda : self.open_help_document('V:/web_design/leases_n_liscense/AboutDocs/PropertyDB_HowTo.pptx'))
		docmenu.add_command(label="Back End Doc" , command=lambda : self.open_help_document('V:/web_design/leases_n_liscense/AboutDocs/PropertyDB_BackEnd.docx'))
		docmenu.add_command(label="Known Issues" , command=lambda : self.open_help_document('V:/web_design/leases_n_liscense/AboutDocs/PropertyDB_Fixes-Future.docx'))
		
	def createWidgets(self):
		#----------TOPFRAME----------
		allprp = tk.Button(self.topframe, text="Active Contracts")
		self.top_button_tables.append(allprp)
		allprp["command"] = lambda arg=len(self.top_button_tables): self.load_table(self.LnLs_flds,self.LnLs_table,"where active = 'Yes'", but=arg)
		allprp.pack(side=tk.LEFT,pady=(2,2),padx=(2,0))
		
		ldld = tk.Button(self.topframe, text="Leases")
		self.top_button_tables.append(ldld)
		ldld["command"] = lambda arg=len(self.top_button_tables): self.load_table(self.LnLs_flds,self.LnLs_table,"where L_or_L = 'Lease' and active='Yes'",but=arg)
		ldld.pack(side=tk.LEFT,pady=(2,2))

		lcnr = tk.Button(self.topframe, text="Licenses")
		self.top_button_tables.append(lcnr)
		lcnr["command"] = lambda arg=len(self.top_button_tables): self.load_table(self.LnLs_flds,self.LnLs_table,"where L_or_L = 'License' and active='Yes'",but=arg)
		lcnr.pack(side=tk.LEFT,pady=(2,2))
		
		#tent = tk.Button(self.topframe, text="Tenant")
		#self.top_button_tables.append(tent)
		#tent["command"] = lambda : self.load_table("select * from property_LnLs where T_L = 'UC Regents' and L_or_L = 'Lease'",but=len(self.top_button_tables))
		#tent.pack(side=tk.LEFT,pady=(2,5))
		
		#lcne = tk.Button(self.topframe, text="Licensee")
		#self.top_button_tables.append(lcne)
		#lcne["command"] = lambda : self.load_table("select * from property_LnLs where T_L = 'UC Regents' and L_or_L = 'License'",but=len(self.top_button_tables))
		#lcne.pack(side=tk.LEFT,pady=(2,5))
		
		rspr = tk.Button(self.topframe, text="Reserves")
		self.top_button_tables.append(rspr)
		rspr["command"] = lambda arg=len(self.top_button_tables): self.load_table(self.reserve_flds,self.reserve_table,"where active = 'Yes'",but=arg)
		rspr.pack(side=tk.LEFT,pady=(2,2))
		
		#gift = tk.Button(self.topframe, text="Gifts")
		#gift["command"] = lambda : self.load_table("*","property_gifts",but=7)
		#gift.pack(side=tk.LEFT,pady=(2,5))
		#self.top_button_tables.append(gift)
		
		offc = tk.Button(self.topframe, text="Off Campus")
		self.top_button_tables.append(offc)
		offc["command"] = lambda arg=len(self.top_button_tables): self.load_table(['pkeyID','apn','site_nm','use_','adr','zipcode','lot_sz','bld_sz','bld_type'],"property_offcampus","where active = 'Yes'",but=arg)
		offc.pack(side=tk.LEFT,pady=(2,2))
		
		oncp = tk.Button(self.topframe, text="Core Campus")
		self.top_button_tables.append(oncp)
		oncp["command"] = lambda arg=len(self.top_button_tables): self.load_table(['pkeyID','apn','date_aq','acres','notes'],"property_corecampus","where active = 'Yes'",but=arg)
		oncp.pack(side=tk.LEFT,pady=(2,2))
		
		# search button
		self.searchbut = tk.Button(self.topframe, text="GO")
		self.searchbut["command"] = self.search_box_load
		self.searchbut.pack(side=tk.RIGHT,padx=2,pady=(2,2))
		
		# search box
		self.searchbox = tk.Entry(self.topframe, text="Search Table...")
		self.searchbox.pack(side=tk.RIGHT)
		self.searchbox.bind('<Return>', lambda e : self.search_box_load(e))
		
		# search label
		search_label = tk.Label(self.topframe, text="Search ",bg=main_bg_color)
		search_label.pack(side=tk.RIGHT)
		
		
		#----------BOTFRAME----------
		def createToolTip(widget,text):
			toolTip = TT.ToolTip(widget)
			def enter(event):
				widget.after(600,toolTip.showtip(text))
				#toolTip.showtip(text)
			def leave(event):
				toolTip.hidetip()
			widget.bind('<Enter>', enter)
			widget.bind('<Leave>', leave)
		
		self.addplusimage = PIL.ImageTk.PhotoImage(PIL.Image.open(r".\icons\addplus_30_2.png"))
		self.addbut = tk.Button(self.botframe, image=self.addplusimage,width=30,height=30)
		self.addbut["command"] = lambda : self.aed_selected_row(add=True,to_delete=False)
		self.addbut.pack(side=tk.LEFT,pady=2,padx=(2,0))
		createToolTip(self.addbut,"Add Entry")
		
		self.editcirimage = PIL.ImageTk.PhotoImage(PIL.Image.open(r".\icons\editpenc_30.png"))
		self.edit = tk.Button(self.botframe, image=self.editcirimage,width=30,height=30)
		self.edit["command"] = lambda : self.aed_selected_row(add=False,to_delete=False)
		self.edit.pack(side=tk.LEFT,pady=2)
		createToolTip(self.edit,"Edit Entry")
		
		self.deldashimage = PIL.ImageTk.PhotoImage(PIL.Image.open(r".\icons\delex_30.png"))
		self.delb = tk.Button(self.botframe, image=self.deldashimage,width=30,height=30)
		self.delb["command"] = lambda : self.aed_selected_row(add=False,to_delete=True)
		self.delb.pack(side=tk.LEFT,pady=2)
		createToolTip(self.delb,"Delete Entry")
		
		self.exportimage = PIL.ImageTk.PhotoImage(PIL.Image.open(r".\icons\export_30_2.png"))
		self.expo = tk.Button(self.botframe, image=self.exportimage,width=30,height=30)
		self.expo["command"] = self.export_to_file
		self.expo.pack(side=tk.LEFT,pady=2)
		createToolTip(self.expo,"Export Table")
		
		#-----------BOT INFO FRAME-----------
		self.table_name_label = tk.Label(self.botinfoframe,bg=bot_info_color,bd=1,relief=tk.SUNKEN,anchor='w')
		self.table_name_label.pack(side=tk.LEFT,expand=1,fill=tk.X)

		self.rows_returned_label = tk.Label(self.botinfoframe,bg=bot_info_color,bd=1,relief=tk.SUNKEN,anchor='w')
		self.rows_returned_label.pack(side=tk.LEFT,expand=1,fill=tk.X)

		self.sels_returned_label = tk.Label(self.botinfoframe,bg=bot_info_color,bd=1,relief=tk.SUNKEN,anchor='w')
		self.sels_returned_label.pack(side=tk.LEFT,expand=1,fill=tk.X)

		self.dbcn_returned_label = tk.Label(self.botinfoframe,bg=bot_info_color,bd=1,relief=tk.SUNKEN,anchor='w')
		self.dbcn_returned_label.pack(side=tk.LEFT,expand=1,fill=tk.X)

		self.dbus_returned_label = tk.Label(self.botinfoframe,bg=bot_info_color,bd=1,relief=tk.SUNKEN,anchor='w')
		self.dbus_returned_label.pack(side=tk.LEFT,expand=1,fill=tk.X)

		return 
	
	def edit_connection(self,full_edit=False):
		if self.selected_table:
			if self.aed_window:
				self.aed_window.destroy()
			if self.vrf_window:
				self.vrf_window.destroy()
				
			self.aed_window = tk.Toplevel(self)
			self.aed_window.wm_title("Configure database connection")
			#self.aed_window.resizable(0,0)
			self.aed_window.grab_set()

			SC.Security(self.aed_window,self.db,full_edit,self)
			PE.center_window_window(self.master,self.aed_window)
		return
	
	# attempts to execute a select query from the MySQL db
	# takes in a full query as a string
	# could be improved by using the more secure execute option
	def run_query_select(self,query):
		try:
			self.db.executeSQL(query)							# passes query into db class
			self.field_names = self.db.fetchColumnNames()		# fetches all the columns of the query and stores them
			self.fetched_data= self.db.fetchalldata()			# fetches all the rows of the query and stores them
		except:
			#self.db.close_db()
			self.db.refresh_connection()								# attempts to refresh lost connections
			try:
				self.db.executeSQL(query)						
				self.field_names = self.db.fetchColumnNames()
				self.fetched_data= self.db.fetchalldata()
			except MySQLdb.Error, e:
				pass
			#	PE.produce_error_popup(self,"MySQL Error [%d]: %s" % (e.args[0], e.args[1]))
			#except:
			#	PE.produce_error_popup(self,"Failed to gather data.\nConnection may be to an invalid database")
	
	# attemtps to gather the description of the selected table
	def run_querys_table_info(self):
		try:
			self.all_fields_info = self.db.describe_table(self.selected_table)				# returns all the field information for the selected table
			self.selected_table_pkey = self.db.return_primary_key(self.selected_table)		# returns the primary key as a string
		except:
			#self.db.close_db()
			self.db.refresh_connection()														# attempts to refresh lost connections
			try:
				self.all_fields_info = self.db.describe_table(self.selected_table)
				self.selected_table_pkey = self.db.return_primary_key(self.selected_table)
			except MySQLdb.Error, e:
			#	PE.produce_error_popup(self,"MySQL Error [%d]: %s" % (e.args[0], e.args[1]))
				pass
		
	def run_query_update(self,query):
		try:
			self.db.executeSQL(query)							# execute an update. do not fetch table info
			self.db.dbconn.commit()								# commit the update to the database
			return True
		except:
			#self.db.close_db()
			self.db.refresh_connection()
			try:
				self.db.executeSQL(query)
				self.db.dbconn.commit()
				return True
			except MySQLdb.Error, e:
				#PE.produce_error_popup(self,"MySQL Error [%d]: %s" % (e.args[0], e.args[1]))
				return False
			
	def return_flds_info(self):
		try:
			query = "select fld,alias,datatype from property_aliases where table_name = %s"
			self.db.executeSQL(query,(self.selected_table,))
			return self.db.fetchalldata()
		except MySQLdb.Error, e:
		#	PE.produce_error_popup(self,"MySQL Error [%d]: %s" % (e.args[0], e.args[1]))
			pass
		return None
	
	def search_box_load(self,e=0):
		srch = self.searchbox.get().lower()
		if srch:
			srch_table = []
			for r in range(len(self.table_rows)):
				for c in range(len(self.table_rows[r])):
					if srch in str(self.table_rows[r][c]).lower():
						srch_table.append(self.table_rows[r])
						break
			self.table_rows = srch_table
			self.reload_table()
			self.master.focus() # so the cursor is not in the search box anymore
	
	def compare_rows_selected(self):
		comp_rows = []
		self.table_rows = self.mlb.get_all_rows()
		for row in self.mlb.curselection():
			comp_rows.append(self.table_rows[row])
		self.table_rows = comp_rows
		self.reload_table()
		return
	
	def sink_table_button(self,num):
		for b in self.top_button_tables:
			if b == self.top_button_tables[num-1]:
				b.config(relief=tk.SUNKEN)
				break
			
	def raise_table_buttons(self):
		for b in self.top_button_tables:
			b.config(relief=tk.RAISED)
	
	# Gross ass load function on the foundation of even worse querying protos
	# Should make it take in a set of fields, a table name, and a string of 
	def load_table(self,flds,table,constraints='',but=0,check_date=True):

		self.table_fields = flds
		self.selected_table = table
		self.table_constraints = constraints

		#runs the actual query, loads string in current_query_loaded
		query = "select %s from %s %s" % (','.join(flds),table,constraints)
		self.run_query_select(query)
		self.current_query_loaded = query
		
		#raises all preset buttons, then sinks the correct one
		self.raise_table_buttons()
		if but > 0:
			self.sink_table_button(but)
		
		column_aliases = []
		column_names = []
		w = [max(len(str(x)) for x in line) for line in zip(*self.fetched_data)]
		
		db_flds,alias_flds = zip(*self.db.fetchAliases(self.selected_table))
		if self.table_fields != '*':
			for f in self.table_fields:
				column_aliases.append(alias_flds[db_flds.index(f)])
		else:
			column_aliases = alias_flds

		#determines the width of the column
		for n in range(len(column_aliases)):
			set_fields = []
			set_fields.append(column_aliases[n]) #n refers to the alias
			if w: # if returns rows
				if w[n] > 10:
					set_fields.append(w[n])
				elif w[n] == 10:
					set_fields.append(12)
				else:
					set_fields.append(10)
			else:
				set_fields.append(15)
			column_names.append(set_fields)

		if self.mlb:
			self.mlb.remove()
		
		self.mlb = MLB.MultiListbox(self.midframe, column_names , self)
		for row in self.fetched_data:
			self.mlb.insert(tk.END, row)
		self.mlb.pack(expand=tk.YES,fill=tk.BOTH)
		
		# #bind lists		
		for l in range(len(self.mlb.lists)):
			self.mlb.lists[l].bind('<Double-Button-1>', lambda e : self.aed_selected_row(add=False,to_delete=False))
			self.mlb.lists[l].bind('<Button-3>', lambda e, s=self: s.list_drop_menu(e))
			#self.mlb.lists[l].bind('<Delete>', lambda e : self.delete_selected_row(e))
		
		#bind labels
		for l in range(len(self.mlb.labls)):
			self.mlb.labls[l].bind('<Double-Button-1>', lambda e: self.sort_on_label(e))
			self.mlb.labls[l].bind('<Button-3>', lambda e : self.label_menu(e))
		
		self.convertDates()
		self.check_date_highlight(check_date)
		self.table_rows = self.mlb.get_all_rows()
		return

	def reload_table_querydb(self,preserve_format=True,adding_row=False):
		current_table_view = self.mlb.get_all_rows()
		if self.current_query_loaded:
			self.run_query_select(self.current_query_loaded)
			self.run_querys_table_info()
			if preserve_format:
				self.preserve_table_format(current_table_view,adding_row)
		self.reload_table()
		return 'Reloaded'
	
	def preserve_table_format(self,table_view,adding_row):
		pkey_loc = 0 #we know the primary key is the first one
		updated_table_view = []
		for preserve_row in table_view:
			for new_row in self.fetched_data:
				if str(new_row[pkey_loc]) == str(preserve_row[pkey_loc]):
					updated_table_view.append(new_row)
					break
		if adding_row:
			updated_table_view.append(self.fetched_data[-1])
		self.table_rows = updated_table_view
		return
		
	def reload_table(self):
		for r in self.mlb.lists:
			r.delete(0,r.size())
		self.mlb.clear_indexes()
		for r in self.table_rows:
			self.mlb.insert(tk.END, r)
		self.convertDates()
		self.check_date_highlight()
		return
				
	def label_menu(self,e):
		self.labelMenu = tk.Menu(self, tearoff=0)
		self.labelMenu.add_command(label="Sort ASC", 	command= lambda : self.sort_on_label(e))
		self.labelMenu.add_command(label="Sort DES", 	command= lambda : self.sort_on_label(e,r=True))
		self.labelMenu.add_command(label="Hide", 		command= lambda : self.mlb.hide_col(e.widget))
		self.labelMenu.add_command(label="Unhide", 		command= lambda : self.mlb.unhide_col(e.widget))
		self.labelMenu.post(e.x_root, e.y_root)
	
	def list_drop_menu(self,e):
		if self.selected_table:
			self.vrf_window = None
			self.mlb._checkselect(e.y)
			self.listMenu = tk.Menu(self, tearoff=0)
			if len(self.mlb.curselection()) > 1:
				self.listMenu.add_command(label="Compare  (%s)" % len(self.mlb.curselection()), command = self.compare_rows_selected)
			elif len(self.mlb.curselection()) == 1:
				self.listMenu.add_command(label="Edit", command= lambda : self.aed_selected_row(add=False,to_delete=False))
				self.listMenu.add_command(label="Delete", command= lambda : self.aed_selected_row(add=False,to_delete=True))
				self.listMenu.add_command(label="View Files", command= lambda : self.view_rows_files_window(e))
				if self.selected_table == 'property_reserves':
					self.listMenu.add_command(label="View Parcels", command= lambda : self.view_rows_parcels_window(e))
				self.listMenu.add_command(label="Export Entry", command= self.export_entry)
				if self.selected_table == 'property_reserves':
					self.listMenu.add_command(label="Export Reserve", command=self.export_reserve_parcels)
					
			self.listMenu.post(e.x_root, e.y_root)
		return
	
	# Wish this wouldve been MLB native and not in PDB
	def sort_on_label(self,e, r=False):
		w = e.widget
		mindate = datetime.date(datetime.MINYEAR, 1, 1)
		
		def getdate(x):
			return x[l] or mindate
		def is_date():
			for dt in self.table_rows:
				if type(dt[l]) is datetime.date:
					return True

		self.table_rows = self.mlb.get_all_rows()
		for l in range(len(self.mlb.labls)):
			if self.mlb.labls[l] == w:
				if is_date():
					self.table_rows = sorted(self.table_rows,key=getdate,reverse=r)
				else:
					self.table_rows = sorted(self.table_rows,key=lambda x : x[l],reverse=r)
				self.reload_table()
				break
		return
	
	def view_rows_parcels_window(self,e=0):
		selection 	= self.mlb.get(self.mlb.curselection()[0])
		if self.aed_window:
			self.aed_window.destroy()
		if self.vrf_window and update==1:
			for w in self.vrf_window.winfo_children():
				w.destroy()
		elif self.vrf_window:
			self.aed_window.destroy()
		else:
			self.vrf_window = tk.Toplevel(self)
			self.vrf_window.wm_title("Parcels Associated with %s" % selection[1] )
			self.vrf_window.resizable(0,1)
				

		VP.ViewParcels(self.vrf_window,self.db,selection,self.selected_table)
		return
	
	def view_rows_files_window(self,e=0):
		selection 	= self.mlb.get(self.mlb.curselection()[0])
		if self.aed_window:
			self.aed_window.destroy()
		if self.vrf_window and update == 1:
			for w in self.vrf_window.winfo_children():
				w.destroy()
		elif self.vrf_window:
			self.aed_window.destroy()
		else:
			self.vrf_window = tk.Toplevel(self)
			self.vrf_window.wm_title("Files Associated with %s" % selection[1] )
			self.vrf_window.resizable(0,0)
				
		VF.ViewFiles(self.vrf_window,self.db,selection,self.selected_table)
		PE.center_window_window(self.master,self.vrf_window)
		return
	
	def aed_selected_row(self,add=False,to_delete=False):
		if self.selected_table:
			if self.aed_window:
				self.aed_window.destroy()
			if self.vrf_window:
				self.vrf_window.destroy()
			
			if add:
				aed = 'Add'
				pkey = None
			elif self.mlb.curselection():
				aed = 'Edit'
				pkey = self.mlb.row_pkeyID()
			else:
				return
				
			self.aed_window = tk.Toplevel(self)
			self.aed_window.wm_title("%s Entry in %s" % (aed,self.selected_table))
			self.aed_window.resizable(0,0)

			AE.Add_or_Edit(self.aed_window, self.db, self.selected_table, self.reload_table_querydb, pkeyID=pkey,delete=to_delete)
		return
			
	def export_to_file(self):
		fname = tkf.asksaveasfilename(defaultextension = '.csv', initialfile="Table_Export.csv", initialdir = 'C:\\')
			
		if fname:
			tb_cols = [i[1] for i in self.db.fetchAliases(self.selected_table)]
			self.db.executeSQL("select * from %s %s" % (self.selected_table,self.table_constraints))
			tb_rows = [list(tup)[1:] for tup in self.db.fetchalldata()]
			
			#removes pkeyID
			tb_cols.pop(0)
				
			if not fname.endswith('.csv'):
				fname = fname + '.csv'
			with open(fname,"wb") as f:
				w = csv.writer(f)
				w.writerow (tb_cols)
				w.writerows(tb_rows)
		return
		
	def export_entry(self):
		fname = tkf.asksaveasfilename(defaultextension = '.csv', initialfile="Entry_Export.csv", initialdir = 'C:\\')
			
		if fname:
			row_pkey = self.table_rows[self.mlb.curselection()[0]][0]
			tb_cols = [i[1] for i in self.db.fetchAliases(self.selected_table)]
			self.db.executeSQL("select * from %s where pkeyID = %s" % (self.selected_table,row_pkey))
			tb_entr = list(self.db.fetchalldata()[0])
			
			entry_info = zip(tb_cols,tb_entr)
			entry_info = entry_info[1:]

			if not fname.endswith('.csv'):
				fname = fname + '.csv'
			with open(fname,"wb") as f:
				w = csv.writer(f)
				w.writerows(entry_info)
		return 

	def export_reserve_parcels(self):
		fname = tkf.asksaveasfilename(defaultextension = '.csv', initialfile="Reserve_Export.csv", initialdir = 'C:\\')
			
		if fname:
			row_pkey = self.table_rows[self.mlb.curselection()[0]][0]
		
			tb_cols = [i[1] for i in self.db.fetchAliases(self.selected_table)]
			self.db.executeSQL("select * from %s where pkeyID = %s" % (self.selected_table,row_pkey))
			tb_rows = list(self.db.fetchalldata()[0])
			reserve_info = zip(tb_cols,tb_rows)
			reserve_info = reserve_info[1:] #removes primary key
			
			self.db.executeSQL("select apn,data,area_acres from property_reserves_apn where property_fkey = %s and active = 'Yes'",(row_pkey,))
			reserve_parc = self.db.fetchalldata()
		
			if not fname.endswith('.csv'):
				fname = fname + '.csv'
			with open(fname,"wb") as f:
				w = csv.writer(f)
				w.writerows(reserve_info) # write the reserve info
				w.writerow (['\n'])
				w.writerow (['Parcel Number','Description','Area in Acres'])
				w.writerows(reserve_parc)
		return
	
	def send_requests_reports_window(self,type):
		self.srr_window = tk.Toplevel(self)
		self.srr_window.wm_title("Send %s" % (type))
		
		def send_requests_reports(type,msg):
			if msg:
				SM.sendmail_request(msg,'Property DataBase Request or Bug',to_whom='admin')
				self.srr_window.destroy()
		
		self.srr_window.bind('<Return>', lambda e : send_requests_reports(type,srr_text.get("1.0",'end-1c')))
		self.srr_window.bind('<Escape>', lambda e : self.srr_window.destroy )
		tk.Label(self.srr_window,text="Enter report or request").pack(padx=10,anchor="nw",expand='false')
		srr_text = tk.Text(self.srr_window, bg="white",height=10)
		srr_text.pack(padx=10,pady=2)
		srr_but = tk.Button(self.srr_window,text="Submit Report/Request",command=lambda : send_requests_reports(type,srr_text.get("1.0",'end-1c')))
		srr_but.pack(padx=10,anchor="nw",expand='false')
		srr_text.focus_set()
		
		#self.srr_window.bind('<Escape>', lambda e : self.srr_window.destroy )
		return
	
	def send_notify_mail_window(self):
		self.snm_window = tk.Toplevel(self)
		self.snm_window.geometry("250x100")
		self.snm_window.wm_title("Sending mail...")
		tk.Label(self.snm_window,text="Mail notifications have been sent.").pack()
		SM.send_notify_mail()
		tk.Button(self.snm_window,text="Okay",command=self.snm_window.destroy).pack()
		return
	
	def convertOneDate(self,date_string,date_start_format='%m-%d-%Y',date_end_format='%Y-%m-%d'):
		return datetime.datetime.strptime(date_string,date_start_format).strftime(date_end_format)
	
	def convertDates(self):
		flds,aliases,datatype = zip(*self.return_flds_info())
		for l in range(len(self.mlb.labls)):
			if self.mlb.labls[l].cget('text') in aliases and datatype[aliases.index(self.mlb.labls[l].cget('text'))] == 'Date':
				for n in range(self.mlb.size()):
					try:
						date_mdy = datetime.datetime.strptime(self.mlb.lists[l].get(n),'%Y-%m-%d').strftime('%m-%d-%Y')
						self.mlb.lists[l].delete(n)
						self.mlb.lists[l].insert(n,date_mdy)
					except:
						pass
		return
	
	def update_sel_count(self,event=0):
		if self.mlb:
			try:
				self.sels_returned_label["text"] = "Sel: %s / %s" % ( len(self.mlb.curselection()),self.mlb.size() )
			except:
				self.sels_returned_label["text"] = "Sel: 0 / %s" % ( self.mlb.size() )
	
	def update_botframe_info(self):
		self.rows_returned_label["text"] = "Rows: %s | Cols: %s" % (self.mlb.size(),len(self.mlb.labls)-1)
		try:
			self.table_name_label["text"] = self.selected_table
		except:
			self.table_name_label["text"] = 'Unknown'
		self.update_sel_count()
		self.dbcn_returned_label["text"] = "%s -- %s" % (self.db.HOST,self.db.DBSE)
		self.dbus_returned_label["text"] = "User: %s" % (self.db.USER)
		
	def clear_botframe_info(self):
		self.rows_returned_label["text"] = "Rows: 0 | Cols: 0"
		self.table_name_label["text"] = 'None'
		self.sels_returned_label["text"] = "Sel: 0 / 0"
		self.dbcn_returned_label["text"] = "%s -- %s" % (self.db.HOST,self.db.DBSE)
		self.dbus_returned_label["text"] = "User: %s" % (self.db.USER)
	
	def check_date_highlight(self,check_date=True):
		#set label in bot right for how many entries there are
		self.update_botframe_info()
	
		# Colors every other row to create transparency between entries
		self.mlb.color_break_rows()	
		if check_date and self.selected_table == 'property_LnLs':
			enddate = optenddate = -1
			today_date = datetime.datetime.now()#.strftime('%m-%d-%Y')
			in_180days = (datetime.datetime.now() + datetime.timedelta(days=180))#.strftime('%m-%d-%Y')
			#print today_date, in_180days
			
			def makeDate(s):
				return datetime.datetime.strptime(s,'%m-%d-%Y')
			
			for l in range(len(self.mlb.labls)):
				if   self.mlb.labls[l].cget('text') == "End Date":
					enddate = l
				elif self.mlb.labls[l].cget('text') == "Renewal End Date":
					optenddate = l
				elif self.mlb.labls[l].cget('text') == "Monthly":
					monthly = l
			if enddate >= 0:
				edate_field = self.mlb.lists[enddate] #return listbox
				month_field = self.mlb.lists[monthly]
				if optenddate >= 0:
					optdt_field = self.mlb.lists[optenddate] #return listbox
				else:
					optdt_field = None
				for d in range(edate_field.size()):
					if month_field.get(d) == 'No':
						#if option_date_exists
						if optdt_field and optdt_field.get(d):
							if makeDate(optdt_field.get(d)) <= today_date:
								for c in self.mlb.lists:
									c.itemconfig(d,bg='#FFADAD') #red3
							elif makeDate(optdt_field.get(d)) <= in_180days:
								for c in self.mlb.lists:
									c.itemconfig(d,bg='#FFD1A3')
						
						elif edate_field.get(d):
							if makeDate(edate_field.get(d)) <= today_date:
								for c in self.mlb.lists:
									c.itemconfig(d,bg='#FFADAD')
							elif makeDate(edate_field.get(d)) <= in_180days:
								for c in self.mlb.lists:
									c.itemconfig(d,bg='#FFD1A3') #D65900				
		return
	
	def open_help_document(self,file_link):
		try:
			os.startfile(file_link)
		except:
			PE.produce_error_popup(self.master,'Error: Invalid Link')	
	
if __name__ == '__main__':
	app = Application()
	app.master.title("Property DataBase")
	app.master.geometry("1200x750")
	app.master.iconbitmap(default=r".\icons\icon.ico")
	#app.master.configure(bg='black')
	#app.master.tk_setPalette(background='#C9C9C9')
	app.mainloop()
	app.db.close_db()

#C:\Python27\Arcgis10.3\python.exe V:\web_design\leases_n_liscense\PropertyDB.py