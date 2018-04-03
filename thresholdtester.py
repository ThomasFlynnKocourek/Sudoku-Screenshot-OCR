from PIL import Image
#from PIL import ImageFilter
from PIL import ImageDraw
import math
import os
import time
import copy
import numpy as np
import sys


class ImagePreprocesser:
	version = '0.1'
	path = os.path.dirname(os.path.realpath(__file__))
	threshold = 10 #should be between 0 and 255
	gapOverlapCropPercent = 0.05 #the percentage (relative to the size of a gap overlap) to crop from each gap overlap
	minimumLengthPercent = 0.3

	def __init__(self, imageName):
		self.imageName = imageName
		self.image = Image.open(self.path + self.imageName)
		self.imageGray = self.image.convert("L", dither=Image.NONE)
		self.imageBW = self.image.convert('1', dither=Image.NONE)
		self.pixels = self.imageBW.load() #using this to access all pixels is much faster then using getpixel
		self.width, self.height = self.image.size

	def process(self):
		self.detectBackgroundColor()

	def outputGrayColorCounts(self):
		grayColorCounts = self.imageGray.getcolors()
		highCount = 0
		for i in range (0,len(grayColorCounts)):
			if (grayColorCounts[i][0] > highCount):
				highCount = grayColorCounts[i][0]
		print("High color count: ", highCount)
		for i in range(0,100):
			for j in range(0,len(grayColorCounts),1):
				if (grayColorCounts[j][0] >= (highCount * 0.01 * (100 - i) - (highCount * 0.005))):
					print("X",end="")
				else:
					print("-",end="")
			print()

		for i in range(len(grayColorCounts)):
			if (i % 10 == 0):
				print("|",end="")
			else:
				print(" ",end="")


		#for i in range(0, len(grayColorCounts), 2):
			#print("X", end="")
		#	print(i, ": ", grayColorCounts[i][0])

	def detectBackgroundColor(self):
		colorCounts = self.imageBW.getcolors()
		if(colorCounts[1][0] > colorCounts[0][0]):
			self.backgroundColor = 255
		else:
			self.backgroundColor = 0

	def detectLinesVert(self):
		tTime = time.time()

		self.linesVert = []
		
		minimumVertLength = self.height * self.minimumLengthPercent
		
		for x in range(self.width): 
			pixelColor = testData[x][0]
			#pixelColor = self.pixels[x,0]
			lineLength = 0;
			for y in range(self.height):
				previousPixelColor = pixelColor
				pixelColor = testData[x][y]
				#pixelColor = self.pixels[x,y]
				if (pixelColor != self.backgroundColor):
					if (lineLength == 0) :
						lineStart = y
					lineLength = lineLength + 1
				else:
					if (lineLength >= minimumVertLength):
						self.linesVert.append(((x,lineStart),(x,y)))
					lineLength = 0
			if (lineLength >= minimumVertLength):
				self.linesVert.append(((x,lineStart),(x,y)))

	def customThreshold(self, thresholdValue):
		imageGray = self.image.convert('L')
		thresholdArray = np.array(imageGray)	

		thresholdArray[thresholdArray >= thresholdValue] = 255
		thresholdArray[thresholdArray < thresholdValue] = 0
		
		thresholdImage = Image.fromarray(thresholdArray)
		thresholdImage.save(self.path + '\\thresholdtest\\' + str(thresholdValue) + '.png', format="png")

if (len(sys.argv) > 1): 
	ip = ImagePreprocesser(sys.argv[1])
	ip.outputGrayColorCounts()
	ip.process()

	ip.customThreshold(10)
	ip.customThreshold(20)
	ip.customThreshold(30)
	ip.customThreshold(40)
	ip.customThreshold(50)
	ip.customThreshold(60)
	ip.customThreshold(70)
	ip.customThreshold(80)
	ip.customThreshold(90)
	ip.customThreshold(100)
	ip.customThreshold(110)
	ip.customThreshold(120)
	ip.customThreshold(130)
	ip.customThreshold(134)
	ip.customThreshold(140)
	ip.customThreshold(150)
	ip.customThreshold(160)
	ip.customThreshold(170)
	ip.customThreshold(180)
	ip.customThreshold(190)
	ip.customThreshold(200)
	ip.customThreshold(210)
	ip.customThreshold(220)
	ip.customThreshold(230)
	ip.customThreshold(240)
	ip.customThreshold(250)
	


