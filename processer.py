from PIL import Image
#from PIL import ImageFilter
from PIL import ImageDraw
from PIL import ImageFont

import math
import os
import time
import copy
import numpy as np
import sys
import cv2
import subprocess
import re
import platform

import SudokuSolver

class ImageProcesser:
	#An OCR preprocesser for screenshots that contain sudoku puzzles.
	#The screenshot is processed to find the grid. 
	#If the grid is found then it is chopped up to isolate individual letters.
	#The letters are then isolated in 81 individual images and saved so that they can be processed by an OCR program.

	version = '0.1'
	path = os.path.dirname(os.path.realpath(__file__))
	progressFolder = "/progress/"
	tempFolder = "/temp/"
	if (platform.system() == "Windows"):
		progressFolder = "\\progress\\"
		tempFolder = "\\temp\\"



	threshold = 128 #should be between 0 and 255

	gapOverlapCropPercent = 0.13 #the percentage (relative to the size of a gap overlap) to crop from each side of the gap overlap
	minimumLengthPercent = 0.3	#the size of the image is multiplied by this number to determine the minimum line length
	lineDetectionScale = 0.1	#resizes image by this scale to make line detection quicker
	commonPercent = 0.02		#gaps within commonPercent of the most common gaps are included in the most common gap size lists
	lineSpacePercent = 0.0015		#percentage relative to the size of the image that determines the maximum size of a space when detecting lines
	lineSpaceSumPercent = 0.004		#percentage relative to the size of the image that determines the maximum size of the sum of line spaces when detecting lines
	minVertGapSize = 8
	minHorGapSize = 8
	saveProgress = False

	def __init__(self, imageName):
		self.imageName = imageName
		self.image = Image.open(self.path + self.imageName)
		self.width, self.height = self.image.size
		self.originalWidth = self.width
		self.originalHeight = self.height
		self.imageGray = self.image.convert('L')
		self.sudokuBoard = ""
		self.repairedBoard = ""
		self.solvedBoard = ""

		self.resizeImageTime = 0
		self.binarizeTime = 0
		self.detectLinesVertTime = 0
		self.detectLinesHorTime = 0
		self.detectGapsVertTime = 0
		self.detectGapsHorTime = 0
		self.detectMostCommonGapsVertTime = 0
		self.detectMostCommonGapsHorTime = 0
		self.detectGapOverlapTime = 0
		self.convertOverlapGapsTime = 0
		self.saveGapOverlapImagesTime = 0
		self.detectNumbersTime = 0
		self.saveProgressImagesTime = 0

		self.mostCommonVertGaps = []
		self.mostCommonHorGaps = []
		self.detectMostCommonGapsVertTime = 0
		self.detectMostCommonGapsHorTime = 0

	def process(self):
		self.resizeImage()
		self.binarize()
		self.detectBackgroundColor()
		self.detectLinesVert()
		if (len(self.linesVert) < 2 and self.saveProgress == False):
			return
		self.detectLinesHor()
		if (len(self.linesHor) < 2 and self.saveProgress == False):
			return
		self.detectGapsVert()
		if (len(self.vertGaps) < 3 and self.saveProgress == False):
			return
		self.detectGapsHor()
		if (len(self.horGaps) < 3 and self.saveProgress == False):
			return

		self.detectMostCommonGapsVert()
		while (len(self.mostCommonVertGaps) < len(self.vertGaps) and self.commonPercent <= 0.20 and len(self.mostCommonVertGaps) != 3 and len(self.mostCommonVertGaps) != 9):
			self.commonPercent += 0.1
			self.detectMostCommonGapsVert()
		self.commonPercent = 0.02
		if ((len(self.mostCommonVertGaps) != 3 and len(self.mostCommonVertGaps) != 9 or self.mostCommonVertGapSize <= 6) and self.saveProgress == False):
			return


		self.detectMostCommonGapsHor()
		while (len(self.mostCommonHorGaps) < len(self.horGaps) and self.commonPercent <= 0.20 and len(self.mostCommonHorGaps) != 3 and len(self.mostCommonHorGaps) != 9):
			self.commonPercent += 0.01
			self.detectMostCommonGapsHor()
		self.commonPercent = 0.02
		if ((len(self.mostCommonHorGaps) != 3 and len(self.mostCommonHorGaps) != 9 or self.mostCommonHorGapSize <= 6) and self.saveProgress== False):
			return

		self.detectGapOverlap()
		if (len(self.mostCommonVertGaps) == 3 and len(self.mostCommonHorGaps) == 3 and len(self.gapOverlaps) == 9):
			self.convertGapOverlaps()
			self.sortGapOverlaps()
		if (len(self.gapOverlaps) != 81 and self.saveProgress == False):
			return

		self.saveGapOverlapImages()
		self.detectNumbers()

		self.solve()

	#resizes image
	def resizeImage(self):
		startTime = time.time()

		minSize = 800
		if (self.width < minSize or self.height < minSize):

			if (self.width <= self.height):
				scale = minSize / self.width
			else:
				scale = minSize / self.height
			self.image = self.image.resize((int(self.width*scale),int(self.height*scale)))
			self.width, self.height = self.image.size
			self.imageGray = self.image.convert('L')	

		self.resizeImageTime = time.time() - startTime	

	#converts image to a black and white image
	def binarize(self):
		startTime = time.time()

		#convert using a static threshold
		###################################
		#self.imageBW = self.image.convert('1', dither=Image.NONE)
		###################################

		# convert the image to a black and white image using a custom threshold
		###################################
		#self.imageGray = self.image.convert('L')
		#self.bwArray = np.array(self.imageGray)	
		#self.bwArray[self.bwArray >= self.threshold] = 255
		#self.bwArray[self.bwArray < self.threshold] = 0
		#self.imageBW = Image.fromarray(self.bwArray)
		#self.pixels = self.imageBW.load() #using this to access all pixels is much faster then using getpixel
		###################################

		#convert the image to a black and white image using Otsu thresholding
		###################################
		self.grayArray = np.array(self.imageGray)

		#apply unsharp mask
		blurArray = cv2.GaussianBlur(self.grayArray, (9,9), 10.0)
		self.grayArray = cv2.addWeighted(self.grayArray, 1.5, blurArray, -0.5, 0, self.grayArray)

		#apply threshold using OTSU thresholding.
		self.threshold, self.bwArray = cv2.threshold(self.grayArray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)	

		#apply threshold using adaptive thresholding
		#self.bwArray = cv2.adaptiveThreshold(self.grayArray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 23, 2)

		#Correct a threshold of 0 to a threshold of 1
		if (int(self.threshold) == 0):
			self.threshold = 1
			self.bwArray = np.array(self.imageGray)	
			self.bwArray[self.bwArray >= self.threshold] = 255
			self.bwArray[self.bwArray < self.threshold] = 0

		self.imageBW = Image.fromarray(self.bwArray)
		self.pixels = self.imageBW.load()
		###################################

		self.binarizeTime = time.time() - startTime

	#detects the background color for binary images
	def detectBackgroundColor(self):
		startTime = time.time()
		
		colorCounts = self.imageBW.getcolors()
		if (len(colorCounts) >= 2 and colorCounts[1][0] > colorCounts[0][0]):
			self.backgroundColor = 255
		elif (len(colorCounts) >= 2 and colorCounts[1][0] < colorCounts[0][0]):
			self.backgroundColor = 0
		elif (len(colorCounts) == 1):
			self.backgroundColor = colorCounts[0][1]
		else:
			self.backgroundColor = -1

		self.detectBackgroundColorTime = time.time() - startTime

	#detect vertical lines
	def detectLinesVert(self):
		startTime = time.time()
		
		self.linesVert = []

		lineSpaceSizeTop = self.lineSpacePercent * self.height
		lineSpaceSumSizeTop = self.lineSpaceSumPercent * self.height

		#shrink image vertically to speed up the vertical line detection
		self.imageBWShort = self.imageBW.resize((self.width,int(self.height*self.lineDetectionScale)))
		pixelsShort = self.imageBWShort.load()

		shortWidth, shortHeight = self.imageBWShort.size
		minimumVertLength = shortHeight * self.minimumLengthPercent

		for x in range(shortWidth):
			lineLength = 0
			lineSpaceSize = 0
			lineSpaceSumSize = 0
			for y in range(shortHeight):
				pixelColor = pixelsShort[x,y]
				#line continues
				if (pixelColor != self.backgroundColor):
					if (lineLength == 0):
						lineStart = y
					lineSpaceSize = 0
					lineLength = lineLength + 1
				#line continues with a line space
				elif (lineLength != 0 and lineSpaceSize < lineSpaceSizeTop and lineSpaceSumSize < lineSpaceSumSizeTop):
					lineLength = lineLength + 1
					lineSpaceSize = lineSpaceSize + 1
					lineSpaceSumSize = lineSpaceSumSize + 1
				#line ends
				else:
					if (lineLength >= minimumVertLength):
						#dont extend lines to the edges of the image
						#self.linesVert.append(((x,int(lineStart/self.lineDetectionScale)),(x,int(y/self.lineDetectionScale))))
						#extend lines to the edges of the image
						self.linesVert.append(((x,0),(x,self.height-1)))

					lineLength = 0
			if (lineLength >= minimumVertLength):
				#dont extend lines to the edges of the image
				#self.linesVert.append(((x,int(lineStart/self.lineDetectionScale)),(x,int(y/self.lineDetectionScale))))
				#extend lines to the edges of the image
				self.linesVert.append(((x,0),(x,self.height-1)))

		self.detectLinesVertTime = time.time() - startTime

	#detect horizontal lines
	def detectLinesHor(self):
		startTime = time.time()

		self.linesHor = []

		lineSpaceSizeTop = self.lineSpacePercent * self.width
		lineSpaceSumSizeTop = self.lineSpaceSumPercent * self.width
		#shrink image horizontally to speed up the vertical line detection
		self.imageBWThin = self.imageBW.resize((int(self.width*self.lineDetectionScale),self.height))
		pixelsThin = self.imageBWThin.load()

		thinWidth, thinHeight = self.imageBWThin.size
		minimumHorLength = thinWidth * self.minimumLengthPercent

		for y in range(thinHeight):
			lineLength = 0
			lineSpaceSize = 0
			lineSpaceSumSize = 0
			for x in range(thinWidth):
				pixelColor = pixelsThin[x,y]
				#line continues
				if(pixelColor != self.backgroundColor):
					if (lineLength == 0):
						lineStart = x
					lineSpaceSize = 0
					lineLength = lineLength + 1
				#line continues with a line space
				elif (lineLength != 0 and lineSpaceSize < lineSpaceSizeTop and lineSpaceSumSize < lineSpaceSumSizeTop):
					lineLength = lineLength + 1
					lineSpaceSize = lineSpaceSize + 1
					lineSpaceSumSize = lineSpaceSumSize + 1
				#line ends
				else:
					if (lineLength >= minimumHorLength):
						#dont extend lines to the edges of the image
						#self.linesHor.append(((int(lineStart/self.lineDetectionScale),y),(int(x/self.lineDetectionScale),y)))
						#extend lines to the edges of the image
						self.linesHor.append(((0,y),(self.width-1,y)))
					lineLength = 0
			if (lineLength >= minimumHorLength):
				#dont extend lines to the edges of the image
				#self.linesHor.append(((int(lineStart/self.lineDetectionScale),y),(int(x/self.lineDetectionScale),y)))
				#extend lines to the edges of the image
				self.linesHor.append(((0,y),(self.width-1,y)))

		self.detectLinesHorTime = time.time() - startTime

	#detect gaps between vertical lines
	def detectGapsVert(self):
		startTime = time.time()

		self.vertGaps = []
		self.vertGapsBySize = [[] for i in range(self.width)]	#lists of line pairs that represent vertical gaps that are sorted by gap size

		#get the gap between the left edge of the picture and the first vertical line
		if(len(self.linesVert) >= 1):
			gap = self.linesVert[0][0][0] - 0
			if (gap > 1):
				x1 = 0
				y1 = self.linesVert[0][0][1]
				x2 = 0
				y2 = self.linesVert[0][1][1]
				x3 = self.linesVert[0][0][0] - 1
				y3 = self.linesVert[0][0][1]
				x4 = self.linesVert[0][1][0] - 1
				y4 = self.linesVert[0][1][1]
				self.vertGaps.append( ( ((x1, y1),(x2, y2)), ((x3,y3),(x4,y4)) ) )
				self.vertGapsBySize[gap].append( ( ((x1, y1),(x2, y2)), ((x3,y3),(x4,y4)) ) )
		#get the gap between vertical lines
		if(len(self.linesVert) > 1):
			i = 0
			while(i < len(self.linesVert)):
				gap = self.linesVert[i][0][0] - self.linesVert[i-1][0][0]
				if (gap >= self.minVertGapSize):
					x1 = self.linesVert[i-1][0][0] + 1
					y1 = self.linesVert[i-1][0][1]
					x2 = self.linesVert[i-1][1][0] + 1
					y2 = self.linesVert[i-1][1][1]
					x3 = self.linesVert[i][0][0] - 1
					y3 = self.linesVert[i][0][1]
					x4 = self.linesVert[i][1][0] - 1
					y4 = self.linesVert[i][1][1]
					self.vertGaps.append( ( ((x1, y1),(x2, y2)), ((x3,y3),(x4,y4)) ) )
					self.vertGapsBySize[gap].append( ( ((x1, y1),(x2, y2)), ((x3,y3),(x4,y4)) ) )
				i = i + 1
		#get the gap between the right edge of the picture and the last vertical line
		if(len(self.linesVert) >= 1):
			gap = self.width - self.linesVert[len(self.linesVert)-1][0][0]
			if (gap > 1):
				x1 = self.linesVert[len(self.linesVert)-1][0][0] + 1
				y1 = self.linesVert[len(self.linesVert)-1][0][1]
				x2 = self.linesVert[len(self.linesVert)-1][1][0] + 1
				y2 = self.linesVert[len(self.linesVert)-1][1][1]
				x3 = self.width - 1
				y3 = self.linesVert[len(self.linesVert)-1][0][1]
				x4 = self.width - 1
				y4 = self.linesVert[len(self.linesVert)-1][1][1]
				self.vertGaps.append( ( ((x1, y1),(x2, y2)), ((x3,y3),(x4,y4)) ) )
				self.vertGapsBySize[gap].append( ( ((x1, y1),(x2, y2)), ((x3,y3),(x4,y4)) ) )

		self.detectGapsVertTime = time.time() - startTime

	#detect gaps between horizontal lines
	def detectGapsHor(self):
		startTime = time.time()

		self.horGaps = []
		self.horGapsBySize = [[] for i in range(self.height)]	#lists of line pairs that represent horizontal gaps that are sorted by gap size

		#get the gap between the top edge of the picture and the first horizontal line
		if(len(self.linesHor) >= 1):
			gap = self.linesHor[0][0][1] - 0
			if (gap >= self.minHorGapSize):
				x1 = self.linesHor[0][0][0]
				y1 = 0
				x2 = self.linesHor[0][1][0]
				y2 = 0
				x3 = self.linesHor[0][0][0]
				y3 = self.linesHor[0][0][1] - 1
				x4 = self.linesHor[0][1][0]
				y4 = self.linesHor[0][1][1] - 1
				self.horGaps.append( ( ((x1, y1),(x2, y2)), ((x3,y3),(x4,y4)) ) )
				self.horGapsBySize[gap].append( ( ((x1, y1),(x2, y2)), ((x3,y3),(x4,y4)) ) )
		#get the gap between horizontal lines
		if(len(self.linesHor) > 1):
			i = 0
			while(i < len(self.linesHor)):
				gap = self.linesHor[i][0][1] - self.linesHor[i-1][0][1]
				if (gap > 1):
					x1 = self.linesHor[i-1][0][0]
					y1 = self.linesHor[i-1][0][1] + 1
					x2 = self.linesHor[i-1][1][0]
					y2 = self.linesHor[i-1][1][1] + 1
					x3 = self.linesHor[i][0][0]
					y3 = self.linesHor[i][0][1] - 1
					x4 = self.linesHor[i][1][0]
					y4 = self.linesHor[i][1][1] - 1
					self.horGaps.append( ( ((x1, y1),(x2, y2)), ((x3,y3),(x4,y4)) ) )
					self.horGapsBySize[gap].append( ( ((x1, y1),(x2, y2)), ((x3,y3),(x4,y4)) ) )
				i = i + 1

		#get the gap between the bottom edge of the picture and the last horizontal line
		if(len(self.linesHor) >= 1):
			gap = self.height - self.linesHor[len(self.linesHor)-1][0][1]
			if (gap > 1):
				x1 = self.linesHor[len(self.linesHor)-1][0][0]
				y1 = self.linesHor[len(self.linesHor)-1][0][1] + 1
				x2 = self.linesHor[len(self.linesHor)-1][1][0]
				y2 = self.linesHor[len(self.linesHor)-1][1][1] + 1
				x3 = self.linesHor[len(self.linesHor)-1][0][0]
				y3 = self.height - 1
				x4 = self.linesHor[len(self.linesHor)-1][1][0]
				y4 = self.height - 1
				self.horGaps.append( ( ((x1, y1),(x2, y2)), ((x3,y3),(x4,y4)) ) )
				self.horGapsBySize[gap].append( ( ((x1, y1),(x2, y2)), ((x3,y3),(x4,y4)) ) )

		self.detectGapsHorTime = time.time() - startTime

	#detect the most common sized gaps between vertical lines
	def detectMostCommonGapsVert(self):
		startTime = time.time()

		#Consolidate vertical gap sizes
		for i in range(1,len(self.vertGapsBySize)):
			if (len(self.vertGapsBySize[i]) > 0):
				commonGapSize = math.ceil(i * self.commonPercent)
				for j in range(1, commonGapSize + 1):
					if (i - j > 0 and len(self.vertGapsBySize[i-j]) > 0):
						self.vertGapsBySize[i] = self.vertGapsBySize[i] + self.vertGapsBySize[i-j]
						self.vertGapsBySize[i-j] = []

		#Find the most common vert gap size
		mostCommonVertGapSize = -1
		mostCommonVertGapOccurances = -1
		for i in range(len(self.vertGapsBySize) - self.minVertGapSize):
			j = len(self.vertGapsBySize) - 1 - i
			if(len(self.vertGapsBySize[j]) > mostCommonVertGapOccurances):
				self.mostCommonVertGapSize = j
				mostCommonVertGapOccurances = len(self.vertGapsBySize[j])
		self.mostCommonVertGaps = self.vertGapsBySize[self.mostCommonVertGapSize]

		#sort mostCommonVertGaps by x position of gap
		self.mostCommonVertGaps.sort(key=lambda a: a[0][0][0])
		
		self.detectMostCommonGapsVertTime += time.time() - startTime

	#detect the most common sized gaps between horizontal lines
	def detectMostCommonGapsHor(self):
		startTime = time.time()

		############
		#Consolidate horizontal gap sizes
		for i in range(1,len(self.horGapsBySize)):
			if (len(self.horGapsBySize[i]) > 0):
				commonGapSize = math.ceil(i * self.commonPercent)
				for j in range(1, commonGapSize + 1):
					if (i - j > 0 and len(self.horGapsBySize[i-j]) > 0):
						self.horGapsBySize[i] = self.horGapsBySize[i] + self.horGapsBySize[i-j]
						self.horGapsBySize[i-j] = []

		#Find the most common horizontal gap size
		mostCommonHorGapSize = -1
		mostCommonHorGapOccurances = -1
		for i in range(len(self.horGapsBySize) - self.minHorGapSize):
			j = len(self.horGapsBySize) - 1 - i
			if(len(self.horGapsBySize[j]) > mostCommonHorGapOccurances):
				self.mostCommonHorGapSize = j
				mostCommonHorGapOccurances = len(self.horGapsBySize[j])
		self.mostCommonHorGaps = self.horGapsBySize[self.mostCommonHorGapSize]

		#sort mostCommonHorGaps by x position of gap
		self.mostCommonHorGaps.sort(key=lambda a: a[0][0][1])

		self.detectMostCommonGapsHorTime += time.time() - startTime

	#detect the spots where vertical and horizontal gaps overlap
	def detectGapOverlap(self):
		startTime = time.time()

		self.gapOverlaps = []
		for i in self.mostCommonHorGaps:
			h1x = i[0][0][0]
			h1y = i[0][0][1]
			h4x = i[1][1][0]
			h4y = i[1][1][1]
			for j in self.mostCommonVertGaps:
				v1x = j[0][0][0]
				v1y = j[0][0][1]
				v4x = j[1][1][0]
				v4y = j[1][1][1]
				
				#check for overlap( including partial overlap)
				if  ( ( h1y >= v1y and h1y <= v4y or h4y >= v1y and h4y <= v4y) and (v1x >= h1x and v1x <= h4x or v4x >= h1x and v4x <= h4x) ):
					topLeftCorner     = (v1x, h1y)
					bottomRightCorner = (v4x, h4y)
					self.gapOverlaps.append((topLeftCorner,bottomRightCorner))
		self.detectGapOverlapTime = time.time() - startTime

	#convert gap overlaps
	def convertGapOverlaps(self):
		startTime = time.time()

		newGapOverlaps = []
		for i in self.gapOverlaps:
			x1 = i[0][0]
			y1 = i[0][1]
			x2 = i[1][0]
			y2 = i[1][1]
			xGap = x2 - x1
			yGap = y2 - y1
			newXGap = int(xGap / 3)
			newYGap = int(yGap / 3)

			#for y in range(y1,y2,newYGap):
			#	for x in range(x1,x2,newXGap):

			newGapOverlaps = newGapOverlaps + [
				((x1+1, y1+1), (x1 + newXGap-1, y1 + newYGap-1)),
				((x1+newXGap+1, y1+1), (x1+2*newXGap-1, y1 + newYGap-1)),
				((x1+2*newXGap+1, y1+1), (x1+3*newXGap-1, y1 + newYGap-1)),
				((x1+1, y1 + newYGap+1), (x1 + newXGap-1, y1 + 2*newYGap-1)),
				((x1 + newXGap+1, y1 + newYGap+1), (x1 + 2*newXGap-1, y1 + 2*newYGap-1)),
				((x1 + 2*newXGap+1, y1 + newYGap+1), (x1 + 3*newXGap-1, y1 + 2*newYGap-1)),
				((x1+1, y1 + 2*newYGap+1), (x1 + newXGap-1, y1 + 3*newYGap-1)),
				((x1 + newXGap+1, y1 + 2*newYGap+1), (x1 + 2*newXGap-1, y1 + 3*newYGap-1)),
				((x1 + 2*newXGap+1, y1 + 2*newYGap+1), (x1 + 3*newXGap-1, y1 + 3*newYGap-1))
				]

		#print(newGapOverlaps)
		self.gapOverlaps = newGapOverlaps
		self.mostCommonHorGapSize = int(self.mostCommonHorGapSize/3)
		self.mostCommonVertGapSize = int(self.mostCommonVertGapSize/3)

		self.convertOverlapGapsTime = time.time() - startTime

	#sort gap overlaps
	def sortGapOverlaps(self):
		#sort gapOverlaps by y position then x position of the upper left corner of the gap overlap
		self.gapOverlaps.sort(key=lambda a: (a[0][1], a[0][0]))

	#crop the image into 81 smaller images that are saved to file so that tesseract ocr can be used on them
	def saveGapOverlapImages(self):
		startTime = time.time()
		
		image = self.imageGray
		imageArray = np.array(image)

		#apply canny edge detection
		#imageArray = cv2.Canny(imageArray,100,200)
		#image = Image.fromarray(imageArray)

		#blur image
		imageArray = cv2.GaussianBlur(imageArray, (5,5), 2.0)
	
		#apply unsharp mask
		#imageBlurArray = cv2.GaussianBlur(imageArray, (9,9), 10.0)
		#imageArray = cv2.addWeighted(imageArray, 1.5, imageBlurArray, -0.5, 0, imageArray)
		
		#apply denoising
		#imageArray = cv2.fastNlMeansDenoising(imageArray,None,10,7,11)

		#apply binarization to the image using previously calculated threshold
		#imageArray[imageArray >= self.threshold] = 255
		#imageArray[imageArray < self.threshold] = 0
		
		#convert array back to image
		image = Image.fromarray(imageArray)


		count = 0
		for i in self.gapOverlaps:
			cropLeft = i[0][0]
			cropTop = i[0][1]
			cropRight = i[1][0]
			cropBottom = i[1][1]
			horCrop = (cropRight - cropLeft) * self.gapOverlapCropPercent
			vertCrop = (cropBottom - cropTop) * self.gapOverlapCropPercent
			cropLeft = cropLeft + horCrop
			cropTop = cropTop + vertCrop
			cropRight = cropRight - horCrop
			cropBottom = cropBottom - vertCrop

			count = count + 1
			#crop image
			if(cropBottom > cropTop and cropRight > cropLeft):
				cropImage = image.crop((cropLeft, cropTop, cropRight, cropBottom))
				
				cropWidth, cropHeight = cropImage.size

				scaleRatio = 1
				if (cropWidth < cropHeight):
					scaleRatio = 300 / cropWidth
				else:
					scaleRatio = 300 / cropHeight
				#print("Scale Ratio: ", scaleRatio)

				#cropImage = cropImage.resize((300, 300), resample=Image.BILINEAR)
				cropImage = cropImage.resize((int(cropWidth*scaleRatio), int(cropHeight*scaleRatio)), resample=Image.BICUBIC)
				cropImageArray = np.array(cropImage)
	
				#apply unsharp mask
				cropImageBlurArray = cv2.GaussianBlur(cropImageArray, (9,9), 10.0)
				cropImageArray = cv2.addWeighted(cropImageArray, 1.5, cropImageBlurArray, -0.5, 0, cropImageArray)

				#binarize
				cropImageArray[cropImageArray >= self.threshold] = 255
				cropImageArray[cropImageArray < self.threshold] = 0
				cropImage = Image.fromarray(cropImageArray)

			else:	#if the cropped image is not a proper size it creates a 1x1 black image to save
				cropImage = Image.new("1",(1,1))

			cropImage.save(self.path + self.tempFolder + str(count) + '.tif', format="tiff", dpi=(300,300))

		self.saveGapOverlapImagesTime = time.time() - startTime

	#save images of progress so that they can be analyzed	
	def saveProgressImages(self):
		startTime = time.time()

		##############################
		#save grayscale image
		self.imageGray.save(self.path + self.progressFolder + "1-GrayScale" + '.png', format="png")
		##############################
		#save binarized image
		self.imageBW.save(self.path + self.progressFolder + "2-binarized" + '.png', format="png")
		##############################
		#Save vertically shrunk image
		self.imageBWShort.save(self.path + self.progressFolder + "3-verticallyShrunk" + '.png', format="png")
		##############################
		#Save horizontally shrunk image
		self.imageBWThin.save(self.path + self.progressFolder + "4-horizontallyShrunk" + '.png', format="png")
		##############################
		#convert gray image to rgb
		imGrayRGB = self.imageGray.convert('RGB')
		#convert black and white image to rgb
		imBWRGB = self.imageBW.convert('RGB')
		##############################
		#draw detected lines in red on image
		imLines = copy.copy(imBWRGB)
		draw = ImageDraw.Draw(imLines)
		for i in self.linesVert:
			draw.line(i,fill=(255, 0, 0))
		for i in self.linesHor:
			draw.line(i,fill=(255, 0, 0))
		imLines.save(self.path + self.progressFolder + "5-detectedLines" + '.png', format="png")
		##############################
		#draw detected vertical gaps in image
		imVertGaps = copy.copy(imBWRGB)
		draw = ImageDraw.Draw(imVertGaps)
		counter = 0
		colorFill = (246,0,255)
		#print("Length of vertGaps: ", len(vertGaps))
		for i in self.vertGaps:
			colorFill = ((246,0,255) if counter % 2 == 0 else (255,127,0))
			
			x1 = i[0][0][0]
			y1 = i[0][0][1]
			x2 = i[0][1][0]
			y2 = i[0][1][1]
			x3 = i[1][0][0]
			y3 = i[1][0][1]
			x4 = i[1][1][0]
			y4 = i[1][1][1]
			lowY = (y1 if y1 < y3 else y3)
			highY = (y2 if y2 > y4 else y4)
			draw.rectangle(((x1,lowY),(x4,highY)), fill=colorFill)
			counter = counter + 1
		imVertGaps.save(self.path + self.progressFolder + "6-vertGaps" + '.png', format="png")
		##############################
		#draw detected horizontal gaps in image
		imHorGaps = copy.copy(imBWRGB)
		draw = ImageDraw.Draw(imHorGaps)
		counter = 0
		#print("Length of horGaps: ", len(horGaps))

		for i in self.horGaps:
			colorFill = ((246,0,255) if counter % 2 == 0 else (255,127,0))
			x1 = i[0][0][0]
			y1 = i[0][0][1]
			x2 = i[0][1][0]
			y2 = i[0][1][1]
			x3 = i[1][0][0]
			y3 = i[1][0][1]
			x4 = i[1][1][0]
			y4 = i[1][1][1]
			lowX = (x1 if x1 < x3 else x3)
			highX = (x2 if x2 > x4 else x4)
			draw.rectangle(((lowX,y1),(highX,y4)), fill=colorFill)
			#draw.line(i[0], fill=(246, 0, 255))
			#draw.line(i[1], fill=(255, 127, 0))
			counter = counter + 1
		imHorGaps.save(self.path + self.progressFolder + "7-horGaps" + '.png', format="png")
		##############################	
		#draw detected most commonly sized vertical gaps in image
		imCommonVertGaps = copy.copy(imBWRGB)
		draw = ImageDraw.Draw(imCommonVertGaps)
		counter = 0
		colorFill = (246,0,255)
		#print("Length of mostCommonVertGaps: ", len(mostCommonVertGaps))
		for i in self.mostCommonVertGaps:
			colorFill = ((246,0,255) if counter % 2 == 0 else (255,127,0))
			#print(colorFill)
			x1 = i[0][0][0]
			y1 = i[0][0][1]
			x2 = i[0][1][0]
			y2 = i[0][1][1]
			x3 = i[1][0][0]
			y3 = i[1][0][1]
			x4 = i[1][1][0]
			y4 = i[1][1][1]
			lowY = (y1 if y1 < y3 else y3)
			highY = (y2 if y2 > y4 else y4)
			draw.rectangle(((x1,lowY),(x4,highY)), fill=colorFill)
			counter = counter + 1
		#print(counter)
		imCommonVertGaps.save(self.path + self.progressFolder + "8-mostCommonVertGaps" + '.png', format="png")
		##############################
		#draw detected most commonly sized horizontal gaps in image
		imCommonHorGaps = copy.copy(imGrayRGB)
		draw = ImageDraw.Draw(imCommonHorGaps)
		counter = 0
		#print("Length of mostCommonHorGaps: ", len(mostCommonHorGaps))
		for i in self.mostCommonHorGaps:
			colorFill = ((246,0,255) if counter % 2 == 0 else (255,127,0))
			#print(colorFill)
			x1 = i[0][0][0]
			y1 = i[0][0][1]
			x2 = i[0][1][0]
			y2 = i[0][1][1]
			x3 = i[1][0][0]
			y3 = i[1][0][1]
			x4 = i[1][1][0]
			y4 = i[1][1][1]
			#print("gap height: ", y4- y1)
			lowX = (x1 if x1 < x3 else x3)
			highX = (x2 if x2 > x4 else x4)
			draw.rectangle(((lowX,y1),(highX,y4)), fill=colorFill)
			#draw.line(i[0], fill=(246, 0, 255))
			#draw.line(i[1], fill=(255, 127, 0))
			counter = counter + 1
		#print(counter)
		imCommonHorGaps.save(self.path + self.progressFolder + "9-mostCommonHorGaps" + '.png', format="png")
		##############################	
		#draw detected overlap rectangles in image
		imOverlapGaps = copy.copy(imBWRGB)
		draw = ImageDraw.Draw(imOverlapGaps)
		counter = 0
		colorFill = (246,0,255)
		for i in self.gapOverlaps:
			colorFill = ((246,0,255) if counter % 2 == 0 else (255,127,0))
			draw.rectangle(i,fill=colorFill)
			counter = counter + 1
		imOverlapGaps.save(self.path + self.progressFolder + "10-overlapGaps" + '.png', format="png")
		##############################
		#draw detected board in image
		imDetectedNums = copy.copy(imBWRGB)
		draw = ImageDraw.Draw(imDetectedNums)
		vertGridSize = self.mostCommonVertGapSize
		horGridSize = self.mostCommonHorGapSize
		gridSquareSize = ((vertGridSize) if vertGridSize < horGridSize else (horGridSize))
		fontSize = math.floor(gridSquareSize * .7 * (1 - self.gapOverlapCropPercent))
		backColor = (224,224,224)
		color = (204,53,110)
		for i in range(len(self.sudokuBoard)):
			if(self.sudokuBoard[i] != "0"):
				if (i < len(self.gapOverlaps)):
					draw.rectangle(self.gapOverlaps[i],fill=backColor)
		for i in range(len(self.sudokuBoard)):
			if(self.sudokuBoard[i] != "0"):
				if (i < len(self.gapOverlaps)):
					numChar = self.sudokuBoard[i]
					font = ImageFont.truetype("arial.ttf",fontSize) 
					fontWidth, fontHeight = font.getsize(numChar)
					x = self.gapOverlaps[i][0][0] + horGridSize / 2 - fontWidth / 2
					y = self.gapOverlaps[i][0][1] + vertGridSize / 2 - fontHeight / 2 - fontHeight*0.12	#last term accounts for space at top of font
					xy = (x, y)
					draw.text(xy, numChar, fill=color, font=font)
		imDetectedNums.save(self.path + self.progressFolder + "11-detectedNums" + ".png", format="png")

		######################################
		#draw repaired board in image
		imRepairedNums = copy.copy(imBWRGB)
		draw = ImageDraw.Draw(imRepairedNums)
		vertGridSize = self.mostCommonVertGapSize
		horGridSize = self.mostCommonHorGapSize
		gridSquareSize = ((vertGridSize) if vertGridSize < horGridSize else (horGridSize))
		fontSize = math.floor(gridSquareSize * .7 * (1 - self.gapOverlapCropPercent))
		backColor = (224,224,224)
		color = (204,53,110)
		for i in range(len(self.sudokuBoard)):
			if(self.sudokuBoard[i] != "0"):
				if (i < len(self.gapOverlaps)):
					draw.rectangle(self.gapOverlaps[i],fill=backColor)
		for i in range(len(self.repairedBoard)):
			if(self.repairedBoard[i] != "0"):
				if (i < len(self.gapOverlaps)):
					numChar = self.repairedBoard[i]
					font = ImageFont.truetype("arial.ttf",fontSize) 
					fontWidth, fontHeight = font.getsize(numChar)
					x = self.gapOverlaps[i][0][0] + horGridSize / 2 - fontWidth / 2
					y = self.gapOverlaps[i][0][1] + vertGridSize / 2 - fontHeight / 2 - fontHeight*0.12	#last term accounts for space at top of font
					xy = (x, y)
					draw.text(xy, numChar, fill=color, font=font)
		imRepairedNums.save(self.path + self.progressFolder + "12-repairedNums" + ".png", format="png")
		######################################
		#draw solved board in image
		imSolvedNums = copy.copy(self.imageGray.convert('RGB'))
		draw = ImageDraw.Draw(imSolvedNums)
		vertGridSize = self.mostCommonVertGapSize
		horGridSize = self.mostCommonHorGapSize
		gridSquareSize = ((vertGridSize) if vertGridSize < horGridSize else (horGridSize))
		fontSize = math.floor(gridSquareSize * .7 * (1 - self.gapOverlapCropPercent))
		backColor = (224,224,224)
		color = (35,80,153)
		for i in range(len(self.solvedBoard)):
			if(self.repairedBoard != "" and self.repairedBoard[i] == "0" or self.sudokuBoard[i] == "0"):
				if (i < len(self.gapOverlaps)):
					draw.rectangle(self.gapOverlaps[i],fill=backColor)
		for i in range(len(self.solvedBoard)):
			if(self.repairedBoard != "" and self.repairedBoard[i] == "0" or self.sudokuBoard[i] == "0"):
				if (i < len(self.gapOverlaps)):
					numChar = self.solvedBoard[i]
					font = ImageFont.truetype("arial.ttf",fontSize) 
					fontWidth, fontHeight = font.getsize(numChar)
					x = self.gapOverlaps[i][0][0] + horGridSize / 2 - fontWidth / 2
					y = self.gapOverlaps[i][0][1] + vertGridSize / 2 - fontHeight / 2 - fontHeight*0.12	#last term accounts for space at top of font
					xy = (x, y)
					draw.text(xy, numChar, fill=color, font=font)
		imSolvedNums.save(self.path + self.progressFolder + "13-solvedNums" + ".png", format="png")
		######################################
		self.saveProgressImagesTime = time.time() - startTime
		######################################
	#use tesseract ocr on saved images and get results
	def detectNumbers(self):
		startTime = time.time()
		
		#make text file with all image file names
		imageListFile = open(self.path + self.tempFolder + "imagelist.txt","w")
		for i in range(1, len(self.gapOverlaps) + 1):
			imageListFile.write(self.path + self.tempFolder + str(i) + ".tif\n")
			#imageListFile.write(self.path + self.tempFolder + str(i) + ".tif\n")
			#imageListFile.write(self.path + self.tempFolder + str(i) + ".tif\n")
			#imageListFile.write(self.path + self.tempFolder + str(i) + ".tif\n")
			#imageListFile.write(self.path + self.tempFolder + str(i) + ".tif\n")

		imageListFile.close()

		#run tesseract ocr on image list
		imgListPath = "\"" + self.path +  self.tempFolder + "imagelist.txt" + "\" "
		txtPath = "\"" + self.path +  self.tempFolder + "out" + "\" "
		processStr = "tesseract " + imgListPath + " " + txtPath + " --oem 0 --psm 13 -l eng -c tessedit_char_whitelist=123456789 -c page_separator=# -c load_system_dawg=false -c load_freq_dawg=false -c debug_file=nul"# -c tessedit_write_images=true"  -c page_separator=# 
		subprocess.call(processStr, shell=False)

		#get tesseract ocr output
		recCharFile = open(self.path + self.tempFolder + "out.txt", "r")
		recChars = recCharFile.read()

		#print(recChars)

		#replace space with empty string
		recChars = re.sub(" ","", recChars)
		#replace multiple numbers with a zero
		recChars = re.sub("[123456789]{2,}","0", recChars)
		#replace line feed with empty string
		recChars = re.sub(chr(10), "", recChars)
		#replace number followed by # with matched number
		recChars = re.sub("([0123456789])" + "#", r"\1", recChars)
		#replace # with 0
		recChars = re.sub("#", "0", recChars)

		self.sudokuBoard = recChars
		
		"""
		for i in range(1, len(self.gapOverlaps) + 1):
			imgPath = "\"" + self.path +  self.tempFolder + str(i) + ".tif"  + "\" "
			txtPath = "\"" + self.path +  self.tempFolder + str(i) + "\" "
			processStr = "tesseract " + imgPath + " " + txtPath + " --oem 0 --psm 10 -l eng -c tessedit_char_whitelist=123456789 -c load_system_dawg=false -c load_freq_dawg=false  -c debug_file=nul"# -c tessedit_write_images=true"
			subprocess.call(processStr,shell=False)

		for i in range(1, len(self.gapOverlaps) + 1):
			recCharFile = open(self.path + self.tempFolder + str(i) + ".txt")
			recChars = recCharFile.read()
			recCharFile.close()
			numFound = False
			for j in recChars:
				if(ord(j) >= 48 and ord(j) <= 57):
					numFound = True
					self.sudokuBoard += j
			if(not numFound):
				self.sudokuBoard += "0"


		
		"""
		self.detectNumbersTime = time.time() - startTime

	def solve(self):
		if (len(self.sudokuBoard) == 81):
			solver = SudokuSolver.SudokuSolver(self.sudokuBoard)
			
			if (solver.detectProblems()):
				#Attempt to repair grid
				print("Problem detected with input grid. Not Solvable. Attempting to repair grid.")
				solver.removeProblems()
				self.repairedBoard = solver.getGridString()
				self.sudokuBoard = self.repairedBoard
			else:
				self.repairedBoard = self.sudokuBoard

			solver.solve()

			self.solvedBoard = solver.getGridString()

			#print("Detected Board: ", self.sudokuBoard)
			#print("Repaired Board: ", self.repairedBoard)
			#print("  Solved Board: ", self.solvedBoard)


##########COMMAND LINE

if (len(sys.argv) > 1): 
	startTime = time.time()

	s = False
	ip = ImageProcesser(sys.argv[1])
	#handle command line modifiers
	i = 2
	while(i < len(sys.argv)):
		if ( sys.argv[i] == "s"):
			s = True
			ip.saveProgress = True
			print("Progress images will be saved.")
			i = i + 1
		elif (len(sys.argv) > i + 1):
			if (sys.argv[i] == "t"):
				print("Threshold set to " + sys.argv[i+1] + ".")
				ip.threshold = int(sys.argv[i+1])
				i = i + 2	

	ip.process()

	if (s):
		ip.saveProgressImages()

	print("\tresizeImage time:" , ip.resizeImageTime, "seconds")
	print("\tbinarize time:" , ip.binarizeTime, "seconds")
	print("\tdetectLinesVert time:" , ip.detectLinesVertTime, "seconds")
	print("\tdetectLinesHor time:" , ip.detectLinesHorTime, "seconds")
	print("\tdetectGapsVert time:" , ip.detectGapsVertTime, "seconds")
	print("\tdetectGapsHor time:" , ip.detectGapsHorTime, "seconds")
	print("\tdetectMostCommonGapsVert time:" , ip.detectMostCommonGapsVertTime, "seconds")
	print("\tdetectMostCommonGapsHor time:" , ip.detectMostCommonGapsHorTime, "seconds")
	print("\tdetectGapOverlap time:" , ip.detectGapOverlapTime, "seconds")
	print("\tconvertOverlapGaps time:" , ip.convertOverlapGapsTime, "seconds")
	print("\tsaveGapOverlapImages time:" , ip.saveGapOverlapImagesTime, "seconds")
	print("\tdetectNumbers time:" , ip.detectNumbersTime, "seconds")
	print("\tsaveProgressImages time:" , ip.saveProgressImagesTime, "seconds")
	print("\nTotal Time: ", time.time() - startTime)

