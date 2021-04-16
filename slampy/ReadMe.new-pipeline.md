
New slam version following Valerio pipeline

Call the python command by:


```
python -m slampy <args>
```

Where args are the following:

### (OPTIONAL) If you have the data on the cloud (example S3 mounted with CyberDuck or rclone) and you need to download it,us the following :
```
--remote-dir /path/to/remote/images

EXAMPLE:
   --remote-dir "G:/visus-agricultural/Field_Images/Blackadder Farms Ptr/Sams 6.24.20"
```

### (NEEDED) Specify where the local image directory is:
```
--image-dir /path/to/local/images

EXAMPLE:
   --image-dir "D:/visus-slam/visus-agricultural/Field_Images/Blackadder Farms Ptr/Sams 6.24.20"
```

### (OPTIONAL) Specify where to store local slam files (useful if you want the slam files in a different directory):
```
--cache /path/to/stitching/directory

EXAMPLE:
    --cache-dir "D:/visus-slam/cache-dir/visus-agricultural/Field_Images/Blackadder Farms Ptr/Sams 6.24.20"
````

### (OPTIONAL) Specify where to store the final idx files. If not specified you will be using MIDX:

```
--idx-filename /path/to/idx/filename

EXAMPLE:
   --idx-filename "D:/visus-slam/idx-dir/visus-agricultural/Field_Images/Blackadder Farms Ptr/Sams 6.24.20/visus.idx"
```

As an example, assuming you have a sequence on CyberDuck mounted as `G:` drive:

```
python -m slampy 
	--remote-dir   "G:/visus-agricultural/Field_Images/Blackadder Farms Ptr/Sams 6.24.20" 
	--image-dir    "C:/visus-slam/image-dir/visus-agricultural/Field_Images/Blackadder Farms Ptr/Sams 6.24.20" 
	--cache-dir    "C:/visus-slam/cache-dir/visus-agricultural/Field_Images/Blackadder Farms Ptr/Sams 6.24.20" 
	--idx-filename "C:/visus-slam/visus-dir/visus-agricultural/Field_Images/Blackadder Farms Ptr/Sams 6.24.20/visus.idx"
````