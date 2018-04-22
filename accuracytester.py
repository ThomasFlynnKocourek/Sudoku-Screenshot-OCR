import processer
import SudokuSolver
import os
import time
import platform

startTime = time.time()

imagesFileName = "images.txt"
testFolder = "/test/cropped/"
testFolderWindows = "\\test\\cropped\\"

imagesFile = open(imagesFileName, "r")

output = ""
output += "Testing using images in " + imagesFileName + "\n\n\n"

imageNamesAndBoards = imagesFile.read().splitlines()
imageNames = []
imageBoards = []
for i in range(0,len(imageNamesAndBoards),2):
	imageNames.append(imageNamesAndBoards[i])
for i in range(1,len(imageNamesAndBoards),2):
	imageBoards.append(imageNamesAndBoards[i])

#initialize counts
gridRecognizedCount = 0
boardMatchCount = 0
partialMatchCount = 0
falsePositiveCount = 0
mismatchCount = 0
solvedCount = 0

#initialize times
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

minSolveWidth = -1
minSolveHeight = -1

#makes changes to correct for windows
if (platform.system() == "Windows"):
		testFolder = testFolderWindows

for i in range(len(imageNames)):
	output += "Testing " + imageNames[i] + "\n"
	print("\nTesting", imageNames[i])

	ip = processer.ImageProcesser(testFolder + imageNames[i])
	ip.process()
	#print(ip.sudokuBoard)

	#check if the grid is recognized
	if (len(ip.sudokuBoard) == 81 or len(ip.sudokuBoard) == 9 or len(ip.sudokuBoard) == 27):
		gridRecognizedCount += 1

	#check if the board matches
	if (ip.sudokuBoard == imageBoards[i]):
		output += "\tMatch" + "\n"
		print("\tMATCHED")
		boardMatchCount += 1
		if (minSolveWidth == -1 or ip.originalWidth < minSolveWidth):
			minSolveWidth = ip.originalWidth
		if (minSolveHeight == -1 or ip.originalHeight < minSolveHeight):
			minSolveHeight = ip.originalHeight
	else:
		#check if the board is a partial match
		if (len(ip.sudokuBoard) == len(imageBoards[i])):
			sudokuBoard = ip.sudokuBoard
			#replace 0s in ip.sudokuboard with numbers from imageBoards[i]
			for j in range(len(sudokuBoard)):
				if (sudokuBoard[j] == "0" and imageBoards[i][j] != "0"):
					sudokuBoard = sudokuBoard[:j] + imageBoards[i][j] + sudokuBoard[j+1:]
			if (sudokuBoard == imageBoards[i]):
				output += "\tPartial Match" + "\n"
				print("\tPARTIAL MATCH")
				partialMatchCount += 1
		if (len(ip.sudokuBoard) == len(imageBoards[i])):
			for j in range(len(ip.sudokuBoard)):
				#check if the board has false positives (match a number when none is there)
				if (imageBoards[i][j] == "0" and ip.sudokuBoard[j] != "0"):
					falsePositiveCount += 1
				#check if the numbers dont match
				if(imageBoards[i][j] != ip.sudokuBoard[j]):
					mismatchCount += 1

	#check if the solved boards match
	solver = SudokuSolver.SudokuSolver(imageBoards[i])
	solver.detectProblems()
	solver.removeProblems()
	solver.solve()
	#print("noo: ", solver.getGridString())
	if (ip.solvedBoard == solver.getGridString()):
		print("\tSOLVED")
		solvedCount += 1


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
	
	print("\tLength board: ", len(ip.sudokuBoard))
	output += "\tDetected Board: " + ip.sudokuBoard + "\n"
	print("\tDetected Board:", ip.sudokuBoard)
	output += "\t   Known Board: " + imageBoards[i] + "\n"
	print("\t   Known Board:", imageBoards[i])



output += "\n\n\n"
output += str(len(imageNames)) + "\tfiles tested.\n"
output += str(gridRecognizedCount) + "\tgrids recognized.\n"
output += str(boardMatchCount) + "\tboards matched.\n"
output += str(partialMatchCount) + "\tboards partially matched.\n"
output += str(solvedCount) + "\tboards solved.\n"
output += str(falsePositiveCount) + "\tfalse positives.\n"
output += str(mismatchCount) + "\tmismatches.\n"
output += "\nTime Elapsed: " + str(time.time() - startTime) + " seconds\n"
output += "\t             resizeImage time: " + str(resizeImageTime) + " seconds\n"
output += "\t                binarize time: " + str(binarizeTime) + " seconds\n"
output += "\t         detectLinesVert time: " + str(detectLinesVertTime) + " seconds\n"
output += "\t          detectLinesHor time: " + str(detectLinesHorTime) + " seconds\n"
output += "\t          detectGapsVert time: " + str(detectGapsVertTime) + " seconds\n"
output += "\t           detectGapsHor time: " + str(detectGapsHorTime) + " seconds\n"
output += "\tdetectMostCommonGapsVert time: " + str(detectMostCommonGapsVertTime) + " seconds\n"
output += "\t detectMostCommonGapsHor time: " + str(detectMostCommonGapsHorTime) + " seconds\n"
output += "\t        detectGapOverlap time: " + str(detectGapOverlapTime) + " seconds\n"
output += "\t      convertOverlapGaps time: " + str(convertOverlapGapsTime) + " seconds\n"
output += "\t    saveGapOverlapImages time: " + str(saveGapOverlapImagesTime) + " seconds\n"
output += "\t           detectNumbers time: " + str(detectNumbersTime) + " seconds\n"
output += "\t      saveProgressImages time: " + str(saveProgressImagesTime) + " seconds\n"

print(len(imageNames), "files tested.")
print(gridRecognizedCount, "grids recognized.")
print(boardMatchCount, "boards matched.")
print(partialMatchCount, "boards partially matched.")
print(solvedCount, "boards solved.")

print(falsePositiveCount, "false positives.")
print(mismatchCount, "mismatches.")

print("Minimum solved image width: ", minSolveWidth)
print("Minimum solved image height: ", minSolveHeight)
print("Time Elapsed:", time.time() - startTime, "seconds")

outputFile = open("accuracyTesterOutput.txt", "w")
outputFile.write(output)