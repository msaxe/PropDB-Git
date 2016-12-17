try:
	import tkinter as tk
except:
	import Tkinter as tk
	
def produce_error_popup(master,error_msg):
	err_window = tk.Toplevel(master)
	err_window.wm_title("ERROR!")
	err_window.resizable(0,0)
	#err_window.geometry('320x100')
	tk.Label(err_window,text=error_msg,fg='red').pack(expand='false',anchor="w")
	tk.Button(err_window,text='Okay',command=err_window.destroy).pack(expand='false')
	err_window.grab_set()
	center_window_screen(err_window)
	return
	
def produce_error_frame(master,error_msg):
	err_window = master
	#err_window.wm_title("ERROR!")
	#err_window.resizable(0,0)
	#err_window.geometry('320x100')
	tk.Label(err_window,text=error_msg,fg='red').pack(expand='false',anchor="w")
	tk.Button(err_window,text='Okay',command=err_window.destroy).pack(expand='false')
	center_window_screen(err_window)
	#err_window.grab_set()
	return
	
def center_window_screen(win):
	win.update_idletasks()
	
	width = win.winfo_width()
	frm_width = win.winfo_rootx() - win.winfo_x()
	win_width = width + 2 * frm_width
	
	height = win.winfo_height()
	titlebar_height = win.winfo_rooty() - win.winfo_y()
	win_height = height + titlebar_height + frm_width
	
	x = win.winfo_screenwidth() // 2 - win_width // 2
	y = win.winfo_screenheight() // 2 - win_height // 2
	
	win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
	win.deiconify()

# Center a window on top of another window
def center_window_window(parent,child):
	parent.update_idletasks()
	child.update_idletasks()

	width = child.winfo_width()
	frm_width = child.winfo_rootx() - child.winfo_x()
	child_width = width + 2 * frm_width
	
	height = child.winfo_height()
	titlebar_height = child.winfo_rooty() - child.winfo_y()
	child_height = height + titlebar_height + frm_width
	
	x = (parent.winfo_width()  // 2 - child_width  // 2) + parent.winfo_rootx()
	y = (parent.winfo_height() // 2 - child_height // 2) + parent.winfo_rooty()
	
	child.geometry('{}x{}+{}+{}'.format(width, height, x, y))
	child.deiconify()
	
	