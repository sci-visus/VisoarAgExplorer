`

##  VisusSlam

On osx install prerequisites:

``` 
brew install exiftool zbar 
```


Install OpenVisus / slampy package:

``` 
python -m pip install --upgrade pip
python -m pip install --no-cache-dir --upgrade --force-reinstall OpenVisus
python -m OpenVisus configure

python -m pip install git+https://github.com/sci-visus/slampy
```

For Windows only. You need to install Visual Studio redistributable `http://download.microsoft.com/download/c/c/2/cc2df5f8-4454-44b4-802d-5ea68d086676/vcredist_x64.exe`.

FOR MACOS ONLY, you may need to solve conflicts between Qt embedded in opencv2 and PyQt5:
```
python -m pip uninstall -y opencv-python opencv-contrib-python opencv-python-headless opencv-contrib-python-headless
python -m pip install      opencv-python-headless opencv-contrib-python-headless 
```


Finally run slam:

```
python -m slampy
```

## Notes for developers

```
python -m pip install numpy matplotlib pymap3d pytz pyzbar scikit-image scipy pysolar json-tricks cmapy tifffile pyexiftool opencv-python opencv-contrib-python
PYTHONPATH=.\build\RelWithDebInfo;.\Libs
python -m slampy --directory [D:\GoogleSci\visus_slam\TaylorGrant]
```


# Command line help

![Screenshot](C:/projects/OpenVisus/VisoarAgExplorer/slampy/resources/images/server-pipeline.png)


Call the slampy command by:

```
python -m slampy \
	[--batch] \
	[--remote-dir <value>] \
	[--image-dir <value>] \
	[--cache-dir <value> \
	[--idx-filename <value>]
```


Linux example (`DroneWasabi` is an rclone configured item):
```
name=/visus-agricultural/Field_Images/Blackadder Farms Ptr/Sams 6.24.20
python -m slampy \
	--batch \
	--remote-dir   "DroneWasabi:$name" \
	--image-dir    "C:/visus-slam/image-dir$name" \
	--cache-dir    "C:/visus-slam/cache-dir$name" \
	--idx-filename "C:/visus-slam/final-dir$name/visus.idx"
````

Windows example (`G:` is a CyberDuck mounted drive):

```
set name=/visus-agricultural/Field_Images/Blackadder Farms Ptr/Shape Behind Toris
python -m slampy ^
	--batch ^
	--remote-dir   "WasabiDrone:%name%" ^
	--image-dir    "C:/visus-slam/image-dir%name%" ^
	--cache-dir    "C:/visus-slam/cache-dir%name%" ^
	--idx-filename "C:/visus-slam/final-dir%name%/visus.idx"
```

### (REQUIRED) `--image-dir  /path/to/local/images` 

Specify where the image directory is. Example:
```
--image-dir "D:/visus-slam/visus-agricultural/Field_Images/Blackadder Farms Ptr/Sams 6.24.20"
```

### (OPTIONAL)`--remote-dir /path/to/remote/images`  

If you have the data on the cloud and you need to download data into `--image-dir` **before** the stitching. It can be a mounted drive 
(`rclone mount` or cyberduck mount) or a simple rclone item.

Note: `rclone` but be **installed and configured properly**. Examples:
```
rclone item    :  --remote-dir "WasabiDrone:/visus-agricultural/Field_Images/Blackadder Farms Ptr/Sams 6.24.20"
rclone mount   :  --remote-dir "G:/visus-agricultural/Field_Images/Blackadder Farms Ptr/Sams 6.24.20"
cyberduck mount:  --remote-dir "H:/visus-agricultural/Field_Images/Blackadder Farms Ptr/Sams 6.24.20"
```

### (OPTIONAL)  `--cache-dir /path/to/stitching/directory` 

Specify where to store local slam files (useful if you want the slam files in a different directory). Example:
```
--cache-dir "D:/visus-slam/cache-dir/visus-agricultural/Field_Images/Blackadder Farms Ptr/Sams 6.24.20"
````

### (OPTIONAL)`--idx-filename /path/to/idx/filename`  

Specify where to store the final idx files. 
If not specified you will be using MIDX. Example:

```
--idx-filename "D:/visus-slam/idx-dir/visus-agricultural/Field_Images/Blackadder Farms Ptr/Sams 6.24.20/visus.idx"
```

