import os,sys,glob,threading,platform,sysconfig,re,time,subprocess, errno, fnmatch, shutil
import numpy

from OpenVisus import *
from OpenVisus.image_utils import *

try:
	import cv2
except:
	pass

# ////////////////////////////////////////////////////////////////////////////////
def MatrixToNumPy(value):
	ret=numpy.eye(3, 3, dtype=numpy.float32)
	for R in range(3):
		for C in range(3):
			ret[R,C]=value.getRow(R)[C]
	return ret

# ////////////////////////////////////////////////////////////////////////////////
def ComputeImageRange(src):
	if len(src.shape)<3:
		return (numpy.amin(src)),float(numpy.amax(src))
	else:
		return [ComputeImageRange(src[...,C]) for C in range(src.shape[2])]
	
# ////////////////////////////////////////////////////////////////////////////////
def NormalizeImage32f(src):
		
	if len(src.shape)<3:
		dst = numpy.zeros(src.shape, dtype=numpy.float32)
		m,M=ComputeImageRange(src)
		delta=(M-m)
		if delta==0.0: delta=1.0
		return (src.astype('float32')-m)*(1.0/delta)
			
	dst = numpy.zeros(src.shape, dtype=numpy.float32)
	for C in range(src.shape[2]):
		dst[:,:,C]=NormalizeImage32f(src[:,:,C])
	return dst

# ////////////////////////////////////////////////////////////////////////////////
def ConvertImageToGrayScale(img):
	if len(img.shape)>=3 and img.shape[2]==3:
		return cv2.cvtColor(img[:,:,0:3], cv2.COLOR_RGB2GRAY)
	else:
		return img[:,:,0] 

# ////////////////////////////////////////////////////////////////////////////////
def ResizeImage(src,max_size):
	H,W=src.shape[0:2]
	vs=max_size/float(max([W,H]))
	if vs>=1.0: return src
	return cv2.resize(src, (int(vs*W),int(vs*H)), interpolation=cv2.INTER_CUBIC)

# ////////////////////////////////////////////////////////////////////////////////
def ConvertImageToUint8(img):
	if img.dtype==numpy.uint8: 
		return img
	else:
		return (NormalizeImage32f(img) * 255).astype('uint8')

# ////////////////////////////////////////////////////////////////////////////////
def SaveImage(filename,img):
	array=Array.fromNumPy(img, TargetDim=2, bShareMem=True)
	return ArrayUtils.saveImage(filename,array)

# ////////////////////////////////////////////////////////////////////////////////
def SaveUint8Image(filename,img):
	SaveImage(filename, ConvertImageToUint8(img))	

# ////////////////////////////////////////////////////////////////////////////////
def MatchHistogram(img, ref):
	num_channels=img.shape[2] if len(img.shape)==3 else 1

	for i in range(num_channels):
		source = img[:,:,i].ravel()
		reference = ref[:,:,i].ravel()
		orig_shape = ref[:,:,i].shape

		s_values, s_idx, s_counts = numpy.unique(source, return_inverse=True, return_counts=True)
		r_values, r_counts = numpy.unique(reference, return_counts=True)
		s_quantiles = numpy.cumsum(s_counts).astype(numpy.float64) / source.size
		r_quantiles = numpy.cumsum(r_counts).astype(numpy.float64) / reference.size
		interp_r_values = numpy.interp(s_quantiles, r_quantiles, r_values)
		img[:,:,i] = interp_r_values[s_idx].reshape(orig_shape)
