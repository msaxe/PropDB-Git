import MySQLdb

try:
	import tkinter as tk
except:
	import Tkinter as tk
import DataBase as DB
import MultiListBox as MLB
import ProduceError as PE
import ValidateEntry as VE
import Add_Edit as AE
import paths

main_bg_color = '#E0E0E0'

class ViewParcels():
	global main_bg_color
	def __init__(self,master,dbconn,selection,table):
		self.master = master
		self.db = dbconn
		self.mlb = None
		self.foreign_key = selection[0]
		self.parcels_table = table + '_apn'
		
		# Create Frames
		self.tframe = tk.Frame(self.master)
		self.bframe = tk.Frame(self.master)
		
		# Pack Frames
		self.tframe.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
		self.bframe.pack(side=tk.TOP, fill=tk.X)
		
		gplus  = tk.PhotoImage(file=paths.resource_path(r"icons\greenplus.gif"))
		redx   = tk.PhotoImage(file=paths.resource_path(r"icons\redx.gif"))
		
		self.widget_entires_params = [] # for validating entries
		
		self.eapn = tk.Entry(self.bframe,width=20)
		self.eapn.grid(row=0,column=0,sticky='w',padx=4)
		self.eapn.bind('<FocusOut>', lambda e,t='Text',   l=16 : VE._validate_entry(e.widget,t,length_constraint=l))
		self.widget_entires_params.append((self.eapn,'Text',16)) # append params for validating entries
		
		self.edes = tk.Entry(self.bframe,width=75)
		self.edes.grid(row=0,column=1,sticky='w')
		self.edes.bind('<FocusOut>', lambda e,t='Text',   l=100 : VE._validate_entry(e.widget,t,length_constraint=l))
		self.widget_entires_params.append((self.edes,'Text',100)) # append params for validating entries
		
		self.eare = tk.Entry(self.bframe,width=15)
		self.eare.grid(row=0,column=2,sticky='w',padx=4)
		self.eare.bind('<FocusOut>', lambda e,t='Decimal',l=13 : VE._validate_entry(e.widget,t,length_constraint=l))
		self.widget_entires_params.append((self.eare,'Decimal',13)) # append params for validating entries
		
		gp = tk.Button(self.bframe,image=gplus,command=self.add_parcel_db,width=20,height=20,relief=tk.FLAT,bg=main_bg_color)
		gp.image = gplus
		gp.grid(row=0,column=3,sticky='e')
	
		self.load_table()
		self.master.grab_set() # Forces user to interact here
	
	def fetch_parcel_data(self):
		try:
			self.db.executeSQL("select pkeyID,apn,data,area_acres from %s where property_fkey = '%s' and active = 'Yes'" % (self.parcels_table,self.foreign_key))
			data = self.db.fetchalldata()
		except MySQLdb.Error, e:
			PE.produce_error_popup(self.master,"MySQL Error [%d]\n%s" % (e.args[0], e.args[1]))
		return data
	
	def load_table(self):
		data = self.fetch_parcel_data()
		self.mlb = MLB.MultiListbox(self.tframe, [['pkey',5],['Parcel Number',14],['Description',55],['Area in Acres',10]])
		for row in data:
			self.mlb.insert(tk.END, row)
		self.mlb.pack(expand=tk.YES,fill=tk.BOTH)
		
		#self.mlb.hscrol.pack_forget()
		self.mlb.unbind_labels()
		
		self.mlb.color_break_rows()
		self.create_list_binds()
		return

	def reload_table(self):
		data = self.fetch_parcel_data()
		self.mlb.delete(0,self.mlb.size())
		for row in data:
			self.mlb.insert(tk.END, row)
		self.mlb.color_break_rows()
		return
	
	def create_list_binds(self):
		for l in self.mlb.lists:
			l.bind('<Double-Button-1>',lambda e, s=self: s.edit_parcel(e))
			l.bind('<Button-3>'		,  lambda e, s=self: s.list_drop_menu(e))
			l.bind('<Delete>'		,  lambda e, s=self: s.edit_parcel(e,True))
		
	def add_parcel_db(self):
		fn = self.eapn.get()
		fl = self.edes.get()
		fa = self.eare.get()
		if VE._validate_entries(self.widget_entires_params) and (fl or fn or fa):
			query = "insert into %s (property_fkey,apn,data,area_acres) values (%%s,%%s,%%s,%%s);" % self.parcels_table
			try:
				self.db.executeSQL(query,(self.foreign_key,fn,fl,fa))
				self.reload_table()
				self.db.dbconn.commit()
				self.eapn.delete(0,tk.END)
				self.edes.delete(0,tk.END)
				self.eare.delete(0,tk.END)
			except MySQLdb.Error, e:
				PE.produce_error_popup(self.master,"MySQL Error [%d]\n%s" % (e.args[0], e.args[1]))
		else:
			PE.produce_error_popup(self.master,"Failed to validate all entries.\nCheck that the entries match the datatypes.")

	def edit_parcel(self,e=0,to_delete=False):
		if self.parcels_table and self.mlb.curselection():
			#if self.aed_window:
			#	self.aed_window.destroy()
				
			aed_window = tk.Toplevel(self.master)
			aed_window.wm_title("Edit Entry in %s" % self.parcels_table)
			aed_window.resizable(0,0)
			
			AE.Add_or_Edit(aed_window, self.db, self.parcels_table, self.reload_table, self.mlb.row_pkeyID(),delete=to_delete)
		return
		
	def list_drop_menu(self,e):
		if len(self.mlb.curselection()) == 1:
			self.listMenu = tk.Menu(self.master, tearoff=0)
			self.listMenu.add_command(label="Edit"	, command= lambda : self.edit_parcel(e,to_delete=False))
			self.listMenu.add_command(label="Delete", command= lambda : self.edit_parcel(e,to_delete=True ))
		
			self.listMenu.post(e.x_root, e.y_root)
	