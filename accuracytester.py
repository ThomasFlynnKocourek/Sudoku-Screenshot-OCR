import processer
import os
import time

startTime = time.time()

imagesFile = open("images.txt", "r")


imageNamesAndSolutions = imagesFile.read().splitlines()
imageNames = []
imageSolutions = []
for i in range(0,len(imageNamesAndSolutions),2):
	imageNames.append(imageNamesAndSolutions[i])
for i in range(1,len(imageNamesAndSolutions),2):
	imageSolutions.append(imageNamesAndSolutions[i])

gridRecognizedCount = 0
boardMatchCount = 0
partialMatchCount = 0
falsePositiveCount = 0
mismatchCount = 0

resizeImageTime = 0
binarizeTime = 0
detectLinesVertTime = 0
detectLinesHorTime = 0
detectGapsVertTime = 0
detectGapsHorTime = 0
detectMostCommonGapsVertTime = 0
detectMostCommonGapsHorTime = 0
detectGapOverlapTime = 0
convertOverlapGapsTime = 0
saveGapOverlapImagesTime = 0
detectNumbersTime = 0
saveProgressImagesTime = 0

for i in range(len(imageNames)):
	print("Testing", imageNames[i])

	ip = processer.ImageProcesser("\\test\\" + imageNames[i])
	ip.process()
	#print(ip.sudokuBoard)

	#check if the grid is recognized
	if (len(ip.sudokuBoard) == 81 or len(ip.sudokuBoard) == 9 or len(ip.sudokuBoard) == 27):
		gridRecognizedCount += 1
	#check if the board matches
	if (ip.sudokuBoard == imageSolutions[i]):
		print("\tMATCH")
		boardMatchCount += 1
	else:
		#check if the board is a partial match
		if (len(ip.sudokuBoard) == len(imageSolutions[i])):
			sudokuBoard = ip.sudokuBoard
			#replace 0s in ip.sudokuboard with numbers from imageSolutions[i]
			for j in range(len(sudokuBoard)):
				if (sudokuBoard[j] == "0" and imageSolutions[i][j] != "0"):
					sudokuBoard = sudokuBoard[:j] + imageSolutions[i][j] + sudokuBoard[j+1:]
			if (sudokuBoard == imageSolutions[i]):
				print("\tPARTIAL MATCH")
				partialMatchCount += 1
		if (len(ip.sudokuBoard) == len(imageSolutions[i])):
			for j in range(len(ip.sudokuBoard)):
				#check if the board has false positives (match a number when none is there)
				if (imageSolutions[i][j] == "0" and ip.sudokuBoard[j] != "0"):
					falsePositiveCount += 1
				#check if the numbers dont match
				if(imageSolutions[i][j] != ip.sudokuBoard[j]):
					mismatchCount += 1


	#increment timers
	resizeImageTime += ip.resizeImageTime
	binarizeTime += ip.binarizeTime
	detectLinesVertTime += ip.detectLinesVertTime
	detectLinesHorTime += ip.detectLinesHorTime
	detectGapsVertTime += ip.detectGapsVertTime
	detectGapsHorTime += ip.detectGapsHorTime
	detectMostCommonGapsVertTime += ip.detectMostCommonGapsVertTime
	detectMostCommonGapsHorTime += ip.detectMostCommonGapsHorTime
	detectGapOverlapTime += ip.detectGapOverlapTime 
	convertOverlapGapsTime += ip.convertOverlapGapsTime
	saveGapOverlapImagesTime += ip.saveGapOverlapImagesTime
	detectNumbersTime += ip.detectNumbersTime
	saveProgressImagesTime += ip.saveProgressImagesTime
	
	
	print("\tDetected Board:", ip.sudokuBoard)
	print("\tKnown Solution:", imageSolutions[i])

print(len(imageNames), "files tested.")
print(gridRecognizedCount, "grids recognized.")
print(boardMatchCount, "boards matched.")
print(partialMatchCount, "boards partially matched.")
print(falsePositiveCount, "false positives.")
print(mismatchCount, "mismatches.")

print("Time Elapsed:", time.time() - startTime, "seconds")
print("\tresizeImage time:" , resizeImageTime, "seconds")
print("\tbinarize time:" , binarizeTime, "seconds")
print("\tdetectLinesVert time:" , detectLinesVertTime, "seconds")
print("\tdetectLinesHor time:" , detectLinesHorTime, "seconds")
print("\tdetectGapsVert time:" , detectGapsVertTime, "seconds")
print("\tdetectGapsHor time:" , detectGapsHorTime, "seconds")
print("\tdetectMostCommonGapsVert time:" , detectMostCommonGapsVertTime, "seconds")
print("\tdetectMostCommonGapsHor time:" , detectMostCommonGapsHorTime, "seconds")
print("\tdetectGapOverlap time:" , detectGapOverlapTime, "seconds")
print("\tconvertOverlapGaps time:" , convertOverlapGapsTime, "seconds")
print("\tsaveGapOverlapImages time:" , saveGapOverlapImagesTime, "seconds")
print("\tdetectNumbers time:" , detectNumbersTime, "seconds")
print("\tsaveProgressImages time:" , saveProgressImagesTime, "seconds")

