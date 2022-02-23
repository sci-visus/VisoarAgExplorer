# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


pf_foldr=' c:\\users\\drone\\appdata\\local\\packages\\pythonsoftwarefoundation.python.3.8_qbz5n2kfra8p0\\localcache\\local-packages\\python38\\site-packages'
pyqtPath = pf_foldr+'\\PyQt5\\Qt5\\bin\\'
visusPath = pf_foldr+'\\OpenVisus\\bin\\'
relDir = 'C:\\tools\\VisoarAgExplorer\\'
added_files = [
    ( 'token.json', '.' ),
    ( 'userFileHistory.xml', '.' ),
    ( 'client_secret_credentials.json', '.' ),
    ( 'README.md', '.' ),
    ( 'scripts\\*.py', 'scripts' ),
    ( '*.py', '.' ),
	('icons\\*', 'icons'),
	('data', '.')
]

dlls = [('LIBPQ.dll','C:\\Program Files\\PostgreSQL\\14\\bin\\libpq.dll','BINARY'),
('Qt5MultimediaQuick.dll',pyqtPath+'Qt5MultimediaQuick.dll','BINARY'),
('Qt53DQuickScene2D.dll',pyqtPath+'Qt53DQuickScene2D.dll','BINARY'),
('Qt53DCore.dll',pyqtPath+'Qt53DCore.dll','BINARY'),
('Qt53DRender.dll',pyqtPath+'Qt53DRender.dll','BINARY'),
('Qt53DInput.dll',pyqtPath+'Qt53DInput.dll','BINARY'),
('Qt53DLogic.dll',pyqtPath+'Qt53DLogic.dll','BINARY'),
('Qt53DCore.dll',pyqtPath+'Qt53DCore.dll','BINARY'),
('Qt53DAnimation.dll',pyqtPath+'Qt53DAnimation.dll','BINARY'),
('VisusGui.dll',visusPath+'VisusGui.dll','BINARY'),
('VisusKernel.dll',visusPath+'VisusKernel.dll','BINARY'),
('VisusDataflow.dll',visusPath+'VisusDataflow.dll','BINARY'),
('VisusKernel.dll',visusPath+'VisusKernel.dll','BINARY'),
('VisusDataflow.dll',visusPath+'VisusDataflow.dll','BINARY'),
('VisusDb.dll',visusPath+'VisusDb.dll','BINARY'),
('VisusNodes.dll',visusPath+'VisusNodes.dll','BINARY'),]

mybinaries=[('C:\\Program Files\\PostgreSQL\\14\\bin\\libpq.dll','platforms\\libpq.dll'),
(visusPath+'VisusGui.dll' ,'platforms\\VisusGui.dll'),
(visusPath+'VisusKernel.dll' ,'platforms\\VisusKernel.dll'),
(visusPath+'VisusDataflow.dll','platforms\\VisusDataflow.dll'),
(visusPath+'VisusKernel.dll','platforms\\VisusKernel.dll' ),
(visusPath+'VisusDataflow.dll','platforms\\VisusDataflow.dll' ),
(visusPath+'VisusDb.dll','platforms\\VisusDb.dll' ),
(visusPath+'VisusNodes.dll','platforms\\VisusNodes.dll'),]

a = Analysis(['VisoarAgExplorer.py'],
             pathex=['C:\\Program Files\\PostgreSQL\\14\\bin', 'C:\\tools\\tmp', pf_foldr+'\\OpenVisus\\bin', pyqtPath, relDir+'StandAloneMAPIR_CameraController',relDir+'slampy', relDir+'scripts', relDir+'slampy\\micasense',pf_foldr+'\\OpenVisus', relDir,pf_foldr],
             binaries=[],
             datas=added_files,
             hiddenimports=['PyQt5','PyQt5.QtWidgets','PyQt5.QtGui','PyQt5.QtCore'],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [('v', None, 'OPTION')],
          exclude_binaries=True,
          name='VisoarAgExplorer',
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
          entitlements_file=None )




coll = COLLECT(exe,
                a.binaries+dlls,
                a.zipfiles,
                a.datas,
         name='VisoarAgExplorer.app',
         icon='icons\\visoareye.ico',
         bundle_identifier=None)

