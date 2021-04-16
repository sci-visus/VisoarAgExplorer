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



# New slam version following Valerio pipeline

Call the python command by:


```
python -m slampy [--remote-dir <value>] [--image-dir <value>] [--cache-dir <value> [--idx-filename <value>]
```

Where:

### --remote-dir (OPTIONAL) 

If you have the data on the cloud (example S3 mounted with CyberDuck or rclone) and you need to download it,us the following :
```
--remote-dir /path/to/remote/images
# example: --remote-dir "G:/visus-agricultural/Field_Images/Blackadder Farms Ptr/Sams 6.24.20"
```

### --image-dir (REQUIRED) 

Specify where the local image directory is:
```
--image-dir /path/to/local/images
# example: --image-dir "D:/visus-slam/visus-agricultural/Field_Images/Blackadder Farms Ptr/Sams 6.24.20"
```

### --cache-dir (OPTIONAL) 

Specify where to store local slam files (useful if you want the slam files in a different directory):
```
--cache-dir /path/to/stitching/directory
# example: --cache-dir "D:/visus-slam/cache-dir/visus-agricultural/Field_Images/Blackadder Farms Ptr/Sams 6.24.20"
````

### --idx-filename (OPTIONAL) 

Specify where to store the final idx files. 
If not specified you will be using MIDX:

```
--idx-filename /path/to/idx/filename
# example: --idx-filename "D:/visus-slam/idx-dir/visus-agricultural/Field_Images/Blackadder Farms Ptr/Sams 6.24.20/visus.idx"
```

As an example, assuming you have a sequence on CyberDuck mounted as `G:` drive:

```
python -m slampy 
	--remote-dir   "G:/visus-agricultural/Field_Images/Blackadder Farms Ptr/Sams 6.24.20" 
	--image-dir    "C:/visus-slam/image-dir/visus-agricultural/Field_Images/Blackadder Farms Ptr/Sams 6.24.20" 
	--cache-dir    "C:/visus-slam/cache-dir/visus-agricultural/Field_Images/Blackadder Farms Ptr/Sams 6.24.20" 
	--idx-filename "C:/visus-slam/visus-dir/visus-agricultural/Field_Images/Blackadder Farms Ptr/Sams 6.24.20/visus.idx"
````