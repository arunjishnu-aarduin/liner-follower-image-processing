
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np

from motorControl import *
import sys


np.set_printoptions(threshold=np.nan)
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (250,250)
camera.framerate = 10
rawCapture = PiRGBArray(camera, size=(250, 250))
# allow the camera to warmup
time.sleep(1)
count=0
skipped_frame=False
initial_skip=5
skip_frame_count=0
direction="k"

def follow_previous_direction():
                        if direction=="r":
                                right(0)
                                time.sleep(0.05)
                                stop()
                        elif direction=="l":
                                left(0)
                                time.sleep(0.05)
                                stop()


def printFrame(im_bw):
	for x in range(0,250):
        	for y in range(0,250):
                	if im_bw[x][y] == 0 :
                        	sys.stdout.write("#")
                        else:
                        	sys.stdout.write(".")
                sys.stdout.write("\n")
	print "\n\n-------------------------------------------------------------------------------------------------------------\n\n"



def directRobot(count_b_top,count_b_bottom,count_b_left,count_b_right,skipped_frame):

                print "\n\n-------------------------------------------------------------------------------------------------------------\n"
                print "\t\t\t top = "+ str(count_b_top)
                print "left = "+str(count_b_left)
                print "\t\t\t\t\t\tright =  "+ str(count_b_right)
                print "\t\t\tbottom = "+str(count_b_bottom)
		


try:
	for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
		# grab the raw NumPy array representing the image, then initialize the timestamp
		# and occupied/unoccupied text
		image_RGB = frame.array
		#print "image RGB"
		img_gray = cv2.cvtColor(image_RGB, cv2.COLOR_BGR2GRAY)
		#print img_gray
		#(thresh, im_bw) = cv2.threshold(img_gray, 50, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
		(thresh, im_bw) = cv2.threshold(img_gray, 80, 255, cv2.THRESH_BINARY)
		#print thresh
		#print im_bw
		#printFrame(im_bw)
		
		if initial_skip >0:
			initial_skip-=1
			print "initial skip"
			rawCapture.truncate(0)
			continue	

		if skip_frame_count>0:
			skip_frame_count-=1
			print "frame skip due to junction"
			rawCapture.truncate(0)
			continue	
		count+=1


		# checking for incompleate frames by taking the count of 10 th row 
		w_count=0

		count_b_top=0
		count_b_bottom=0
		count_b_left=0
		count_b_right=0

		for i in range(0,250):
			if im_bw[10][i]== 255:
				w_count+= 1
			if im_bw[10][i]==0:
				count_b_top+=1
			if im_bw[240][i]==0:
				count_b_bottom+=1
			if im_bw[i][10]==0:
				count_b_left+=1
			if im_bw[i][240]==0:
				count_b_right+=1
		#print "count of w = " + str(w_count)
		
		if w_count < 10:
			skipped_frame= True
			print "\t\t\tskipped frame--white count = "+str(w_count)
			#follow_previous_direction()
			stop()
			#break
			forward(0)
			skip_frame_count=5
			
			 # clear the stream in preparation for the next frame
			#cv2.imwrite("skipped_Frame"+str(count)+".jpg",image_RGB)

		        rawCapture.truncate(0)

			continue

		
		exit=directRobot(count_b_top,count_b_bottom,count_b_left,count_b_right,skipped_frame)
		if exit :
			print "break"
			stop()
			#break
		skipped_frame=False
		
		#printFrame(im_bw)
		#clear the stream in preparation for the next frame
		rawCapture.truncate(0)

	
	

	

except KeyboardInterrupt:
	print "Goodbye"
	stop()
	exit()
