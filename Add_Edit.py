try:
	import Tkinter as tk
except:
	import tkinter as tk
import MySQLdb
import ttk, re, datetime

import DataBase as DB
import ValidateEntry as VE
import ProduceError as PE

class Add_or_Edit():

	def __init__(self,master,dbconn,table,reload_func,pkeyID=None,delete=False):
		self.master = master
		self.frame = None
		self.db = dbconn
		self.pkeyID = pkeyID
		self.widget_list = []
		self.cur_entry = None
		self.table_name = table
		self.reload_func = reload_func
		
		if not delete:
			self.frame = tk.Frame(self.master)
			self._get_fields()
			self._get_data_edit()
			self._create_widgets()
			self.master.grab_set() # Forces user to interact here
		if delete:
			self.delete_entry_window(delete)
		
	def _get_fields(self):
		try:
			self.db.executeSQL("select fld,alias,datatype,domain_tbl,max_len,user_sees from property_aliases where table_name = %s order by in_order ASC;", (self.table_name,))
			self.fields = self.db.fetchalldata()
			#print self.fields
		except MySQLdb.Error, e:
			PE.produce_error_frame(self.frame,"MySQL Error [%d]\n%s" % (e.args[0], e.args[1]))
		
	def _get_data_edit(self):
		if self.pkeyID:
			try:
				self.db.executeSQL("select * FROM %s WHERE pkeyID = %s;" % (self.table_name,self.pkeyID))
				self.cur_entry = self.db.fetchalldata()[0] #list of entries
				#print self.cur_entry
			except MySQLdb.Error, e:
				pass
				#PE.produce_error_popup(self.master,"MySQL Error [%d]\n%s" % (e.args[0], e.args[1]))
	
	def _validate_entries(self):
		success = True
		for w,d,l,f in self.widget_list:
			if not VE._validate_entry(w,d,l,write_errors=False):
				success = False
				
		if not success:
			PE.produce_error_popup(self.master,"Failed to validate all entries.\nCheck that the entries match the datatypes.")
			
		return success
	
	def _create_labels(self):
		if self.cur_entry and len(self.fields) != len(self.cur_entry):
			PE.produce_error_popup(self.master,"Mismatching fields to fields aliases.\nCheck the database and be sure to include all columns.")
			return
		fields_row_count = entry_row_count = 0
		for FLD,ALS,DTY,DTB,MXL,URS in self.fields:
			if URS == 'Yes':
				widget = tk.label(self.frame,width="50")
				if self.pkeyID and str(self.cur_entry[fields_row_count]) != 'None':
					widget["text"] = str(self.cur_entry[fields_row_count])
				
				entry_row_count += 1	#row counter
			fields_row_count += 1	#counts entry rows in order to correctly insert values
		self.frame.pack()
	
	def _create_widgets(self):
		if self.cur_entry and len(self.fields) != len(self.cur_entry):
			PE.produce_error_popup(self.master,"Mismatching fields to fields aliases.\nCheck the database and be sure to include all columns.")
			return
		fields_row_count = entry_row_count = 0
		for FLD,ALS,DTY,DTB,MXL,URS in self.fields:
			if URS == 'Yes':
				if DTY == "Set":
					try:
						self.db.executeSQL("select val FROM %s" % str(DTB) )
						domain = self.db.fetchalldata()
						domain = [".".join(map(str,r)) for r in domain]
					except MySQLdb.Error, e:
						PE.produce_error_popup(self.master,"MySQL Error [%d]: %s" % (e.args[0], e.args[1]))
					widget = ttk.Combobox(self.frame,width="50",state='readonly')
					widget['values'] = domain
					
					if self.pkeyID and str(self.cur_entry[fields_row_count]) != 'None':
						try:
							widget.current(domain.index(self.cur_entry[fields_row_count]))
						except:
							print "Could not index current entry: %s" % self.cur_entry[fields_row_count]
						
				#elif DTY == "Date":
					#if datepicker is ever implemented
					
				else:
					widget = tk.Entry(self.frame,width="50")
					
					if self.pkeyID and str(self.cur_entry[fields_row_count]) != 'None':
						widget.insert(tk.END,str(self.cur_entry[fields_row_count]))
				
				widget.bind('<FocusOut>', lambda e, arg1=DTY, arg2=MXL : VE._validate_entry(e.widget,arg1,length_constraint=arg2))
				self.entry_row(ALS,widget,DTY,entry_row_count)
				self.widget_list.append([widget,			#refers to the actual widget
										DTY,				#datatype of entry
										MXL,				#max length of entry
										FLD					#corresponding db field
										])
				entry_row_count += 1	#row counter
			fields_row_count += 1	#counts entry rows in order to correctly insert values
		self.frame.pack()
		
		if self.pkeyID:
			add_butt = tk.Button(self.frame, text="Edit Entry")
			add_butt["command"] = lambda : self.edit_entry_db()
			
			del_butt = tk.Button(self.frame, text="Delete Entry" ,bg='light pink')
			del_butt["command"] = lambda : self.delete_entry_window()
			del_butt.grid(row=entry_row_count,column=0,pady=2)
		else:
			add_butt = tk.Button(self.frame, text="Add Entry")
			add_butt["command"] = lambda : self.add_entry_db()
			
		add_butt.grid(row=entry_row_count,column=1,pady=2)
			
		can_butt = tk.Button(self.frame, text="Cancel")
		can_butt["command"] = self.master.destroy
		can_butt.grid(row=entry_row_count,column=2,pady=2)
		
	def entry_row(self,col_name,widget,data_type,row_count):	
		ln = tk.Label(self.frame, text=col_name)
		ln.grid(row=row_count,column=0,sticky="w")
		widget.grid(row=row_count,column=1,padx=2,sticky="ew")
		lt = tk.Label(self.frame, text=data_type)
		lt.grid(row=row_count,column=2,sticky="w")
	
	def add_entry_db(self):
		if not self._validate_entries():
			#produce error popup
			#print "Failed to validate all entries.\nCheck that the entries match the datatypes"
			return
		
		flds = [f[0] for f in self.fields]
		#flds.pop(0) #remove the auto incremented pkey that is not set by the user
		#flds = ','.join(flds)
		
		add_vals = []
		for w,d,l,f in self.widget_list:
			get_val = w.get()
			if get_val != '':
				vals = []
				vals.append(f)
				vals.append(get_val)
				add_vals.append(vals)
		
		if len(add_vals):
			field_names, field_vals = zip(*add_vals)
			
			flds_names_s = ','.join( field_names )
			add_vals_s = ','.join(['%s'] * len(field_vals))
			
			query_str =  "INSERT INTO %s (%s) VALUES (%s);" % (self.table_name,flds_names_s,add_vals_s)
			#print query_str
			
			try:
				self.db.executeSQL(query_str, tuple(field_vals))
				self.db.dbconn.commit()
				self.reload_func(adding_row=True)
				self.master.destroy()
			except MySQLdb.Error, e:
				PE.produce_error_popup(self.master,"MySQL Error [%d]\n %s" % (e.args[0], e.args[1]))
			except:
				PE.produce_error_popup(self.master,"Failed to add data!")
		return 
		
	def edit_entry_db(self):
		if not self._validate_entries():
			#produce error popup
			#print "Failed to validate all entries.\nCheck that the entries match the datatypes"
			return
			
		flds = [f[0] for f in self.fields] # db field names
	
		query = "UPDATE %s SET" % self.table_name
		where_clause = " WHERE pkeyID = %s;" % self.pkeyID
		
		set = set_vals = []
		for w,d,l,f in self.widget_list:
			new_val = w.get()
			old_val = self.cur_entry[flds.index(f)]
			if old_val is None or old_val == None:		#forces None or NULLS to be seen a ""
				old_val = ""
			else:
				old_val = str(old_val)
			if new_val != old_val:
				if set:
					set += (", %s = %%s" % f)
				else:
					set  = (" %s = %%s" % f)
				set_vals.append(new_val)
		
		if set:
			update_sql = query + set + where_clause
			try:
				self.db.executeSQL(update_sql,tuple(set_vals))
				self.db.dbconn.commit()
				self.reload_func()
				self.master.destroy()
			except MySQLdb.Error, e:
				PE.produce_error_popup(self.master,"MySQL Error [%d]\n%s" % (e.args[0], e.args[1]))
			except:
				PE.produce_error_popup(self.master,"Failed to edit data!\n%s" % update_sql)
		else:
			self.master.destroy()
		return
		
	def delete_entry_window(self,strict_delete=False):
		if self.frame:
			aed_window = tk.Toplevel(self.master)
			aed_window.wm_title("Delete Entry in %s!" % self.table_name)
			aed_window.resizable(0,0)
		else:
			aed_window = self.master
		
		def delete_entry_db():
			try:
				query = "update %s set active = 'No' where pkeyID = %%s" % self.table_name
				self.db.executeSQL(query,(self.pkeyID,))
				self.db.dbconn.commit()
			except MySQLdb.Error, e:
				PE.produce_error_popup(self.master,"MySQL Error [%d]\n%s" % (e.args[0], e.args[1]))
			except:
				PE.produce_error_popup(self.master,"Failed to delete data!")
			finally:
				self.reload_func()
				aed_window.destroy()
				self.master.destroy()
			
			flds = [f[0] for f in self.fields]
			if 'deleted_by' in flds and 'deleted_on' in flds:
				try:
					query = "update %s set deleted_by = %%s, deleted_on = NOW() where pkeyID = %%s" % self.table_name
					self.db.executeSQL(query,(self.db.USER,self.pkeyID))
					self.db.dbconn.commit()
				except MySQLdb.Error, e:
					PE.produce_error_popup(self.master,"MySQL Error [%d]\n%s" % (e.args[0], e.args[1]))
		
		delete_frame = tk.Frame(aed_window)
		delete_frame.grid(sticky='nsew')
		lb = tk.Label(delete_frame,text="Are you sure you wish to delete the selected row?")
		lb.pack(side=tk.TOP)
		#lb = tk.Label(delete_frame,text="(The delete is permanent and cannot be undone)")
		#lb.pack(side=tk.TOP)
		#lb = tk.Label(delete_frame,text=self.mlb.get(selection)[2])
		#lb.pack(side=tk.TOP)
		bt = tk.Button(delete_frame, text="Delete Entry",bg="light pink")
		bt["command"] = delete_entry_db
		bt.pack(side=tk.LEFT,pady=2,padx=2)
		cl = tk.Button(delete_frame, text="   Cancel   ")
		if strict_delete:
			cl["command"] = self.master.destroy
		else:
			cl["command"] = aed_window.destroy
		cl.pack(side=tk.RIGHT,pady=2,padx=2)
			
		aed_window.bind('<Escape>', aed_window.destroy)
		aed_window.grab_set()
		PE.center_window_screen(aed_window)
		
		return