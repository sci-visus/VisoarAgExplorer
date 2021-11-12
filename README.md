# VisoarAgExplorer
VisoarAgExplorer Python Interface

#Get a copy of the 

    visus_google.py 
    
    file from the developers by emailing Amy

#Install zip  

- For Windows:   TBP
- For Mac: TBP

- Need to address how to install necessary parts from MapIR Calibration
  
  -- Currently that means issues with exiftool.exe
  
#Install for Windows:

```
python -m pip install  --upgrade pip

pip install  -r MAPIR_CameraController/requirements.txt 
pip install   -r requirements.txt 

python -m pip install   --no-cache-dir --upgrade --force-reinstall OpenVisus
python -m OpenVisus configure  

python -m pip install  google-api-python-client oauth2client PyDrive opencv-contrib-python
```

#Install OpenVisus y package:

```
python -m pip install --user --upgrade pip

pip install --user  -r MAPIR_CameraController/requirements.txt 
pip install --user  -r requirements.txt 

python -m pip install  --user --no-cache-dir --upgrade --force-reinstall OpenVisus
python -m OpenVisus configure  --user 

python -m pip install --user google-api-python-client oauth2client PyDrive opencv-contrib-python
```
    
For Windows only. You need to install Visual Studio redistributable 

```
http://download.microsoft.com/download/c/c/2/cc2df5f8-4454-44b4-802d-5ea68d086676/vcredist_x64.exe.
```

You may need to put the path for the repository in your PATH

If you have errors with hidraw, download the release and put it in the environment variable path
```
https://github.com/libusb/hidapi/releases
```

If you have an error about exiftool:
```
pip install git+https://github.com/smarnach/pyexiftool.git#egg=pyexiftool

```


FOR MACOS ONLY, you may need to solve conflicts between Qt embedded in opencv2 and PyQt5:

```
python -m pip uninstall -y opencv-python opencv-contrib-python opencv-python-headless opencv-contrib-python-headless
python -m pip install   --user     opencv-python-headless opencv-contrib-python-headless 
```



Documentation for  OpenVisus if above fails `https://github.com/sci-visus/OpenVisus/blob/master/README.md`.



Then grab this code:

```
git clone https://github.com/sci-visus/VisoarAgExplorer.git
```


Install helper libraries:
`cd` to directory where this code lives:

```
pip install --user  -r MAPIR_CameraController/requirements.txt 
pip install --user  -r requirements.txt 

```


then you can run this simply by:

```
python VisoarAgExplorer.py 
```


Note:  it saves what you have loaded in an xml file:


```
userFileHistory.xml
```

you may need to edit this file to remove non-working files or links
(and it is not initialized to be correct when you grab this repo;
its on my to do list.)

if the file doesn't exist and you get an error:

```
cp userFileHistory_BK.xml userFileHistory.xml
```

Send bug requests to `Amy@visus.net`


# DEVELOPER only

```
pip freeze > requirements.txt
```


### New Laptop Install:

You will need to:

- install python 3.6.8
- install git 
- install teamviewer

may have to:

```
python -m pip install  --user --upgrade pip setuptools # IMPORTANT (!)
python -m pip uninstall pymap3d 
python -m pip install  --user --no-cache-dir --upgrade --force-reinstall pymap3d
```


#OpenViSUS

# For Linux sometimes you have to install some python libraries 
# sudo apt-get install python3.6 libpython3/6

```
python -m pip install --user --upgrade OpenVisus
python -m OpenVisus configure --user
python -m OpenVisus viewer
```

# SLAM

```
brew install exiftool zbar 
```

# Visus_google.py and other secrets
Because we are enabling uploading to google, one needs a copy of the certificate validation infomation
Ask the developers for a copy of the files

#If have trouble with PyQT:
``` 

 
python -m pip uninstall PyQtWebEngine
python -m pip uninstall PyQt5 
python -m pip uninstall PyQt5-sip 
python -m pip install PyQt5  
python -m pip install PyQt5-sip  
python -m pip install PyQtWebEngine
python -m pip install PyQt5  
python -m pip install PyQt5-sip  
python -m pip install PyQtWebEngine
python -m pip install --upgrade OpenVisus
python -m OpenVisus configure 

```

#If have error:
```error Microsoft Visual C++ 14.0 is required```

 see
https://www.scivision.dev/python-windows-visual-c-14-required
