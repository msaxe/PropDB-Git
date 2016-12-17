import os,sys

def resource_path(relative):
	try:
		if hasattr(sys, "_MEIPASS") or getattr(sys, 'frozen', False):
			return os.path.join(sys._MEIPASS, relative)
		return os.path.join(relative)
	except:
		return os.path.join(relative)