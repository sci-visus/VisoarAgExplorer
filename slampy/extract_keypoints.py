import cv2

from OpenVisus  import *

# //////////////////////////////////////////////////////////////////////////
class ExtractKeyPoints:

	# constructor
	def __init__(self,min_num_keypoints,max_num_keypoints,anms):
		self.detector = cv2.AKAZE.create()
		self.akaze_threshold=self.detector.getThreshold()
		self.min_num_keypoints=min_num_keypoints
		self.max_num_keypoints=max_num_keypoints
		self.anms=anms

	# doExtract
	def doExtract(self, energy):

		T1 = Time.now()

		#detect keypoints
		t2 = Time.now()
		keypoints=[]
		history=[]
		while True:
			if not self.akaze_threshold:
				self.akaze_threshold = .1
			self.detector.setThreshold(self.akaze_threshold)
			keypoints=self.detector.detect(energy)
			N = len(keypoints)
			print("akaze treshold " , self.akaze_threshold , " got " , N , " keypoints")

			# after 4 "zeros" assume the image is simply wrong
			history.append(N)
			if history[-4:]==[0]*4:
				print("Failed to extract keypoints")
				return ([],[])

			if self.min_num_keypoints>0.001 and N < self.min_num_keypoints :
				self.akaze_threshold *= 0.8
				continue

			if self.max_num_keypoints>0.001 and N > self.max_num_keypoints :
				self.akaze_threshold *= 1.2
				continue

			break

		msec_detect = t2.elapsedMsec()

		t2 = Time.now()
		if self.anms>0 and len(keypoints)>self.anms:

			# important!
			# sort keypoints in DESC order by response 
			# remember since anms need them to be in order
			keypoints=sorted(keypoints,key=lambda A: A.response,reverse=True)

			responses=[keypoint.response for keypoint in keypoints]
			xs=[keypoint.pt[0] for keypoint in keypoints]
			ys=[keypoint.pt[1] for keypoint in keypoints]
	
			good_indices = KeyPoint.adaptiveNonMaximalSuppression(responses,xs,ys,self.anms)

			keypoints=[keypoints[it] for it in good_indices]

		msec_anms=t2.elapsedMsec()

		# compute descriptors
		t2 = Time.now()
		keypoints,descriptors=self.detector.compute(energy, keypoints)
		msec_compute = t2.elapsedMsec()

		print("Extracted",len(keypoints), " keypoints"," in " , T1.elapsedMsec() ," msec", "msec_detect", msec_detect, "msec_compute" , msec_compute, "msec_anms",msec_anms)
		return (keypoints,descriptors)
