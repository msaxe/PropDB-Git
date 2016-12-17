try:
	import tkinter as tk
except:
	import Tkinter as tk
import re
from datetime import datetime

import ProduceError as PE

def _validate_entries(params):
	all_valid = True
	for w,d,l in params:
		if not _validate_entry(w,d,l,write_errors=False):
			all_valid = False
	return all_valid
			
def _validate_entry(widget,datatype,length_constraint=255,write_errors=True):
	value = widget.get()

	def _throw_error(type,widget,color='pink'):
		try:
			widget.config(bg = color)
		except:
			widget.config(background = color)
		#print "Error! Invalid %s. Please check entry/formating." % type
		
	def _show_correct(widget):
		try:
			widget.config(bg = 'white')
		except:
			widget.config(background = 'white')
	
	if len(value) > length_constraint:
		_throw_error(type,widget,color='lemon chiffon')
		if write_errors:
			msg = "Length of entry too long!\nMax length %s -- currently %s" % (length_constraint,len(value))
			
			# This find the root window to produce an error
			parent = widget
			while parent.winfo_parent() != '':
				parentName 	= parent.winfo_parent()
				parent 		= parent._nametowidget(parentName)
			PE.produce_error_popup(parent,msg)
		return False
	
	if value != "":
		if datatype == 'Text':
			_show_correct(widget)
			return True
			
		elif datatype == 'Set':
			_show_correct(widget)
			return True
			
		elif datatype == 'Date':
			try: #year month day
				try:
					datetime.strptime(value,'%Y-%m-%d')
					_show_correct(widget)
					return True
				except:
					pass
				try:
					conv_date = datetime.strptime(value,'%Y/%m/%d').strftime('%Y-%m-%d')
					widget.delete('0',tk.END)
					widget.insert(tk.END,conv_date)
					_show_correct(widget)
					return True
				except:
					pass
			except:
				pass
			try: # month day year
				try:
					conv_date = datetime.strptime(value,'%m-%d-%Y').strftime('%Y-%m-%d')
					widget.delete('0',tk.END)
					widget.insert(tk.END,conv_date)
					_show_correct(widget)
					return True
				except:
					pass
				try:
					conv_date = datetime.strptime(value,'%m/%d/%Y').strftime('%Y-%m-%d')
					widget.delete('0',tk.END)
					widget.insert(tk.END,conv_date)
					_show_correct(widget)
					return True
				except:
					pass
			except:
				pass
				
			_throw_error(datatype,widget)
			return False
			
		elif datatype == 'Integer':
			if len(value) == 10 and value[0:4].isdigit() and value[5] == '-' and value[6:9].isdigit():
				_show_correct(widget)
				return True
			elif value.replace(',','').isdigit():
				if ',' in value:
					widget.delete('0',tk.END)
					widget.insert(tk.END,value.replace(',',''))
				_show_correct(widget)
				return True
			else:
				return False
				
		elif datatype == 'Decimal':
			if re.match(r'^-?\d+(,\d+)*(\.\d+(e\d+)?)?$', value):
				if ',' in value:
					widget.delete('0',tk.END)
					widget.insert(tk.END,value.replace(',',''))
				_show_correct(widget)
				return True
			else:
				_throw_error(datatype,widget)
				return False
				
	try:
		_show_correct(widget)
	except:
		pass
	return True