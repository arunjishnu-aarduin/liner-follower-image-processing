
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
camera.framerate = 12
rawCapture = PiRGBArray(camera, size=(250, 250))
# allow the camera to warmup
time.sleep(1)
count=0
skipped_frame=False
initial_skip=5
skip_frame_count=0
direction="k"

index_top=100
index_bottom=249
index_left=10
index_right=240
index_mid = 175

junction=False
junction_T_count=0
junction_plus_count=0

def printFrame(im_bw):
	for x in range(index_top,index_bottom+1):
		
		row_count_black=0
		row_count_white=0
		sys.stdout.write(str(x)+ " : ")
        	for y in range(0,250):
                	if im_bw[x][y] == 0 :
                        	sys.stdout.write("#")
				row_count_black+=1
                        else:
                        	sys.stdout.write(".")
				row_count_white+=1
		sys.stdout.write(" : W = "+str(row_count_white)+": B =  "+str(row_count_black))
                sys.stdout.write("\n")
	



try:
	for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
		# grab the raw NumPy array representing the image, then initialize the timestamp
		# and occupied/unoccupied text
		image_RGB = frame.array
		img_gray = cv2.cvtColor(image_RGB, cv2.COLOR_BGR2GRAY)
		(thresh, im_bw) = cv2.threshold(img_gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
		#(thresh, im_bw) = cv2.threshold(img_gray, 80, 255, cv2.THRESH_BINARY)

		
		if initial_skip >0:
			initial_skip-=1
			print "initial skip"
			rawCapture.truncate(0)
			continue

		if skip_frame_count>0:
			skip_frame_count-=1
			print "frame skip may be a junction ahead"
			rawCapture.truncate(0)
			continue	
		#printFrame(im_bw)
		
		# checking for incompleate frames by taking the count of 10 th row 

		count_b_top=0
		count_b_bottom=0
		count_b_left=0
		count_b_right=0

		for i in range(0,250):
			if im_bw[index_top][i]== 0:
				count_b_top+= 1
			if im_bw[index_bottom][i]==0:
				count_b_bottom+=1
			if im_bw[i][index_left]==0:
				count_b_left+=1
			if im_bw[i][index_right]==0:
				count_b_right+=1
	

		#junction identification 

		if count_b_top == 250 and count_b_bottom != 250 :
			skipped_frame= True
			print "skipped frame First ! "
			 # clear the stream in preparation for the next frame
		        rawCapture.truncate(0)
			printFrame(im_bw)
			continue
		# T,+ junction
		if skipped_frame==True:
			print "\t top = "+ str(count_b_top)
	                print "\tleft = "+str(count_b_left)
                	print "\tright =  "+ str(count_b_right)
                	print "\tbottom = "+str(count_b_bottom)
                	printFrame(im_bw)
                	


		if skipped_frame==True and count_b_top < 10 and count_b_left > 50 and count_b_right >50 and count_b_bottom >50:
			print "T junction identified "
			junction_T_count+=1
			junction=True
			#junctionControl("r")
			skip_frame_count=10

		elif skipped_frame==True and count_b_top > 50 and count_b_left > 50 and count_b_right >50 and count_b_bottom >50:
			print " + junction identified "
			junction_plus_count+=1
			junction=True
			#junctionControl("r")
			left(0)
			skip_frame_count=10
			printFrame(im_bw)

		if junction==False:
			if im_bw[175][41]==0  and im_bw[175][209]==255:
				left(0)
				direction="l"
				#stop()
			elif im_bw[175][41]==255   and im_bw[175][209]==0:
				right(0)
				direction="r"
				#stop()
			elif im_bw[175][41]==255 and im_bw[175][125]==0  and im_bw[175][209]==255:
				forward(0)
			else:
				print "unknown condition"
				follow_previous_direction(direction)
				#printFrame(im_bw)
				#break
		skipped_frame=False
		junction=False

		#clear the stream in preparation for the next frame
		rawCapture.truncate(0)

	
	

	

except KeyboardInterrupt:
	print "\n T = "+str(junction_T_count)+"\n + =  "+str(junction_plus_count)
	stop()
	exit(True)
