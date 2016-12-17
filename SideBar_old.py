try:
	import Tkinter as tk
except:
	import tkinter as tk
import tkFont
import tkFileDialog as tkf
import PIL.Image
import PIL.ImageTk
import os, sys, csv, MySQLdb, datetime

import MultiListBox as MLB
import DataBase as DB

main_bg_color = '#E0E0E0'

class SideBar_Info(tk.Frame):
	def __init__(self, master, main_app=None):
		#tk.Frame.__init__(self, master)
		self.labels = []
		self.values = []
		self.app = main_app
		
		#top info control
		frametop = tk.Frame(master)
		
		self.right_arrow = PIL.ImageTk.PhotoImage(PIL.Image.open(r".\icons\right_arrow.png"))
		rbutton = tk.Button(frametop,image=self.right_arrow,width=10,height=10,relief=tk.FLAT)
		rbutton.pack(side=tk.RIGHT)
		
		self.left_arrow = PIL.ImageTk.PhotoImage(PIL.Image.open(r".\icons\left_arrow.png"))
		lbutton = tk.Button(frametop,image=self.left_arrow,width=10,height=10,relief=tk.FLAT)
		lbutton.pack(side=tk.RIGHT)
		
		self.top_label = tk.Label(frametop,text='0 / 0')
		self.top_label.pack(side=tk.RIGHT,expand=tk.NO,fill=tk.X)
		
		frametop.pack(side=tk.TOP,expand=tk.NO,fill=tk.X)
		#end top info control
		
		#info frame
		frameinfo = tk.Frame(master)
		framer = tk.Frame(frameinfo)
		self.canvas = tk.Canvas(frameinfo,bd=0, highlightthickness=0)
		self.canvas.bind_all("<MouseWheel>", lambda e: _on_mousewheel(e))
		self.canvas.bind_all("<Shift-MouseWheel>", lambda e: _on_shiftmousewheel(e))

		def _on_mousewheel(event):
			self.canvas.yview_scroll(-1*(event.delta/120), "units")
				
		def _on_shiftmousewheel(event):
			self.canvas.xview_scroll(-1*(event.delta/120), "units")
		
		vscrol = tk.Scrollbar(framer, orient=tk.VERTICAL, command=self.canvas.yview)
		hscrol = tk.Scrollbar(frameinfo, orient=tk.HORIZONTAL, command=self.canvas.xview)
		
		self.canvas.config(xscrollcommand=hscrol.set)
		self.canvas.config(yscrollcommand=vscrol.set)
		self.canvas.xview_moveto(0)
		self.canvas.yview_moveto(0)
	
		self.interior = tk.Frame(self.canvas)
		interior_id = self.canvas.create_window(0,0,window=self.interior,anchor="nw")
		
		framer.pack(side=tk.RIGHT, fill=tk.Y)
		self.canvas.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
		vscrol.pack(expand=tk.YES, fill=tk.Y)
		hscrol.pack(fill=tk.X)
		
		def _configure_interior(event):
			# update the scrollbars to match the size of the inner frame
			self.canvas.config(scrollregion="0 0 %s %s" % (self.interior.winfo_reqwidth(), self.interior.winfo_reqheight()))
				
			if self.canvas.winfo_width() > self.interior.winfo_reqwidth():
				self.canvas.itemconfig(interior_id,width=event.width)
			if self.canvas.winfo_height() > self.interior.winfo_reqheight():
				self.canvas.itemconfig(interior_id,height=event.height)
			
		self.canvas.bind('<Configure>', lambda e: _configure_interior(e))
		self.interior.grid_columnconfigure(1,weight=1)
		frameinfo.pack(side=tk.TOP,expand=tk.YES,fill=tk.BOTH)
		#end info frame
		return
	
	def load_label_rows(self,col_aliases):
		for c in range(len(col_aliases)):
			lbl_row = tk.Label(self.interior, text=col_aliases[c][1], anchor=tk.W, relief=tk.SUNKEN,borderwidth=1,bg="white")
			lbl_row.grid(row=c,column=0,sticky='we')
			
			val = tk.Label(self.interior, text='', anchor=tk.W, relief=tk.SUNKEN,borderwidth=1,bg="white")
			val.grid(row=c,column=1,sticky='we')
			
			self.labels.append(lbl_row)
			self.values.append(val)

class SideBar_Media(tk.Frame):
	def __init__(self, master, main_app=None):
		#tk.Frame.__init__(self, master)
		self.app = main_app
		
		frametop = tk.Frame(master)
		
		self.right_arrow = PIL.ImageTk.PhotoImage(PIL.Image.open(r".\icons\right_arrow.png"))
		rbutton = tk.Button(frametop,image=self.right_arrow,width=10,height=10,relief=tk.FLAT)
		rbutton.pack(side=tk.RIGHT)
		
		self.left_arrow = PIL.ImageTk.PhotoImage(PIL.Image.open(r".\icons\left_arrow.png"))
		lbutton = tk.Button(frametop,image=self.left_arrow,width=10,height=10,relief=tk.FLAT)
		lbutton.pack(side=tk.RIGHT)
		
		self.top_label = tk.Label(frametop,text='0 / 0')
		self.top_label.pack(side=tk.RIGHT,expand=tk.NO,fill=tk.X)
		
		frametop.pack(side=tk.BOTTOM,expand=tk.NO,fill=tk.X)
		
		return
