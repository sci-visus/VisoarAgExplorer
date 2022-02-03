# -*- mode: python ; coding: utf-8 -*-


block_cipher = None



pf_foldr='/Users/amygooch/.pyenv/versions/3.8.8/lib/python3.8/site-packages'
added_files = [
    ( 'token.json', '.' ),
    ( 'userFileHistory.xml', '.' ),
    ( 'client_secret_credentials.json', '.' ),
    ( 'README.md', '.' ),
    ( 'scripts/*.py', 'scripts' ),
    ( '*.py', '.' ),
	('icons/*', 'icons'),
]


a = Analysis(['VisoarAgExplorer.py'],
             pathex=['/Users/amygooch/GIT/ViSOARAgExplorer_SCI/StandAloneMAPIR_CameraController','/Users/amygooch/GIT/ViSOARAgExplorer_SCI/slampy/', '/Users/amygooch/GIT/ViSOARAgExplorer_SCI/scripts', '/Users/amygooch/GIT/ViSOARAgExplorer_SCI/slampy/micasense','/Users/amygooch/.pyenv/versions/3.8.8/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages/OpenVisus'],
             binaries=[('/Users/amygooch/.pyenv/versions/3.8.8/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages/OpenVisus/_VisusDataflowPy.so', 'platforms/_VisusDataflowPy.so'), 
('/Users/amygooch/.pyenv/versions/3.8.8/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages/OpenVisus/_VisusDbPy.so', 'platforms/_VisusDbPy.so'), 
('/Users/amygooch/.pyenv/versions/3.8.8/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages/OpenVisus/_VisusGuiPy.so', 'platforms/_VisusGuiPy.so'),
('/Users/amygooch/.pyenv/versions/3.8.8/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages/OpenVisus/_VisusKernelPy.so', 'platforms/_VisusKernelPy.so'),
('/Users/amygooch/.pyenv/versions/3.8.8/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages/OpenVisus/_VisusNodesPy.so', 'platforms/_VisusNodesPy.so'),
('/Users/amygooch/GIT/VisoarAgExplorerMay/myenv/lib/python3.6/site-packages/PyQt5/Qt/plugins/platforms/libqcocoa.dylib', 'platforms/libqcocoa.dylib')],
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
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )

 
a.binaries += [ ('cocoa', '/Users/amygooch/GIT/VisoarAgExplorerMay/myenv/lib/python3.6/site-packages/PyQt5/Qt/plugins/platforms/libqcocoa.dylib', 'BINARY' ) ]
a.binaries += [ ('libqcocoa', '/Users/amygooch/GIT/VisoarAgExplorerMay/myenv/lib/python3.6/site-packages/PyQt5/Qt/plugins/platforms/libqcocoa.dylib', 'BINARY' ) ]
a.binaries += [ ('libqcocoa.dylib', '/Users/amygooch/GIT/VisoarAgExplorerMay/myenv/lib/python3.6/site-packages/PyQt5/Qt/plugins/platforms/libqcocoa.dylib', 'BINARY' ) ]

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='VisoarAgExplorer')


app = BUNDLE(coll,
         name='VisoarAgExplorer.app',
         icon='icons/visoareye.ico',
         bundle_identifier=None)

