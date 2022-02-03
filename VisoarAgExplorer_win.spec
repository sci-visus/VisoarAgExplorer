# -*- mode: python ; coding: utf-8 -*-


block_cipher = None



pf_foldr='C:\\Program Files\\Python36\\Lib\\site-packages\\'

relDir = 'C:\\tools\\VisoarAgExplorer\\'
added_files = [
    ( 'token.json', '.' ),
    ( 'userFileHistory.xml', '.' ),
    ( 'client_secret_credentials.json', '.' ),
    ( 'README.md', '.' ),
    ( 'scripts\\*.py', 'scripts' ),
    ( '*.py', '.' ),
	('icons\\*', 'icons'),
]


a = Analysis(['VisoarAgExplorer.py'],
             pathex=[relDir+'StandAloneMAPIR_CameraController',relDir+'slampy\\', relDir+'scripts', relDir+'slampy\\micasense',pf_foldr+'\\OpenVisus', relDir,pf_foldr],
             binaries=[(pf_foldr+'\\OpenVisus\\_VisusDataflowPy.so', 'platforms\\_VisusDataflowPy.so'),
(pf_foldr+'\\OpenVisus\\_VisusDbPy.so', 'platforms\\_VisusDbPy.so'),
(pf_foldr+'\\OpenVisus\\_VisusGuiPy.so', 'platforms\\_VisusGuiPy.so'),
(pf_foldr+'\\OpenVisus\\_VisusKernelPy.so', 'platforms\\_VisusKernelPy.so'),
(pf_foldr+'\\OpenVisus\\_VisusNodesPy.so', 'platforms\\_VisusNodesPy.so') ],
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
            a.binaries,
               a.zipfiles,
               a.datas,
          [('v', None, 'OPTION')],
          exclude_binaries=True,
          name='VisoarAgExplorer',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )




app = BUNDLE(coll,
         name='VisoarAgExplorer.app',
         icon='icons\\visoareye.ico',
         bundle_identifier=None)

