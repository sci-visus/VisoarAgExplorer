# Stand alone MAPIR Image Calibration python code
Based upon code available at: 
https://github.com/mapircamera/MAPIR_Camera_Control

I stripped out all of the UI (QT) code so we can use it on the server to preprocess images for our

ViSOAR Data Portal 

and our 

VisoarAgExplorer Python Interface

https://github.com/sci-visus/VisoarAgExplorer
 
 ##Output
This software creates a Calibration_N folder where N starts at 1 full of newly calibrated images based upon the target image
 
##Install
Included in part of ViSOARAg
https://github.com/sci-visus/VisoarAgExplorer

##Commandline usage 
```
python MAPIR_CalibrateImages.py --target "/path/image" --path "/path/"
 ```
 
 Optional parameters:
  ```
 MAPIR_CalibrateImages.py [-h] [--target TARGET] [--path PATH]
                                [--calibration_camera_model CALIBRATION_CAMERA_MODEL]
                                [--calibration_QR_file CALIBRATION_QR_FILE]
                                [--calibration_filter CALIBRATION_FILTER]
                                [--calibration_lens CALIBRATION_LENS]

MAPIR camera Process target and folder of images.

optional arguments:
  -h, --help            show this help message and exit
  --target TARGET       image containing target
  --path PATH           directory of source images
  --calibration_camera_model CALIBRATION_CAMERA_MODEL
                        Survey3
  --calibration_QR_file CALIBRATION_QR_FILE
                        same as target
  --calibration_filter CALIBRATION_FILTER
                        filter such as OCN
  --calibration_lens CALIBRATION_LENS
                        3.37mm (Survey3W)
  ```

##For usage in an App (like QT UI)

In a class, add a variable for the camera calibration.
 if you are going to use a UI to allow users to provide target image file and path, then you can do:
 ```
self.mapIRCalibrationWidget = MAPIR_ProcessingCLI(parent=self,args='wait')

```
Noting the parameter
```
args = 'wait'
```

which will tell it to not run the calibration when you create the variable.
If you use this, you'll need to explicitly provide the settings via:
 ```
 args = {}
 args['target'] = self.CalibrationQRFile
 args['path'] =  <path to file>
 args['calibration_camera_model']='Survey3'
 args['calibration_QR_file']=<path to file>
 args['calibration_filter']='OCN'
 args['calibration_lens']='3.37mm (Survey3W)'
 
 self.mapIRCalibrationWidget.processArgs(args)
 self.qr_coeffs_index, self.qrcoeffs = self.mapIRCalibrationWidget.generate_calibration(  )
 self.mapIRCalibrationWidget.on_CalibrateButton_released()

```