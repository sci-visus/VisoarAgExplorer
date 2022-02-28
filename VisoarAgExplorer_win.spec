# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

#pf_foldr=' c:\\users\\drone\\appdata\\local\\packages\\pythonsoftwarefoundation.python.3.8_qbz5n2kfra8p0\\localcache\\local-packages\\python38\\site-packages'
pf_foldr='C:\\Program Files\\Python38\\Lib\\site-packages'
pyqtPath = pf_foldr+'\\PyQt5\\Qt5\\bin\\'
pyqtPath2 = pf_foldr+'\\PyQt5\\'
visusPath = pf_foldr+'\\OpenVisus\\'
relDir = 'C:\\tools\\VisoarAgExplorer\\'
added_files = [
    ( 'token.json', '.' ),
    ( 'userFileHistory.xml', '.' ),
    ( 'client_secret_credentials.json', '.' ),
    ( 'README.md', '.' ),
    ( 'scripts\\*.py', 'scripts' ),
    ( 'slampy\\*', 'slampy' ),
    ( '*.py', '.' ),
	('icons\\*', 'icons'),
	('data', '.')
]

mybinaries2=[('C:\\Program Files\\PostgreSQL\\14\\bin\\libpq.dll','.'),
('C:\\Program Files\\Python38\\Lib\\site-packages\\pyzbar\\libiconv.dll', '.'),
('C:\\Program Files\\Python38\\Lib\\site-packages\\pyzbar\\libzbar-64.dll', '.'),
('C:\\Program Files\\Python38\\hidapi.dll', '.'),
(visusPath+'bin\\VisusGui.dll' ,'OpenVisus\\bin\\'),
(visusPath+'bin\\VisusKernel.dll' ,'OpenVisus\\bin\\'),
(visusPath+'bin\\VisusDataflow.dll','OpenVisus\\bin\\'),
(visusPath+'bin\\VisusKernel.dll','OpenVisus\\bin\\'),
(visusPath+'bin\\VisusDataflow.dll','OpenVisus\\bin\\' ),
(visusPath+'bin\\VisusDb.dll','OpenVisus\\bin\\' ),
(visusPath+'bin\\VisusNodes.dll','OpenVisus\\bin\\'),]

a = Analysis(['VisoarAgExplorer.py'],
             pathex=[visusPath,visusPath+'bin\\',pf_foldr+'\\google-api-python-client',pyqtPath2,'C:\\Program Files\\PostgreSQL\\14\\bin', relDir+'StandAloneMAPIR_CameraController',relDir+'slampy', relDir+'scripts', relDir+'slampy\\micasense\\',],
             binaries=mybinaries2,
             datas=added_files,
             hiddenimports=['PyQt5','PyQt5.QtWidgets','PyQt5.QtGui','PyQt5.QtCore','googleapiclient',],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

#             pathex=[pyqtPath2,'C:\\Program Files\\PostgreSQL\\14\\bin', 'C:\\tools\\tmp', pf_foldr+'\\OpenVisus\\bin\\', pyqtPath, relDir+'StandAloneMAPIR_CameraController',relDir+'slampy', relDir+'scripts', relDir+'slampy\\micasense\\',pf_foldr+'\\OpenVisus\\', relDir,pf_foldr],

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [('v', None, 'OPTION')],
          exclude_binaries=True,
          name='VisoarAgExplorer.exe',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir='C:\\tools\\tmp',
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None,
            icon='icons\\visoareye.ico',)

coll = COLLECT(exe,
                a.binaries,
                a.zipfiles,
                a.datas,
         name='VisoarAgExplorer.app',
         icon='icons\\visoareye.ico',
         bundle_identifier=None)
