
class SudokuSolver:

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

	def __init__(self, grid):
		
		grid = [int(x) for x in grid]	#convert string to int list
		self.grid = [grid[0:9], grid[9:18], grid[18:27], grid[27:36], grid[36:45], grid[45:54], grid[54:63], grid[63:72], grid[72:81] ]

		'''
		self.grid = [
				[0,0,0,  0,0,0,  0,0,0],
				[0,0,0,  0,0,0,  0,0,0],
				[1,0,0,  0,0,0,  0,0,0],

				[4,3,0,  0,0,0,  0,0,0],
				[2,0,0,  0,0,0,  0,0,8],
				[0,1,0,  0,0,0,  0,7,6],

				[0,0,4,  0,0,0,  2,5,1],
				[0,0,3,  0,1,7,  3,0,0],
				[0,0,2,  0,9,8,  0,0,0]
		]
		'''

		#Creates and fills the potentialGrid with all true values
		self.potentialGrid = [[[True for j in range(0,10)] for k in range(0,10)] for l in range(0,10)]
		#the change stack holds tuples.
		#the tuple format is (typeOfChange, num, row, col)
		#ex. ('guessed', 1, 4, 6)
		#ex. ('determined', 2, 2, 8)
		self.allChangeStack = []
		self.changeStack = []

		self.currentGuessCount = 0
		self.totalGuessCount = 0

		#a list of positions in which problems were detected
		self.problemsDetected = []


	def outputChangeStack(self):
		f = open("changeStack.txt",'w')
		f.write("Change Stack\n")
		n = 0
		for i in self.changeStack:
			n = n + 1
			f.write(str(n) + ": Change Type: " + str(i[0]) + " Num: " + str(i[1]) + " Row: " + str(i[2]) + " Col:" + str(i[3]) + "\n")
		f.close()

		f = open("allChangeStack.txt",'w')
		f.write("Change Stack\n")
		n = 0
		for i in self.allChangeStack:
			n = n + 1
			f.write(str(n) + ": Change Type: " + str(i[0]) + " Num: " + str(i[1]) + " Row: " + str(i[2]) + " Col:" + str(i[3]) + "\n")
		f.close()
	def printChangeStack(self):
		print("Change Stack\n")
		n = 0
		for i in self.changeStack:
			n = n + 1
			print(str(n) + ": Change Type: " + str(i[0]) + " Num: " + str(i[1]) + " Row: " + str(i[2]) + " Col:" + str(i[3]))

	def printPotentialGrid(self):
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
						if self.potentialGrid[num+numShift][row][col]:
							print(1,end="")
						else:
							print(0,end="")
					print("  |  ",end="")
				print()
		print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

	def printPotentialNum(self, num):
		print(" " + str(num) + " Potential:")
		for row in range (0,9):
			if row == 3 or row == 6:
				print()
			for col in range (0,9):
				if col == 3 or col == 6:
					print("  ",end="")
				if self.potentialGrid[num][row][col]:
					print(1,end="")
				else:
					print(0,end="")
			print()
		print()

	def printGrid(self):
		print("The Grid: \n")
		for row in range (0,9):
			if row == 3 or row == 6:
				print()
			for col in range (0,9):
				if col == 3 or col == 6:
					print("  ",end="")
				print(self.grid[row][col],end="")
			print()
		print()

	def updateGridPosition(self, typeOfChange, num, row, col):
		if typeOfChange == "guessed":
			self.totalGuessCount = self.totalGuessCount + 1
			self.currentGuessCount = self.currentGuessCount + 1
		#print(" " + str(num) + " is " + typeOfChange + " at (" + str(row) + "," + str(col) + ")." )
		self.grid[row][col] = num
		self.allChangeStack.append((typeOfChange, num, row, col))
		self.changeStack.append((typeOfChange, num, row, col))	
		self.updatePotential()

	def updatePotentialPosition(self, num, row, col):
		self.potentialGrid[num][row][col] = False
		self.allChangeStack.append(("potential", num, row, col))
		self.changeStack.append(("potential", num, row, col)) 
		#self.updatePotential()

	def updatePotentialHorizontal(self):
		for row in range (0,9):
			for col in range (0,9):
				if self.grid[row][col] != 0:
					for k in range (0,9):
						if k != col and self.potentialGrid[self.grid[row][col]][row][k] != False:
							self.updatePotentialPosition(self.grid[row][col], row, k)
			
	def updatePotentialVertical(self):
		for row in range (0,9):
			for col in range (0,9):
				if self.grid[row][col] != 0:
					for k in range (0,9):
						if k != row and self.potentialGrid[self.grid[row][col]][k][col] != False:
							self.updatePotentialPosition(self.grid[row][col], k, col)

	def updatePotentialSquare(self):
		for row in range (0,9):
			for col in range (0,9):
				if self.grid[row][col] != 0:
					for k in range (0,9):
						for l in range (0,9):
							if [row,col] == self.squarePositions[k][l]:
								for m in range (0,9):
									if [row,col] != self.squarePositions[k][m] and self.potentialGrid[self.grid[row][col]][self.squarePositions[k][m][0]][self.squarePositions[k][m][1]] != 0:
										self.updatePotentialPosition(self.grid[row][col], self.squarePositions[k][m][0], self.squarePositions[k][m][1])

	def updatePotential(self):
		#update potential for all positions that are filled
		for row in range (0,9):
			for col in range (0,9):
				if self.grid[row][col] > 0:
					for num in range (1,10):
						if num != self.grid[row][col]:
							if self.potentialGrid[num][row][col] == True:
								self.updatePotentialPosition(num, row, col)
		self.updatePotentialVertical()
		self.updatePotentialHorizontal()
		self.updatePotentialSquare()

	def fillGrid(self):
		gridAltered = True
		while gridAltered:
			gridAltered = False
			
			#Fill based on grid space emptyness i.e. only a 3 can fit in a grid space
			for row in range (0, 9):
				for col in range (0,9):
					if self.grid[row][col] == 0:
						fillValue = -1
						for num in range (1,10):
							if self.potentialGrid[num][row][col] != False:
								if fillValue == -1:
									fillValue = num
								else:
									fillValue = -10
						if fillValue > 0:
							self.updateGridPosition("determined", fillValue, row, col)
							gridAltered = True

			#Fill based on number emptyness within a row i.e. a 3 can only fit a particular space in a row
			for row in range (0,9):
				for num in range (1,10):
					if num not in self.grid[row]:
						value = -1
						for col in range (0,9):
							if self.grid[row][col] == 0:
								if self.potentialGrid[num][row][col] == True:
									if value < 0:
										value = col
									elif value >= 0:
										value = -2
										break
						else:
							if value >= 0 and value < 9:
								self.updateGridPosition("determined", num, row, value)
								gridAltered = True 

			#Fill based on number emptyness within a column i.e. a 3 can only fit a particular space in a column
			for col in range (0,9):
				colNums = [ self.grid[x][col] for x in range(0,9) ] #Get all the nums in the current column
				#print(colNums)
				for num in range (1,10):
					if num not in colNums: 
						value = -1
						for row in range (0,9):
							if self.grid[row][col] == 0:
								if self.potentialGrid[num][row][col] == True:
									if value < 0:
										value = row
									elif value >= 0:
										value = -2
										break
						else:
							if value >= 0 and value < 9:
								self.updateGridPosition("determined", num, value, col) 
								gridAltered = True

			#Fill based on number emptyness within a square i.e.  a 3 can only fit a particular space in a square
			for row in range (0,9):
				for col in range (0,9):
					if self.grid[row][col] == 0:
						for num in range(1,10):
							if self.potentialGrid[num][row][col] == True:
								alone = True
								#get the other positions in the square
								square = -1
								for i in range(0,9):
									if [row,col] in self.squarePositions[i]:
										square = i
										break
								#check if num is in any of the other positions in the square
								for i in range (0,9):
									row2 = self.squarePositions[square][i][0]
									col2 = self.squarePositions[square][i][1]
									if [row,col] != [row2,col2]:
										if self.potentialGrid[num][row2][col2]:
											alone = False
											break
								if alone:
									self.updateGridPosition("determined", num, row, col)

	def complete(self): 	#Checks if all positions are filled
		for row in range (0,9):
			for col in range (0,9):
				if self.grid[row][col] == 0:
					return False
		#return true if all positions are filled
		return True

	def completable(self):
		#Check that all positions are completable meaning that every position has at least one potential
		for row in range (0,9):
			for col in range (0,9):
				noPotential = True
				for num in range (1,10):
					if self.potentialGrid[num][row][col] == True:
						noPotential = False
				if noPotential == True:
					return False
		#return true if all conditions are met
		return True

	def fillBestGuess(self):
		#Find the position with the least number of potentials
		bestPotential = 10 #the number of potentials at the position with the least number of potentials
		bestRow = -1
		bestCol = -1
		for row in range (0,9):
			for col in range (0,9):
				if self.grid[row][col] == 0:
					currPotential = 0
					for num in range (1,10):
						if self.potentialGrid[num][row][col] == True:
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
				if self.potentialGrid[i][bestRow][bestCol]:
					self.updateGridPosition("guessed", i, bestRow, bestCol)

	def removeRecentGridChanges(self):
		for i in reversed(self.changeStack):
			changeType = i[0]
			num = i[1]
			row = i[2]
			col = i[3]
			del self.changeStack[-1]

			if changeType == "potential":
				self.potentialGrid[num][row][col] = True

			elif changeType == "determined":
				self.grid[row][col] = 0

			elif changeType == "guessed":
				self.currentGuessCount = self.currentGuessCount - 1
				self.grid[row][col] = 0
				self.updatePotentialPosition(num,row,col) #del changeStack[-1] can not come after this line because this line modifies the changestack
				break

	def solve(self):
		self.updatePotential()
		self.fillGrid()
		
		while (not self.complete()) and self.completable():
			self.fillBestGuess()
			if self.solve() == False:
				self.removeRecentGridChanges()
		if self.complete() and self.completable():
			return True
		else:
			return False

	#Find and report problem
	def detectProblems(self):
		problemDetected = False

		for row in range (0,9):
			for col in range (0,9):
				if self.grid[row][col] > 0:	#if the grid position is filled
					for k in range (0,9):
						#check if horizontal has multiples of a number
						if k != col:
							if self.grid[row][col] == self.grid[row][k]:
								#print("Problem detected Horizontal at (" + str(row) + ", " + str(col) + ") and (" + str(row) + ", " + str(k) + ")")
								problemDetected = True
								self.problemsDetected.append((row,col))
								self.problemsDetected.append((row,k))
						#check if vertical has multiples of a number
						if k != row:
							if self.grid[row][col] == self.grid[k][col]:
								#print("Problem detected Vertical at (" + str(row) + ", " + str(col) + ") and (" + str(k) + ", " + str(col) + ")")
								problemDetected = True
								self.problemsDetected.append((row,col))
								self.problemsDetected.append((k,col))
						#check if square has multiples of a number
						if [row,col] in self.squarePositions[k]:
							for l in range (0,9):
								a = self.squarePositions[k][l][0]
								b = self.squarePositions[k][l][1]
								if [a,b] != [row,col]:
									if self.grid[row][col] == self.grid[a][b]:
										#print("Problem detected Square at (" + str(row) + ", " + str(col) + ") and (" + str(a) + ", " + str(b) + ")")
										problemDetected = True
										self.problemsDetected.append((row,col))
										self.problemsDetected.append((a,b))
				#check if position is able to be filled
				fillable = False
				for k in range (1,10):
					if self.potentialGrid[k][row][col]:
						fillable = True
						break
				if not fillable:
					#print("Problem detected at (" + str(row) + "," + str(col) + ")") 
					problemDetected = True
					self.problemsDetected.append((row,col))
					#exit()

		#check if a number is able to fill a position in vertical, horizontal, or square
		#
		#
		#

		return problemDetected

	def removeProblems(self):
		for i in self.problemsDetected:
			row = i[0]
			col = i[1]
			if (self.grid[row][col] != 0):
				self.grid[row][col] = 0
			else:
				pass

		self.problemsDetected = []

	def getGridString(self):
		gridString = ""
		for row in range(0,9):
			for col in range(0,9):
				gridString += str(self.grid[row][col])
		return gridString

#solver = SudokuSolver("")

#f solver.solve():
#	print ("The grid is complete.")
#else:
#	print ("The grid is incomplete.")

#solver.printGrid()

#solver.printPotentialGrid()
#solver.printChangeStack()
#solver.outputChangeStack()

#solver.detectProblems()
#print("The total number of guesses: " + str(solver.totalGuessCount))
#print("The current number of guesses: " + str(solver.currentGuessCount))