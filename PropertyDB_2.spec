# -*- mode: python -*-

added_files = [
			('icons/*.*','icons'),
			('AboutDocs/*.*','AboutDocs'),
			]

block_cipher = None

a = Analysis(['PropertyDB_2.py'],
             pathex=['D:\\PythonProjects\\PropDB'],
             binaries=[],
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
          a.binaries,
          a.zipfiles,
          a.datas,
          name='PropertyDB_2',
          debug=False,
		  icon='D:\\PythonProjects\\PropDB\\icons\\icon.ico',
          strip=False,
          upx=True,
          console=False
		  )
