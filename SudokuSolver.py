def outputChangeStack():
	f = open("changeStack.txt",'w')
	f.write("Change Stack\n")
	n = 0
	for i in changeStack:
		n = n + 1
		f.write(str(n) + ": Change Type: " + str(i[0]) + " Num: " + str(i[1]) + " Row: " + str(i[2]) + " Col:" + str(i[3]) + "\n")
	f.close()

	f = open("allChangeStack.txt",'w')
	f.write("Change Stack\n")
	n = 0
	for i in allChangeStack:
		n = n + 1
		f.write(str(n) + ": Change Type: " + str(i[0]) + " Num: " + str(i[1]) + " Row: " + str(i[2]) + " Col:" + str(i[3]) + "\n")
	f.close()
def printChangeStack():
	print("Change Stack\n")
	n = 0
	for i in changeStack:
		n = n + 1
		print(str(n) + ": Change Type: " + str(i[0]) + " Num: " + str(i[1]) + " Row: " + str(i[2]) + " Col:" + str(i[3]))

def printPotentialGrid():
	print("\nThe Potential Grid: ")
	for num in [1, 4, 7]:
		print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
		print("|       "+ str(num) + ":        |        " + str(num+1) + ":       |        " + str(num+2) + ":       |")
		print("-------------------------------------------------------")
		for row in range (0,9):
			if row == 3 or row == 6:
				print("|                 |                 |                 |")
			print("|  ",end="")
			for numShift in range (0,3):
				for col in range (0,9):
					if col == 3 or col == 6:
						print("  ",end="")
					if potentialGrid[num+numShift][row][col]:
						print(1,end="")
					else:
						print(0,end="")
				print("  |  ",end="")
			print()
	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
def printPotentialNum(num):
	print(" " + str(num) + " Potential:")
	for row in range (0,9):
		if row == 3 or row == 6:
			print()
		for col in range (0,9):
			if col == 3 or col == 6:
				print("  ",end="")
			if potentialGrid[num][row][col]:
				print(1,end="")
			else:
				print(0,end="")
		print()
	print()
def printGrid():
	print("The Grid: \n")
	for row in range (0,9):
		if row == 3 or row == 6:
			print()
		for col in range (0,9):
			if col == 3 or col == 6:
				print("  ",end="")
			print(grid[row][col],end="")
		print()
	print()
############################################################
def updateGridPosition(typeOfChange, num, row, col):
	if typeOfChange == "guessed":
		global totalGuessCount 
		global currentGuessCount
		totalGuessCount = totalGuessCount + 1
		currentGuessCount = currentGuessCount + 1
	#print(" " + str(num) + " is " + typeOfChange + " at (" + str(row) + "," + str(col) + ")." )
	grid[row][col] = num
	allChangeStack.append((typeOfChange, num, row, col))
	changeStack.append((typeOfChange, num, row, col))	
	updatePotential()
def updatePotentialPosition(num, row, col):
	potentialGrid[num][row][col] = False
	allChangeStack.append(("potential", num, row, col))
	changeStack.append(("potential", num, row, col)) 
	#updatePotential()
def updatePotentialHorizontal():
	for row in range (0,9):
		for col in range (0,9):
			if grid[row][col] != 0:
				for k in range (0,9):
					if k != col and potentialGrid[grid[row][col]][row][k] != False:
						updatePotentialPosition(grid[row][col], row, k)
		
def updatePotentialVertical():
	for row in range (0,9):
		for col in range (0,9):
			if grid[row][col] != 0:
				for k in range (0,9):
					if k != row and potentialGrid[grid[row][col]][k][col] != False:
						updatePotentialPosition(grid[row][col], k, col)

def updatePotentialSquare():
	for row in range (0,9):
		for col in range (0,9):
			if grid[row][col] != 0:
				for k in range (0,9):
					for l in range (0,9):
						if [row,col] == squarePositions[k][l]:
							for m in range (0,9):
								if [row,col] != squarePositions[k][m] and potentialGrid[grid[row][col]][squarePositions[k][m][0]][squarePositions[k][m][1]] != 0:
									updatePotentialPosition(grid[row][col], squarePositions[k][m][0], squarePositions[k][m][1])

def updatePotential():
	#update potential for all positions that are filled
	for row in range (0,9):
		for col in range (0,9):
			if grid[row][col] > 0:
				for num in range (1,10):
					if num != grid[row][col]:
						if potentialGrid[num][row][col] == True:
							updatePotentialPosition(num, row, col)
	updatePotentialVertical()
	updatePotentialHorizontal()
	updatePotentialSquare()

def fillGrid():
	gridAltered = True
	while gridAltered:
		gridAltered = False
		
		#Fill based on grid space emptyness i.e. only a 3 can fit in a grid space
		for row in range (0, 9):
			for col in range (0,9):
				if grid[row][col] == 0:
					fillValue = -1
					for num in range (1,10):
						if potentialGrid[num][row][col] != False:
							if fillValue == -1:
								fillValue = num
							else:
								fillValue = -10
					if fillValue > 0:
						updateGridPosition("determined", fillValue, row, col)
						gridAltered = True

		#Fill based on number emptyness within a row i.e. a 3 can only fit a particular space in a row
		for row in range (0,9):
			for num in range (1,10):
				if num not in grid[row]:
					value = -1
					for col in range (0,9):
						if grid[row][col] == 0:
							if potentialGrid[num][row][col] == True:
								if value < 0:
									value = col
								elif value >= 0:
									value = -2
									break
					else:
						if value >= 0 and value < 9:
							updateGridPosition("determined", num, row, value)
							gridAltered = True 

		#Fill based on number emptyness within a column i.e. a 3 can only fit a particular space in a column
		for col in range (0,9):
			colNums = [ grid[x][col] for x in range(0,9) ] #Get all the nums in the current column
			#print(colNums)
			for num in range (1,10):
				if num not in colNums: 
					value = -1
					for row in range (0,9):
						if grid[row][col] == 0:
							if potentialGrid[num][row][col] == True:
								if value < 0:
									value = row
								elif value >= 0:
									value = -2
									break
					else:
						if value >= 0 and value < 9:
							updateGridPosition("determined", num, value, col) 
							gridAltered = True

		#Fill based on number emptyness within a square i.e.  a 3 can only fit a particular space in a square
		for row in range (0,9):
			for col in range (0,9):
				if grid[row][col] == 0:
					for num in range(1,10):
						if potentialGrid[num][row][col] == True:
							alone = True
							#get the other positions in the square
							square = -1
							for i in range(0,9):
								if [row,col] in squarePositions[i]:
									square = i
									break
							#check if num is in any of the other positions in the square
							for i in range (0,9):
								row2 = squarePositions[square][i][0]
								col2 = squarePositions[square][i][1]
								if [row,col] != [row2,col2]:
									if potentialGrid[num][row2][col2]:
										alone = False
										break
							if alone:
								updateGridPosition("determined", num, row, col)

def complete(): 	#Checks if all positions are filled
	for row in range (0,9):
		for col in range (0,9):
			if grid[row][col] == 0:
				return False
	#return true if all positions are filled
	return True

def completable():
	#Check that all positions are completable meaning that every position has at least one potential
	for row in range (0,9):
		for col in range (0,9):
			noPotential = True
			for num in range (1,10):
				if potentialGrid[num][row][col] == True:
					noPotential = False
			if noPotential == True:
				return False
	#return true if all conditions are met
	return True

def fillBestGuess():
	#Find the position with the least number of potentials
	bestPotential = 10 #the number of potentials at the position with the least number of potentials
	bestRow = -1
	bestCol = -1
	for row in range (0,9):
		for col in range (0,9):
			if grid[row][col] == 0:
				currPotential = 0
				for num in range (1,10):
					if potentialGrid[num][row][col] == True:
						currPotential = currPotential + 1
				#############################
				if currPotential > 0 and currPotential < bestPotential:
				#############################
					bestPotential = currPotential
					bestRow = row
					bestCol = col
	#Fill the position with the least number of potentials with a potential
	#print("Best Guess: [" + str(bestRow) + ", " + str(bestCol) + "] Best Potential: " + str(bestPotential))
	if bestPotential < 10:
		for i in range (1,10):
			if potentialGrid[i][bestRow][bestCol]:
				updateGridPosition("guessed", i, bestRow, bestCol)

def removeRecentGridChanges():
	print("Backtracking")

	for i in reversed(changeStack):
		changeType = i[0]
		num = i[1]
		row = i[2]
		col = i[3]
		del changeStack[-1]

		if changeType == "potential":
			potentialGrid[num][row][col] = True

		elif changeType == "determined":
			grid[row][col] = 0

		elif changeType == "guessed":
			global currentGuessCount
			currentGuessCount = currentGuessCount - 1
			grid[row][col] = 0
			updatePotentialPosition(num,row,col) #del changeStack[-1] can not come after this line because this line modifies the changestack
			break
		
def guess():
	updatePotential()
	fillGrid()
	
	while (not complete()) and completable():
		fillBestGuess()
		if guess() == False:
			removeRecentGridChanges()
	if complete() and completable():
		return True
	else:
		return False

#Find and report problem when a number is found in the same horizontal, vertical, or square
def detectProblem():
	for row in range (0,9):
		for col in range (0,9):
			if grid[row][col] > 0:	#if the grid position is filled
				for k in range (0,9):
					#check if horizontal has multiples of a number
					if k != col:
						if grid[row][col] == grid[row][k]:
							print("Problem detected Horizontal at (" + str(row) + ", " + str(col) + ") and (" + str(row) + ", " + str(k) + ")")
							exit()
					#check if vertical has multiples of a number
					if k != row:
						if grid[row][col] == grid[k][col]:
							print("Problem detected Vertical at (" + str(row) + ", " + str(col) + ") and (" + str(k) + ", " + str(col) + ")")
							exit()
					#check if square has multiples of a number
					if [row,col] in squarePositions[k]:
						for l in range (0,9):
							a = squarePositions[k][l][0]
							b = squarePositions[k][l][1]
							if [a,b] != [row,col]:
								if grid[row][col] == grid[a][b]:
									print("Problem detected Square at (" + str(row) + ", " + str(col) + ") and (" + str(a) + ", " + str(b) + ")")
									exit()
			#check if position is able to be filled
			fillable = False
			for k in range (1,10):
				if potentialGrid[k][row][col]:
					fillable = True
					break
			if not fillable:
				print("Problem detected at (" + str(row) + "," + str(col) + ")") 

############################################################

squarePositions = [
			[[0,0],[0,1],[0,2],[1,0],[1,1],[1,2],[2,0],[2,1],[2,2]],
			[[0,3],[0,4],[0,5],[1,3],[1,4],[1,5],[2,3],[2,4],[2,5]],
			[[0,6],[0,7],[0,8],[1,6],[1,7],[1,8],[2,6],[2,7],[2,8]],
			[[3,0],[3,1],[3,2],[4,0],[4,1],[4,2],[5,0],[5,1],[5,2]],
			[[3,3],[3,4],[3,5],[4,3],[4,4],[4,5],[5,3],[5,4],[5,5]],
			[[3,6],[3,7],[3,8],[4,6],[4,7],[4,8],[5,6],[5,7],[5,8]],
			[[6,0],[6,1],[6,2],[7,0],[7,1],[7,2],[8,0],[8,1],[8,2]],
			[[6,3],[6,4],[6,5],[7,3],[7,4],[7,5],[8,3],[8,4],[8,5]],
			[[6,6],[6,7],[6,8],[7,6],[7,7],[7,8],[8,6],[8,7],[8,8]],
	    ]
grid = [
		[0,0,0,  0,0,0,  8,2,0],
		[0,1,0,  0,0,0,  5,0,9],
		[0,0,9,  0,1,0,  0,0,0],

		[0,6,2,  0,0,1,  0,0,0],
		[0,0,0,  0,6,0,  0,0,0],
		[0,8,0,  3,0,0,  1,0,0],

		[0,0,0,  0,8,0,  0,0,2],
		[0,0,4,  0,0,0,  0,3,0],
		[0,0,6,  0,3,0,  0,0,0]
	   ]
#Creates and fills the potentialGrid with all true values
potentialGrid = [[[True for j in range(0,10)] for k in range(0,10)] for l in range(0,10)]

#the change stack holds tuples.
#the tuple format is (typeOfChange, num, row, col)
#ex. ('guessed', 1, 4, 6)
#ex. ('determined', 2, 2, 8)
allChangeStack = []
changeStack = []

currentGuessCount = 0
totalGuessCount = 0

if guess():
	print ("The grid is complete.")
else:
	print ("The grid is incomplete.")

#for i in range (0,81):
#	print(i)
#	updatePotential()
#	fillGrid()
#	updatePotential()
#	fillBestGuess()
#	detectProblem()

printGrid()
#printPotentialGrid()
#printChangeStack()
#outputChangeStack()
detectProblem()
print("The total number of guesses: " + str(totalGuessCount))
print("The current number of guesses: " + str(currentGuessCount))