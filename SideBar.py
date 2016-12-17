try:
	import Tkinter as tk
	from Tkinter import ttk
except ImportError:
	import tkinter as tk
	import ttk

import PIL.Image, PIL.ImageTk
import threading

import MultiListBox as MLB
import DataBase as DB
import StaticImage as SI
import paths

main_bg_color = '#E0E0E0'

class SideBar_Info(tk.Frame):
	def __init__(self, master, main_app=None):
		tk.Frame.__init__(self, master)
		self.labels = []
		self.values = []
		self.selected_primary_keys = []
		self.table = ''
		self.current_info_num = 0
		self.current_key_loaded = None
		self.app = main_app
		self.side_media = None
		self.call_back = None
		self.pack_propagate(0)
		
		def mouse_motion(event):
			#print event, midside_info.winfo_height(), midside_media.winfo_height(), self.winfo_height()
			info_h = midside_info.winfo_height()
			imga_h = midside_media.winfo_height()
			min__h = frametop.winfo_height()
			total  = self.winfo_height()
			if info_h + event > min__h and imga_h - event > min__h:
				midside_info.configure(height=info_h + event)
				midside_media.configure(height=imga_h - event)
			elif info_h + event < min__h:
				midside_info.configure(height=min__h)
				midside_media.configure(height=total - min__h)
			elif imga_h - event < min__h:
				midside_info.configure(height=total - min__h)
				midside_media.configure(height=min__h)
			
		# breaking up side frame into 3 parts
		midside_info = tk.Frame(self)
		midside_info.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
		midside_info.pack_propagate(0)
		midside_info.configure(bg=main_bg_color)
		
		movebar_hort_image = PIL.ImageTk.PhotoImage(PIL.Image.open(paths.resource_path(r"icons\movebar_hort.png")))
		midside_move_button = tk.Label(self, image=movebar_hort_image,width=80,height=6)
		midside_move_button.image = movebar_hort_image
		midside_move_button.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
		midside_move_button.configure(bg="#EAEAEA",relief=tk.FLAT,cursor='sb_v_double_arrow')
		#midside_move_button.bind('<B1-Motion>',lambda e: mouse_motion(e.y))
		midside_move_button.bind('<ButtonRelease-1>',lambda e: mouse_motion(e.y))
		
		midside_media = tk.Frame(self)
		midside_media.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
		midside_media.pack_propagate(0)
		midside_media.configure(bg=main_bg_color)
		#end break up
		
		#top info control
		frametop = tk.Frame(midside_info)
		
		right_arrow = PIL.ImageTk.PhotoImage(PIL.Image.open(paths.resource_path(r"icons\right_arrow.png")))
		rbutton = tk.Button(frametop,image=right_arrow,width=10,height=10,relief=tk.FLAT)
		rbutton.image = right_arrow
		rbutton['command'] = lambda : self.next_select_info(1)
		rbutton.pack(side=tk.RIGHT)
		
		left_arrow = PIL.ImageTk.PhotoImage(PIL.Image.open(paths.resource_path(r"icons\left_arrow.png")))
		lbutton = tk.Button(frametop,image=left_arrow,width=10,height=10,relief=tk.FLAT)
		lbutton.image = left_arrow
		lbutton['command'] = lambda : self.next_select_info(-1)
		lbutton.pack(side=tk.RIGHT)
		
		self.top_label = tk.Label(frametop,text='0 / 0')
		self.top_label.pack(side=tk.RIGHT,expand=tk.NO,fill=tk.X)
		
		frametop.pack(side=tk.TOP,expand=tk.NO,fill=tk.X)
		#end top info control
		
		#info frame
		self.frameinfo = tk.Frame(midside_info)
		framer = tk.Frame(self.frameinfo,)
		frameb = tk.Frame(self.frameinfo)
		self.canvas = tk.Canvas(self.frameinfo,bd=0, highlightthickness=0)
		#self.canvas.bind_all("<MouseWheel>", lambda e: _on_mousewheel(e))
		#self.canvas.bind_all("<Shift-MouseWheel>", lambda e: _on_shiftmousewheel(e))

		#def _on_mousewheel(event):
		#	self.canvas.yview_scroll(-1*(event.delta/120), "units")
				
		#def _on_shiftmousewheel(event):
		#	self.canvas.xview_scroll(-1*(event.delta/120), "units")
		
		vscrol = ttk.Scrollbar(framer, orient=tk.VERTICAL  , command=self.canvas.yview)
		hscrol = ttk.Scrollbar(frameb, orient=tk.HORIZONTAL, command=self.canvas.xview)
		
		self.canvas.config(xscrollcommand=hscrol.set)
		self.canvas.config(yscrollcommand=vscrol.set)
		self.canvas.xview_moveto(0)
		self.canvas.yview_moveto(0)
	
		self.interior = tk.Frame(self.canvas)
		self.interior_id = self.canvas.create_window(0,0,window=self.interior,anchor="nw")
		
		framer.pack(side=tk.RIGHT, fill=tk.Y)
		frameb.pack(side=tk.BOTTOM, fill=tk.X)
		vscrol.pack(expand=tk.YES, fill=tk.Y)
		hscrol.pack(expand=tk.NO , fill=tk.X)
		self.canvas.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
		
		self.canvas.bind('<Configure>', lambda e: self.configure_scroll_region(e))
		self.interior.grid_columnconfigure(1,weight=1)#,minsize=500)
		self.frameinfo.pack(side=tk.TOP,expand=tk.YES,fill=tk.BOTH)
		#end info frame
		
		self.side_media = SideBar_Media(midside_media,self)
		self.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
		return
	
	def configure_scroll_region(self,event=0):
		if self.call_back:
			self.after_cancel(self.call_back)
		self.call_back = self.after(100,self.resize_interior,event)
	
	def resize_interior(self,event):
		self.frameinfo.update_idletasks()
		self.canvas.config(scrollregion="0 0 %s %s" % (self.interior.winfo_reqwidth(), self.interior.winfo_reqheight()))
		
		if self.frameinfo.winfo_width() < self.interior.winfo_reqwidth():
			self.canvas.config(width=self.interior.winfo_reqwidth())
			self.canvas.itemconfig(self.interior_id,width=self.interior.winfo_reqwidth())
			self.canvas.config(height=self.canvas.winfo_reqheight())
		else:
			if self.canvas.winfo_width() > self.interior.winfo_reqwidth():
				self.canvas.itemconfig(self.interior_id,width=self.canvas.winfo_width())
			#if self.canvas.winfo_height() > self.interior.winfo_reqheight():
			#	self.canvas.itemconfig(self.interior_id,height=self.canvas.winfo_height())
				
		return
	
	def load_label_rows(self,col_aliases,table):
		self.destroy_interior_widgets()
		self.table = table
		for c in range(len(col_aliases)):
			lbl_row = tk.Label(self.interior, text=col_aliases[c][1], anchor=tk.W, relief=tk.SUNKEN,borderwidth=1,bg="white")
			lbl_row.grid(row=c,column=0,sticky='we')
			
			val = tk.Label(self.interior, text='', anchor=tk.W, relief=tk.SUNKEN,borderwidth=1,bg="white")
			val.grid(row=c,column=1,sticky='we',ipadx=4)
			
			self.labels.append(lbl_row)
			self.values.append(val)
			
		self.configure_scroll_region()
		self.canvas.xview_moveto(0)
		self.canvas.yview_moveto(0)
		self.side_media.clear_all_images()
		self.side_media.load_image(self.side_media.no_img)
			
	def load_info_values(self,vals):
		self.current_key_loaded = vals[0]
		for w,v in zip(self.values,vals):
			w['text'] = v
		self.configure_scroll_region()
		
		for l,v in zip(self.labels,vals):
			#print l['text'],v
			if l['text'] == 'Address' and v:
				self.side_media.load_location(v)
				#print 'loading: %s' % v
				break
			
	def clear_info_values(self):
		self.current_key_loaded = None
		for w in self.values:
			w['text'] = ''
		self.configure_scroll_region()
		self.side_media.clear_all_images()
		if not self.selected_primary_keys:
			self.side_media.load_image(self.side_media.no_img)
		
	def destroy_interior_widgets(self):
		if self.labels:
			for a,b in zip(self.labels,self.values):
				a.destroy()
				b.destroy()
		
			self.labels = []
			self.values = []
			self.table  = ''
		
	def edit_selection_label_text(self,on_,total):
		self.top_label['text'] = '%s / %s' % (on_,total)
		
	def load_selected_keys(self,keys):
		if keys:
			self.selected_primary_keys = keys
			if self.current_key_loaded not in keys:
				self.clear_info_values()
				self.load_info_values( self.get_info_values(self.selected_primary_keys[0]) )
				#self.interior.update_idletasks()
		else:
			self.clear_info_values()
			
		self.update_current_info_num()
		self.edit_selection_label_text(self.current_info_num,len(keys))
		
	def get_info_values(self,key):
		if self.selected_primary_keys and self.current_key_loaded is not key:
			if self.app.db.executeSQL( "select * FROM %s WHERE pkeyID = %s" % (self.table,key) ):
				return self.app.db.fetchalldata()[0]
		return None
	
	def update_current_info_num(self):
		for k in range(len(self.selected_primary_keys)):
			if self.selected_primary_keys[k] == self.current_key_loaded:
				self.current_info_num = k+1
				return
		self.current_info_num = 0
	
	def next_select_info(self,direction):
		if self.selected_primary_keys > 1:
			if self.current_info_num-1 + direction > len(self.selected_primary_keys)-1:
				new_val = 0
			elif self.current_info_num-1 + direction < 0:
				new_val = len(self.selected_primary_keys)-1
			else:
				new_val = self.current_info_num-1 + direction
				
			self.clear_info_values()
			self.load_info_values( self.get_info_values(self.selected_primary_keys[new_val]) )
			self.current_info_num = new_val+1
			self.edit_selection_label_text(self.current_info_num,len(self.selected_primary_keys))

			
class SideBar_Media(tk.Frame):
	def __init__(self, master, parent=None):
		tk.Frame.__init__(self, master)
		self.app = parent
		self.no_img = paths.resource_path(r'icons\no_img.png')
		self.ld_img = paths.resource_path(r'icons\loading.png')
		self.loaded_img = None
		self.loaded_img_text = ''
		self.location_image = None
		self.location_image_thread = None
		self.images = []
		self.image_threads = []
		
		frametop = tk.Frame(self)
		
		right_arrow = PIL.ImageTk.PhotoImage(PIL.Image.open(paths.resource_path(r"icons\right_arrow.png")))
		rbutton = tk.Button(frametop,image=right_arrow,width=10,height=10,relief=tk.FLAT)
		rbutton.image = right_arrow
		rbutton.pack(side=tk.RIGHT)
		
		left_arrow = PIL.ImageTk.PhotoImage(PIL.Image.open(paths.resource_path(r"icons\left_arrow.png")))
		lbutton = tk.Button(frametop,image=left_arrow,width=10,height=10,relief=tk.FLAT)
		lbutton.image = left_arrow
		lbutton.pack(side=tk.RIGHT)
		
		self.top_label = tk.Label(frametop,text='0 / 0')
		self.top_label.pack(side=tk.RIGHT,expand=tk.NO,fill=tk.X)
		
		frametop.pack(side=tk.BOTTOM,expand=tk.NO,fill=tk.X)
		
		# image frame portion
		self.framebot = tk.Frame(self)
		self.framemedia_canvas = tk.Canvas(self.framebot)
		self.interior_id = self.framemedia_canvas.create_image(0,0,image=None,anchor="nw")
		# vsb = ttk.Scrollbar(self.framebot, orient=tk.VERTICAL  , command=self.framemedia_canvas.yview)
		# hsb = ttk.Scrollbar(self.framebot, orient=tk.HORIZONTAL, command=self.framemedia_canvas.xview)
		# self.framemedia_canvas.configure(yscrollcommand=vsb.set)
		# self.framemedia_canvas.configure(xscrollcommand=hsb.set)
		
		self.load_image(self.no_img)
		
		self.framemedia_canvas.grid(row=0, column=0, sticky=tk.NSEW)
		# vsb.grid(row=0, column=1, rowspan=2, sticky=tk.NSEW)
		# hsb.grid(row=1, column=0, sticky=tk.NSEW)
		self.framebot.columnconfigure(0, weight=1)
		self.framebot.rowconfigure(0, weight=1)
		
		self.framebot.pack(side=tk.TOP,expand=tk.YES,fill=tk.BOTH)
		self.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
		return

	def load_image(self,img,justify='nw'):
		#self.framemedia_canvas.delete('all')
		self.loaded_img_text = img
		self.loaded_img = PIL.ImageTk.PhotoImage(PIL.Image.open(img))
		img_id = self.framemedia_canvas.itemconfig(self.interior_id,image=self.loaded_img,anchor=justify)#create_image(0,0,image=self.loaded_img,anchor=justify)
		self.framemedia_canvas.config(scrollregion=self.framemedia_canvas.bbox('all'))
		
	def load_location(self,loc):
		self.lding_image()
		self.location_image_thread = fetch_location_image(loc,self.location_image,self.load_location_image,width=self.framebot.winfo_width(),height=self.framebot.winfo_height())
		self.location_image_thread.start()
		
	def load_location_image(self,loc_img):
		if loc_img:
			self.load_image(loc_img)
		else:
			self.load_image(self.no_img)
	
	def lding_image(self):
		self.load_image(self.ld_img,justify='center')
	
	def clear_all_images(self):
		self.location_image = None
		self.images = []

		
		
		
# Threaded image get functions
def fetch_images(urls):
	results = []
	def getter(url, dest):
		results.append(urllib.urlretreave(url, dest))
	
	threads = []
	for u in urls:
		t = threading.Thread(target=getter, args=('http://test.com/file %s.png' % x,'temp/file %s.png' % x))
		t.start()
		threads.append(t)
		
	map(lambda t: t.join(), threads)
		
def fetch_location_image(location_str,var_location_image,load_function,width,height):
	def getter(loc,w,h):
		var_location_image = SI.get_static_google_map('test', center=loc.replace(' ','+'),imgsize=(w,h))#,markers=m)
		load_function(var_location_image)

	return threading.Thread(target=getter, args=(location_str,width,height))