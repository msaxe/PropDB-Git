from distutils.core import setup
import py2exe, sys, os

#sys.argv.append('py2exe')

#setup(windows=[{'script':'V:\web_design\leases_n_liscense\PropertyDB.py','icon_resources':[(1,'V:\web_design\leases_n_liscense\icons\icon.ico')]}])

Mydata_files = []
for files in os.listdir('D:\\PythonProjects\\PropDB\\icons\\'):
	f1 = 'D:\\PythonProjects\\PropDB\\icons\\' + files
	if os.path.isfile(f1) and (f1.endswith('.png') or f1.endswith('.ico')): # skip directories
		f2 = 'icons', [f1]
		Mydata_files.append(f2)

setup(
	name='PropertyDB',
	windows=[
				{
				'script':'D:\PythonProjects\PropDB\PropertyDB_2.py',
				'icon_resources': [(1,'D:\PythonProjects\PropDB\icons\icon.ico')]
				}
			],
	data_files = Mydata_files,
	options={
			'py2exe':{
					'includes' : ['email.mime.multipart','email.mime.text'],
					'dll_excludes': ["MSVCP90.dll", "HID.DLL", "w9xpopen.exe"],
					'bundle_files': 2,
					'optimize': 2,
					'compressed': True				
					}	
			},
	zipfile=None,
	)

# setup(
	# options = {
		# 'py2exe':{
			# 'compressed': 2,
			# 'optimize': 2,
			# #'includes': 'DataBase.py,
			# #'packages': packages,
			# 'bundle_files': 1,  # 1 = .exe; 2 = .zip; 3 = separate
		# }
	# },
	# zipfile = None,
	# windows = [
		# {
			# 'script':'V:\web_design\leases_n_liscense\PropertyDB.py',
			# 'icon_resources':[(1,'V:\web_design\leases_n_liscense\icons\icon.ico')]
		# }
	# ],
# )