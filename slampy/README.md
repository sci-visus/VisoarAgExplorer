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


