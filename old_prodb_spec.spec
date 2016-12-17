		  # -*- mode: python -*-

block_cipher = None

added_files = [
			('icons/*.png','icons'),
			('icons/*.ico','icons'),
			]

a = Analysis(['PropertyDB_2.py'],
             pathex=['D:\\PythonProjects\\PropDB'],
             binaries=None,
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='PropertyDB_2',
          debug=False,
		  icon='D:\\PythonProjects\\PropDB\\icons\\icon.ico',
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='PropertyDB_2')