import cv2

inphoto = "D:/Testing/CustomerIssues/1029_Joe_McGlinchy/PABC00040.tiff"

img = cv2.imread(inphoto, 0)
print(img.max())
print(img.dtype)