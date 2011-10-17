#!/usr/bin/env python

'''
ffmpeg -i renderframes/example1a_%3d.png video/example1a.mpg

For better quality output:

ffmpeg -i renderframes/example1a_%3d.png -b 98000 video/example1a.avi

'''

import Image, ImageDraw
import random
import sys

width = 720
height = 576
bgColour = (255, 255, 255)
imageFormat = "RGB"
fileFormat = "PNG"
renderFiles = 'renderframes'
animName = 'afd'
block_pos =((400,200,450,250),
			(330,200,380,250),
			(260,200,310,250),
			(190,200,240,250),
			(120,200,170,250),
			(50,200,100,250))
block_color = ( (0,0,0),
				(255,0,0),
				(0,0,255),
				(0,255,0),
				(255,255,0),
				(255,0,255),
				(128,128,128),
				(0,255,255),
				(255,128,0),
				(255,255,255) )

def drawFrame(image, framenum):
	"""
	Draws a single frame within the animation.
	"""
	
	# create drawing surface
	drawImage = ImageDraw.Draw(image)
	# define a color for each block
	red = random.randint(0, 255)
	green = random.randint(0, 255)
	blue = random.randint(0, 255)
	for block in block_pos:
		digit = framenum%10
		framenum = framenum / 10
		print "(%d,%d)" % (digit, framenum)
		print "(%d,%d,%d)" % block_color[digit]
		drawImage.rectangle(block[:4], fill=block_color[digit])
	
	
def writeFrame(image, frameNumber):
	"""
	Writes frame image to file.
	"""
	# format number with zero padding: 001, 002, etc
	fileNumber = str(frameNumber).zfill(3)
	# create filename for frame
	frameFilename = '%s/%s_%s.%s' % (renderFiles, animName, fileNumber, fileFormat.lower())
	# write file
	image.save(frameFilename, fileFormat)
	
	
if __name__ == '__main__':
	# set number of frames
	try:
		# get number from command line
		frames = int(sys.argv[1])
	except:
		# or set default value
		frames = 60
		
	# tell the user how many frames are going to be rendered
	print "rendering %d frames ..." % frames
	
	# create a loop and draw the animation frames
	for frameNumber in range(frames):
		# tell user the frame number
		print "frame %d" % frameNumber
		# create image
		image = Image.new(imageFormat, (width, height), bgColour)
		# draw frame
		drawFrame(image, frameNumber)
		# save frame
		writeFrame(image, frameNumber)
		
	# tell the user we have finished
	print "%d frames rendered." % frames