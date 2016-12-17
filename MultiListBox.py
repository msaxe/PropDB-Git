try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    import Tkinter as tk
    import ttk

main_label_bg_color = '#F0F0ED'
main_label_bg_dblue = '#59A8F7'
main_label_bg_lblue = '#ACE8FC'

class MultiListbox(tk.Frame):
	global main_label_bg_color
	global main_label_bg_dblue
	global main_label_bg_lblue
	
	def __init__(self, master, lists, main_app=None):
		tk.Frame.__init__(self, master)
		self.lists = []
		self.labls = []
		self.frmes = []
		self.sel_cols = []
		self.indexes = []
		self.app = main_app
		
		framer = tk.Frame(self)
		self.canvas = tk.Canvas(self,bd=0, highlightthickness=0)
		self.canvas.bind_all("<MouseWheel>", lambda e: _on_mousewheel(e))
		self.canvas.bind_all("<Shift-MouseWheel>", lambda e: _on_shiftmousewheel(e))

		def _on_mousewheel(event):
			for l in self.lists:
				l.yview_scroll(-1*(event.delta/120), "units")
				
		def _on_shiftmousewheel(event):
			self.canvas.xview_scroll(-1*(event.delta/120), "units")
		
		self.spacer = tk.Label(framer, borderwidth=1, relief=tk.RAISED)
		vscrol = ttk.Scrollbar(framer, orient=tk.VERTICAL  , command=self._scrolly)
		hscrol = ttk.Scrollbar(self  , orient=tk.HORIZONTAL, command=self.canvas.xview)
		
		self.canvas.config(xscrollcommand=hscrol.set)
		self.canvas.xview_moveto(0)
	
		self.interior = tk.Frame(self.canvas)
		interior_id = self.canvas.create_window(0,0,window=self.interior,anchor="nw")
		
		for l,w in lists:
			#frame create
			frame = tk.Frame(self.interior)#,bg='#DEDEDE'
			
			#label create
			lbl = tk.Label(frame, text=l, borderwidth=1, relief=tk.RAISED)

			#listbox create that one blue color #EBFAFF
			lb  = tk.Listbox(frame, width=w, borderwidth=0, bg='#EBFAFF', selectborderwidth=0,relief=tk.FLAT, exportselection=tk.FALSE)

			#lists
			self.lists.append(lb)
			self.labls.append(lbl)
			self.frmes.append(frame)
		
		self.bind_listboxes()
		self.bind_labels()
		
		for i in range(len(self.lists)):
			if i > 0: #does not pack the very first colum which SHOULD ALWYS BE THE AI PKEYID
				self.frmes[i].pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)
				self.labls[i].pack(fill=tk.X)
				self.lists[i].pack(expand=tk.YES, fill=tk.BOTH, padx=2)
			
			
		self.lists[1]['yscrollcommand']=vscrol.set

		#pack it all up
		framer.pack(side=tk.RIGHT, fill=tk.Y)
		self.canvas.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
		self.spacer.pack(fill=tk.X)
		vscrol.pack(expand=tk.YES, fill=tk.Y)
		hscrol.pack(fill=tk.X)
		
		for f in range(len(self.frmes)):
			#self.frmes[f].pack_propagate(0)
			if self.lists[f].winfo_reqwidth() > self.labls[f].winfo_reqwidth():
				self.frmes[f].config(width=self.lists[f].winfo_reqwidth())
			else:
				self.frmes[f].config(width=self.labls[f].winfo_reqwidth())
		
		
		self.call_back = None
		def _configure_interior(event):
			if self.call_back:
				self.after_cancel(self.call_back)
			self.call_back = self.after(100,resize_interior,event)
			
		def resize_interior(event):
			#print 'resizied'
			# update the height of the interior_id window to fit the canvas
			self.canvas.itemconfig(interior_id,height=event.height)
			
			# update the scrollbars to match the size of the inner frame
			size = (self.interior.winfo_reqwidth(), self.interior.winfo_reqheight())
			self.canvas.config(scrollregion="0 0 %s %s" % size)
				
			if self.canvas.winfo_width() > self.interior.winfo_reqwidth():
				self.canvas.itemconfig(interior_id,width=event.width)
		
		#def _configure_canvas(event):
		#	self.canvas.itemconfig(interior_id,height=event.height,width=event.width)
			
		self.canvas.bind('<Configure>', lambda e: _configure_interior(e))
		#self.bind('<Configure>', _configure_canvas)
		#print "end multilistbox __init__"
		return
	
	def bind_listboxes(self):
		for lb in self.lists:
			lb.bind('<B1-Motion>', lambda e, s=self: s._scrollselect(e.y))
			lb.bind('<Button-1>', lambda e, s=self: s._select(e.y))
			lb.bind('<Control-Button-1>', lambda e, s=self: s._ctrlselect(e.y))
			lb.bind('<Shift-Button-1>', lambda e, s=self: s._shiftselect(e.y))
			lb.bind('<Control-B1-Motion>', lambda e, s=self: s._scrollselect(e.y))
			lb.bind('<Shift-B1-Motion>', lambda e, s=self: s._scrollselect(e.y))
			lb.bind('<Leave>', lambda e: 'break')
	
	def bind_labels(self):
		for lbl in self.labls:
			lbl.bind('<B1-Motion>', lambda e : self._reziselabel(e))
			lbl.bind('<Motion>', lambda e : self.set_cursor(e))
			lbl.bind('<Button-1>', lambda e : self.label_select(e,False))
			lbl.bind('<Shift-Button-1>', lambda e : self.label_shiftselect(e))
			lbl.bind('<Control-Button-1>', lambda e : self.label_select(e,True))
			lbl.bind('<Enter>', lambda e: e.widget.config(bg=main_label_bg_lblue))
			lbl.bind('<Leave>', lambda e: self.label_leave_widget(e))
			
	def unbind_labels(self):
		for lbl in self.labls:
			lbl.unbind('<B1-Motion>')
			lbl.unbind('<Motion>')
			lbl.unbind('<Button-1>')
			lbl.unbind('<Shift-Button-1>')
			lbl.unbind('<Control-Button-1>')
			lbl.unbind('<Enter>')
			lbl.unbind('<Leave>')
	
	def color_break_rows(self):
		#soft highlight every other row
		for n in range(0,self.lists[0].size()):
			if n % 2:
				for l in self.lists:
					l.itemconfig(n,bg='#EBFAFF')
			else:
				for l in self.lists:
					l.itemconfig(n,bg='#FFFFFF')
		return	
	
	def repack_listboxes(self,first,last):
		#print "str repack_listboxes(%s,%s)" % (first,last)
		for f in range(first,last):
			self.frmes[f].pack_forget()
		for f in range(first,last):
			self.frmes[f].pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)
		#print "end repack_listboxes()"
		return
	
	def reset_label_sel_colors(self):
		#print "str reset_label_sel_colors()"
		for l in self.labls:
			l.config(bg=main_label_bg_color)
		self.sel_cols = []
		#print "end reset_label_sel_colors()"
		#update bot info sel count
		if self.app:
			self.app.update_sel_count()
		return
	
	def set_cursor(self,e):
		#print "str set_cursor()"
		if e.x < 10 or e.x > (e.widget.winfo_width() - 10):
			e.widget.config(cursor='sb_h_double_arrow')
		else:
			e.widget.config(cursor='arrow')
		#print "end set_cursor()"
		return
		
	def label_leave_widget(self,e):
		#print "str label_leave_widget(e)"
		if e.widget not in self.sel_cols: 
			e.widget.config(bg=main_label_bg_color)
		else:
			e.widget.config(bg=main_label_bg_dblue)
		#print "end label_leave_widget(e)"
		return
		
	def label_select(self,e,ctrl):
		#print "str label_select(e,ctrl=%s)" % ctrl
		if not ctrl:
			for s in self.sel_cols:
				s.config(bg=main_label_bg_color)
			self.sel_cols = []
		for n in range(len(self.frmes)):
			if self.labls[n] == e.widget:
				if e.widget in self.sel_cols:
					self.sel_cols.remove(e.widget)
				else:
					self.sel_cols.append(e.widget)
					e.widget.config(bg=main_label_bg_dblue)
		self.selection_clear(0, tk.END)
		#print "end label_select(e,ctrl=))"
		return
	
	def label_shiftselect(self,e):
		for n in range(len(self.frmes)):
			if self.labls[n] == e.widget:
				self.sel_cols.append(e.widget)
				e.widget.config(bg=main_label_bg_dblue)
		col_nums=[]
		for n in range(len(self.frmes)):
			if self.labls[n] in self.sel_cols:
				col_nums.append(n)
		for f in range(min(col_nums),max(col_nums)):
			self.sel_cols.append(self.labls[f])
			self.labls[f].config(bg=main_label_bg_dblue)
		self.selection_clear(0, tk.END)
		return
		
	def hide_col(self,e):
		for n in range(len(self.labls)):
			if self.labls[n] == e or self.labls[n] in self.sel_cols:
				# self.frmes[n].pack_forget()
				self.frmes[n].config(width=1,bg='#4A4A4A')
				self.labls[n].config(fg=main_label_bg_color)
				#self.labls[n].pack_forget()
				#self.lists[n].pack_forget()
				#self.frmes[n].pack_propagate(0)
		self.reset_label_sel_colors()
		return
		
	def unhide_col(self,e):
		if len(self.sel_cols) <= 1:
			for n in range(len(self.labls)):
				if self.labls[n] == e:
					if n:
						if self.lists[n-1].winfo_reqwidth() > self.labls[n-1].winfo_reqwidth():
							self.frmes[n-1].config(width=self.lists[n-1].winfo_reqwidth(),bg=main_label_bg_color)
							self.labls[n-1].config(fg='#000000')
						else:
							self.frmes[n-1].config(width=self.labls[n-1].winfo_reqwidth(),bg=main_label_bg_color)
							self.labls[n-1].config(fg='#000000')
		
					if n < len(self.frmes):
						if self.lists[n+1].winfo_reqwidth() > self.labls[n+1].winfo_reqwidth():
							self.frmes[n+1].config(width=self.lists[n+1].winfo_reqwidth(),bg=main_label_bg_color)
							self.labls[n+1].config(fg='#000000')
						else:
							self.frmes[n+1].config(width=self.labls[n+1].winfo_reqwidth(),bg=main_label_bg_color)
							self.labls[n+1].config(fg='#000000')
					break
					
		else:
			col_nums = []
			for i in range(len(self.frmes)):
				if self.labls[i] in self.sel_cols:
					col_nums.append(i)
			#self.repack_listboxes(min(col_nums),len(self.frmes))
			for f in range(min(col_nums),max(col_nums)):
				if self.lists[f].winfo_reqwidth() > self.labls[f].winfo_reqwidth():
					self.frmes[f].config(width=self.lists[f].winfo_reqwidth(),bg=main_label_bg_color)
					self.labls[f].config(fg='#000000')
				else:
					self.frmes[f].config(width=self.labls[f].winfo_reqwidth(),bg=main_label_bg_color)
					self.labls[f].config(fg='#000000')
			
			self.reset_label_sel_colors()
		return
	
	def _reziselabel(self,e):
		w = e.widget
		#print w.winfo_width(), e.x
		
		e.widget.config(bg=main_label_bg_lblue)
		if e.x < 12:
			for n in range(len(self.labls)):
				if self.labls[n] == w and n:
					self.frmes[n-1].config(width=(self.labls[n-1].winfo_width() + e.x))
					self.frmes[n].config(width=(self.labls[n].winfo_width() - e.x))
					break
					
		elif e.x > (w.winfo_width() - 12):
			for n in range(len(self.labls)):
				if self.labls[n] == w:
					self.frmes[n].config(width=e.x)
					break
					
		self.reset_label_sel_colors()
		return 'break'
	
	def unpack_labels(self):
		for l in self.labls:
			l.pack_forget()
		self.spacer.pack_forget()	
	
	def _scrollselect(self, y):
		row = self.lists[1].nearest(y)
		#self.selection_clear(0, tk.END)
		self.selection_set(row)
		self.reset_label_sel_colors()
		return 'break'
	
	def _select(self, y):
		row = self.lists[1].nearest(y)
		self.selection_clear(0, tk.END)
		self.selection_set(row)
		self.reset_label_sel_colors()
		return 'break'	
	
	def _checkselect(self, y):
		if self.selection_includes(self.lists[1].nearest(y)):
			return
		self._select(y)
		return 'break'
	
	def _ctrlselect(self, y):
		row = self.lists[1].nearest(y)
		if row in self.curselection():
			for l in self.lists:
				l.selection_clear(row,row)
			#self.selection_clear(0, tk.END)
		else:
			self.selection_set(row)
		self.reset_label_sel_colors()
		return 'break'
		
	def _shiftselect(self, y):
		row = self.lists[1].nearest(y)
		mx = max(self.curselection())
		mn = min(self.curselection())
		if row > mx:
			for r in range(mx,row+1):
				self.selection_set(r)
		elif row < mn:
			for r in range(row,mn):
				self.selection_set(r)
		else:
			self.selection_clear(0, tk.END)
			self.selection_set(row)
		self.reset_label_sel_colors()
		return 'break'

	def OnMouseWheel(self, event):
		if event.num == 5 or event.delta == -120:
			count -= 1
		if event.num == 4 or event.delta == 120:
			count += 1
		#for l in self.lists:
		#	l.yview(*args)
		print count
		self.scrollbar.set(*args)
		
	def _button3(self, y):
		self._select(y)
		return 'break'

	def _b3motion(self, x, y):
		#for l in self.lists:
		#	l.scan_dragto(x, y)
		return 'break'

	def _scroll(self, *args):
		for l in self.lists:
			l.yview(*args)
		return 'break'
		
	def _scrolly(self, *args):
		#print args
		for l in self.lists:
			l.yview(*args)
			
	def _scrollx(self, *args):
		for l in self.lists:
			l.yview(*args)

	def curselection(self):
		return self.lists[1].curselection()
		
	def row_pkeyID(self):
		#print "pkeyID = " + str(self.indexes[self.curselection()[0]])
		return self.indexes[self.curselection()[0]]

	def clear_indexes(self):
		self.indexes = []
		
	def delete(self, first, last=None):
		for l in self.lists:
			l.delete(first, last)
		del self.indexes[first:last]

	def get(self, first, last=None):
		result = []
		for l in self.lists:
			result.append(l.get(first,last))
		if last: return map(None, *result)
		return result
	
	def get_all_cols(self):
		return self.lists
	
	# returns list of rows
	def get_all_rows(self):
		rows = []
		for l in range(self.lists[0].size()):
			cols = []
			for c in range(len(self.lists)):
				#print self.lists[c].get(l)
				cols.append(self.lists[c].get(l))
			rows.append(cols)
		return rows
	
	def index(self, index):
		self.lists[1].index(index)

	def insert(self, index, *elements):
		self.indexes.append(elements[0][0])
		for e in elements:
			i = 0
			for l in self.lists:
				if e[i] != None:
					l.insert(index, e[i])
				else:
					l.insert(index, "")
				i = i + 1
		#print self.indexes
		
	def size(self):
		return self.lists[1].size()

	def see(self, index):
		for l in self.lists:
			l.see(index)

	def selection_anchor(self, index):
		for l in self.lists:
			l.selection_anchor(index)

	def selection_clear(self, first, last=None):
		for l in self.lists:
			l.selection_clear(first, last)

	def selection_includes(self, index):
		return self.lists[1].selection_includes(index)

	def remove(self):
		self.pack_forget()
		self.destroy()
	
	def selection_set(self, first, last=None):
		for l in self.lists:
			l.selection_set(first, last)
		return