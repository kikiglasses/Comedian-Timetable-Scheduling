import comedian
import demographic
import ReaderWriter
import timetable
import random
import math

class Scheduler:

	def __init__(self,comedian_List, demographic_List):
		self.comedian_List = comedian_List
		self.demographic_List = demographic_List
		self.schedule={"Monday" : {}, "Tuesday" : {}, "Wednesday" : {}, "Thursday" : {}, "Friday" : {}}
		self.LegalDemos={}				# LegalDemos[comedian.name]=[All Demographics Comedian can perform for]
		self.LegalComs={}				# LegalComs[demographic.reference]=[All Comedians that can perform for Demographic]
		self.LegalTestDemos={}			# As above, but for Test shows
		self.LegalTestComs={}			# As above, but for Test shows
		self.ComedianCount={}			# ComedianCount[comedian.name]=[number of hours in current timetable]
		self.LastAddition=[]			# LastAddition[i]=[the (i+1)th addition to the timetable in the form [Com, Demo, Test]]
		self.WhatAdd=[]					# List of what the last addition(s) were WhatAdd[i]=["Main1", "Main2", "Test1" or "Test4"]
		self.demoMain_List=[]			# Copy of demographic_List for task 3
		self.demoTest_List=[]			# Copy of demographic_List for task 3
		self.considerList=[]			# Copy of demographic_List for task 3


	#################################################################################################################################
		# For Task 1, I started by creating the Order-Domain for every Demographic and Comedian, and stored them in dictionaries.
		# I then used the CSP Backtracking algorithm to search the state space.
		# I sorted the demographic_List at the start in order of best-first so as to avoid unnecessary backtracking.
		# I chose to fill the timetable with empty values so that my isFull() and findFreeSlot functions worked consistently, considering
		# overriding some sessions due to backtracking.

	def createSchedule(self):
		timetableObj = timetable.Timetable(1)
		###
		self.createLegalDicts()					# Populates the Legal Lists
		
		for com in self.comedian_List:			# Sets every count to 0
			self.ComedianCount[com.name]=0

		emptyCom=comedian.Comedian("",list())
		emptyDemo=demographic.Demographic("",list())
		for i in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:				# Fills timetable with empty comedians and demographics
			for j in range(1,6):
				self.addsession(timetableObj, i,j,emptyCom,emptyDemo, "main")

		self.demographic_List.sort(key=lambda x: len(self.LegalComs[x.reference]))# Sorts demographic_List in order of number of possible choices
		for demoref in self.LegalComs:													# Iterate through LegalComs and LegalDemos, sorting each
			self.LegalComs[demoref].sort(key=lambda x: len(self.LegalDemos[x.name]))		# set in order of number of possible choices
		for comnam in self.LegalDemos:
			self.LegalDemos[comnam].sort(key=lambda x: len(self.LegalComs[x.reference]))
		self.backtrack1(timetableObj, 0)
		###
		return timetableObj

	def backtrack1(self, tt, demoind):
		if self.isFull(tt):				# Checks whether the timetable is complete
			return True
		emptyCom=comedian.Comedian("",list())
		emptyDemo=demographic.Demographic("",list())
		for com in self.LegalComs[self.demographic_List[demoind].reference]:	# Searches in order of least possible first=0
			if self.legalToAdd1(com, self.demographic_List[demoind], tt):
				if self.backtrack1(tt, demoind+1):
					return True
		self.ComedianCount[self.LastAddition[len(self.LastAddition)-1][0].name]-=1		# Decrement Comedian Count
		a=self.findInTimetable(tt, self.LastAddition.pop(len(self.LastAddition)-1), 1)	# Find the Comedian, Demographic and test
		self.addsession(tt, a[0],a[1],emptyCom, emptyDemo, "main")						# and clear them from the timetable
		return False			# No choice works - backtrack to previous choice


	# Takes a given Com and Demo, and finds a legal place in the timetable, if one exists, and adds it, then returns True. Otherwise returns False
	def legalToAdd1(self, com, demo, tt):
		if (self.ComedianCount[com.name]==2):			# Checks that the Comedian hasn't performed twice already
			return False
		for day in self.schedule:
			today=True
			for time in self.schedule[day]:
				if self.schedule[day][time][0].name==com.name and self.schedule[day][time][0].themes==com.themes:# Checks if the comedian already has a performance this day
					today=False
			if today:
				timeslot=self.findFreeSlot(day,tt)
				if not timeslot==0:
					self.addsession(tt, day, timeslot, com, demo, "main")
					self.LastAddition.append([com, demo, "main"])
					self.ComedianCount[com.name]+=1
					return True
		return False
	




	#################################################################################################################################
		# Much alike task 1.
		# I alternated between adding main and test shows for each demographic in the demographic_List
		# and backtracked whenever there were no available legal comedians for the selected demographic

	def createTestShowSchedule(self):
		timetableObj = timetable.Timetable(2)
		###
		self.createLegalDicts()					# Populates the Legal Lists
		self.createLegalTestDicts()

		for com in self.comedian_List:			# Sets every count to 0
			self.ComedianCount[com.name]=0

		emptyCom=comedian.Comedian("",list())
		emptyDemo=demographic.Demographic("",list())
		for i in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:				# Fills timetable with empty comedians and demographics
			for j in range(1,11):
				self.addsession(timetableObj, i,j,emptyCom,emptyDemo, "main")
		
		self.demographic_List.sort(key=lambda x: len(self.LegalComs[x.reference]))
		for demoref in self.LegalComs:													# Iterate through LegalComs and LegalDemos, sorting each
			self.LegalComs[demoref].sort(key=lambda x: len(self.LegalDemos[x.name]))		# set in order of least possible choices
			self.LegalTestComs[demoref].sort(key=lambda x: len(self.LegalDemos[x.name]))
		for comnam in self.LegalDemos:
			self.LegalDemos[comnam].sort(key=lambda x: len(self.LegalComs[x.reference]))
			self.LegalTestDemos[comnam].sort(key=lambda x: len(self.LegalComs[x.reference]))
		
		
		self.backtrack2(timetableObj, 0, "main")

		###
		return timetableObj

	def backtrack2(self, tt, demoind, test):	# Recursively finds mathchings and backtracks when mistake is encountered
		if self.isFull(tt):				# Checks whether the timetable is complete
			return True
		emptyCom=comedian.Comedian("",list())
		emptyDemo=demographic.Demographic("",list())
		if test=="main":
			for com in self.LegalComs[self.demographic_List[demoind].reference]:	# Searches in order of least possible first
				if self.legalToAdd2(com, self.demographic_List[demoind], tt, "main"):
					if self.backtrack2(tt, demoind, "test"):
						return True
			self.ComedianCount[self.LastAddition[len(self.LastAddition)-1][0].name]-=1		# Decrement Comedian Count
			a=self.findInTimetable(tt, self.LastAddition.pop(len(self.LastAddition)-1), 2)	# Find the Comedian, Demographic and test
			self.addsession(tt, a[0],a[1],emptyCom, emptyDemo, "main")							# and clear them from the timetable
			return False			# No choice works - backtrack to previous choice
		elif test=="test":
			for com in self.LegalTestComs[self.demographic_List[demoind].reference]:	# Searches in order of least possible first
				if self.legalToAdd2(com, self.demographic_List[demoind], tt, "test"):
					if self.backtrack2(tt, demoind+1, "main"):
						return True
			self.ComedianCount[self.LastAddition[len(self.LastAddition)-1][0].name]-=2		# Decrement Comedian Count
			a=self.findInTimetable(tt, self.LastAddition.pop(len(self.LastAddition)-1), 2)	# Find the Comedian, Demographic and test
			self.addsession(tt, a[0],a[1],emptyCom, emptyDemo, "main")							# and clear them from the timetable
			return False				# No choice works - backtrack to previous choice
		return False


	# Takes a given Com and Demo, and finds a legal place in the timetable and adds it, then returns True. Otherwise returns False
	def legalToAdd2(self, com, demo, tt, test):
		if (self.ComedianCount[com.name]==4)or(test=="main" and self.ComedianCount[com.name]==3):# Checks that adding this performance wouldn't
			return False														# amount to the Comedian performing for more than 4 hours this week
		for day in self.schedule:
			today=0
			for time in self.schedule[day]:
				if self.schedule[day][time][0].name==com.name and self.schedule[day][time][0].themes==com.themes:		# Checks if the comedian already has a performance this day
					if self.schedule[day][time][2]=="test":
						today+=1
					elif self.schedule[day][time][2]=="main":
						today+=2
			if not (today==2 or (test=="main" and today==1)):
				timeslot=self.findFreeSlot(day,tt)
				if not timeslot==0:
					if test=="main":
						self.addsession(tt, day, timeslot, com, demo, "main")
						self.LastAddition.append([com, demo, "main"])
						self.ComedianCount[com.name]+=2
						return True
					elif test=="test":
						self.addsession(tt, day, timeslot, com, demo, "test")
						self.LastAddition.append([com, demo, "test"])
						self.ComedianCount[com.name]+=1
						return True
		return False
	


	#################################################################################################################################
		# I created a timetable that, if successfully filled, always fulfills every possible discount, and therefore is always optimal.
		# It does this by using 12 comedians that each perform 2 main shows on consecutive days, 6 comedians that each perform 4 test shows,
		# and then finds comedians to perform for the remaining main and test show.
		# I duplicated the demographic_List into two lists demoMain_List and demoTest_List which are each sorted for best-first search for their show type.
		# I then made another list called considerList which is demoMain_List concatenated with demoTest_List
		# My program runs the backtracking algorithm over the considerList, looking for comedians that can perform 2 main shows, one for the demographic that we're
		# currently looking at, and another for another demographic. If all the comedians that can perform for the demographic we are on can only perform for that
		# demographic, then we just add the single performance as described above as the remaining main show.
		# After the considerList gets to index 25, the algorithm has assigned all main shows, so repeats for test shows.
	
	def createMinCostSchedule(self):
		timetableObj = timetable.Timetable(3)
		###
		self.createLegalDicts()
		self.createLegalTestDicts()
		emptyCom=comedian.Comedian("",list())
		emptyDemo=demographic.Demographic("",list())
		for i in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:				# Fills timetable with empty comedians and demographics
			for j in range(1,11):
				self.addsession(timetableObj, i,j,emptyCom,emptyDemo, "main")
		
		# Sorts demoTest_List in order of number of possible comedians, then by average number of demographics that those comedians can perform for
		self.demoTest_List=sorted(self.demographic_List, key=lambda x: (len(self.LegalTestComs[x.reference]), self.aveComLen(self.LegalTestComs[x.reference], "test")))

		# Sorts demoMain_List in order of number of possible comedians, then by average number of demographics that those comedians can perform for
		self.demoMain_List=sorted(self.demographic_List, key=lambda x: (len(self.LegalComs[x.reference]), self.aveComLen(self.LegalComs[x.reference], "main")))

		self.considerList.extend(self.demoMain_List)
		self.considerList.extend(self.demoTest_List)

		for demoref in self.LegalComs:													# Iterate through LegalComs and LegalDemos, sorting each
			self.LegalComs[demoref].sort(key=lambda x: len(self.LegalDemos[x.name]))		# set in order of least possible choices
			self.LegalTestComs[demoref].sort(key=lambda x: len(self.LegalDemos[x.name]))
		for comnam in self.LegalDemos:
			self.LegalDemos[comnam].sort(key=lambda x: len(self.LegalComs[x.reference]))
			self.LegalTestDemos[comnam].sort(key=lambda x: len(self.LegalComs[x.reference]))


		try:
			self.backtrack3(timetableObj, 0, False, False)								# Tries to find optimal schedule
		except:
			for i in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:			# Fills timetable with empty comedians and demographics
				for j in range(1,11):
					self.addsession(timetableObj, i,j,emptyCom,emptyDemo, "main")
			self.backtrack2(timetableObj, 0, "main")									# Makes a legal timetable disregarding cost if backtrack3 fails
			
		###
		return timetableObj

	def backtrack3(self, tt, demoind, main, test):
		# First tries to force an optimal solution of cost 10050
		emptyCom=comedian.Comedian("",list())
		emptyDemo=demographic.Demographic("",list())
		if self.isFull(tt):				# Checks whether the timetable is complete
			return True
		if demoind<25:										# Add main shows first
			if not self.considerList[demoind] in self.demoMain_List:		# Check that we haven't already assigned this demographic a main show
				if self.backtrack3(tt, demoind+1, main, test):					# and skips if we have
					return True
			for com in self.LegalComs[self.considerList[demoind].reference]:
				if len(self.LegalDemos[com.name])==1:						# First comedian can only perform for this demographic
					sum=0
					num=0
					for com in self.LegalComs[self.considerList[demoind].reference]:	# Checks that there is not another comedian that can perform for this
						sum+=len(self.LegalDemos[com.name])								# demographic as well as another one
						num+=1
					if (sum/num)==1:
						if main==True:
							return False		# Optimal schedule is not of cost 10050
						main=True
						self.addsession(tt, "Wednesday", 10, com, self.considerList[demoind], "main")		# Only one place to put single main show
						self.LastAddition.append([com, self.considerList[demoind], "main"])
						self.WhatAdd.append("Main1")											# These lines prune all my Main lists as we have assigned this
						self.removeCom(tt, com)													# demographic and comedian all main shows that we are going to assign
						self.removeDemo(tt, self.considerList[demoind], "main")
						self.demoMain_List.remove(self.considerList[demoind])
						if self.backtrack3(tt, demoind+1, main, test):
							return True
				else:
					alreadyVisited=[]
					if not com.name in alreadyVisited:
						alreadyVisited.append(com.name)
						for demo in self.LegalDemos[com.name]:							# For each legal demographic for that comedian
							if not demo==self.considerList[demoind]:						# That is not the same as the first demographic
								a=self.findFree3(tt, main, test)
								self.addsession(tt, a[0], a[2], com, self.considerList[demoind], "main")# Add that comedian performing for the first demographic
								self.addsession(tt, a[1], a[3], com, demo, "main")						# and the second demographic
								self.LastAddition.append([com, self.considerList[demoind], "main"])
								self.LastAddition.append([com, demo, "main"])						# Record adding this so we can backtrack if needed later
								self.WhatAdd.append("Main2")										
								self.removeCom(tt, com)												# These lines prune all my Main lists as we have assigned these
								self.removeDemo(tt, demo, "main")									# demographics and this comedian all main shows that we are going to assign
								self.removeDemo(tt, self.considerList[demoind], "main")
								self.demoMain_List.remove(self.considerList[demoind])
								self.demoMain_List.remove(demo)
								if self.backtrack3(tt, demoind+1, main, test):
									return True
			self.removeLastChoice(tt)
			return False
		
		elif demoind<50:									# Then assign test shows
			if not self.considerList[demoind] in self.demoTest_List:		# Check that we haven't already assigned this demographic a test show
				if self.backtrack3(tt, demoind+1, main, test):
					return True
			for com in self.LegalTestComs[self.considerList[demoind].reference]:
				if len(self.LegalTestDemos[com.name])==1:
					sum=0
					num=0
					for com in self.LegalTestComs[self.considerList[demoind].reference]:	# Checks that there is not another comedian that can perform for this
						sum+=len(self.LegalTestDemos[com.name])								# demographic as well as another one
						num+=1
					if (sum/num)==1:
						if test==True:
							return False					# Optimal schedule is not of cost 10050
						test=True
						self.addsession(tt, "Friday", 10, com, self.considerList[demoind], "test")		# Only one place to put single test show
						self.LastAddition.append([com, self.considerList[demoind], "test"])				# Record adding this so we can backtrack if needed later
						self.WhatAdd.append("Test1")
						self.removeCom(tt, com)															# These lines prune all my Test lists as we have assigned this
						self.removeDemo(tt, self.considerList[demoind], "test")							# demographic and comedian to all test shows that we are going to assign
						self.demoTest_List.remove(self.considerList[demoind])
						if self.backtrack3(tt, demoind+1, main, test):
							return True
				else :
					alreadyVisited=[]
					if not com in alreadyVisited:
						for demo1 in self.LegalTestDemos[com.name]:
							if not demo1==self.considerList[demoind]:						# Looks for 4 different demographics that the comedian
								for demo2 in self.LegalTestDemos[com.name]:				# can perform test shows for
									if not (demo2==self.considerList[demoind]) and not (demo2==demo1):
										for demo3 in self.LegalTestDemos[com.name]:
											if not (demo3==self.considerList[demoind]) and not (demo3==demo1) and not (demo3==demo2):
												a=self.findFree3(tt, main, test)
												self.addsession(tt, a[0], a[2], com, self.considerList[demoind], "test")# Add that comedian performing for the first demographic
												self.addsession(tt, a[0], a[2]+1, com, demo1, "test")					# and the second demographic
												self.addsession(tt, a[1], a[3], com, demo2, "test")						# and the third demographic
												self.addsession(tt, a[1], a[3]+1, com, demo3, "test")					# and the fourth demographic
												self.LastAddition.append([com, self.considerList[demoind], "test"])
												self.LastAddition.append([com, demo1, "test"])							# Record adding this so we can backtrack if needed later
												self.LastAddition.append([com, demo2, "test"])
												self.LastAddition.append([com, demo3, "test"])
												self.WhatAdd.append("Test4")
												self.removeCom(tt, com)									# These lines prune all my Test lists as we have assigned these
												self.removeDemo(tt, self.considerList[demoind], "test")	# demographics and this comedian all test shows that we are going to assign
												self.removeDemo(tt, demo1, "test")
												self.removeDemo(tt, demo2, "test")
												self.removeDemo(tt, demo3, "test")
												self.demoTest_List.remove(self.considerList[demoind])
												self.demoTest_List.remove(demo1)
												self.demoTest_List.remove(demo2)
												self.demoTest_List.remove(demo3)
												if self.backtrack3(tt, demoind+1, main, test):
													return True
			self.removeLastChoice(tt)
			return False
			

	# Function to remove the last addition to the timetable
	def removeLastChoice(self, tt):
		emptyCom=comedian.Comedian("",list())
		emptyDemo=demographic.Demographic("",list())
		a=self.WhatAdd.pop(len(self.WhatAdd)-1)
		
		if a=="Main1":								# Last addition was a comedian performing for a single main show
			a=self.LastAddition.pop(len(self.LastAddition)-1)
			b=self.findInTimetable(tt, a, 3)												# one comedian can perform for only one demographic

			self.demoMain_List.append(a[1])

			self.addsession(tt, b[0], b[1], emptyCom, emptyDemo, "main")

			self.addComToLegals(tt, a[0])
			self.addDemoToLegals(tt, a[1], "main")
			self.demoMain_List.sort(key=lambda x: (len(self.LegalComs[x.reference]), self.aveComLen(self.LegalComs[x.reference], "main")))
		
		elif a=="Main2":							# Last addition was a comedian performing for two main shows
			a=self.LastAddition.pop(len(self.LastAddition)-1)
			b=self.LastAddition.pop(len(self.LastAddition)-1)

			self.demoMain_List.append(a[1])						# Add the removed demographics back to the demographics lists
			self.demoMain_List.append(b[1])

			c=self.findInTimetable(tt, a, 3)						# Find the Comedian, Demographic and test
			d=self.findInTimetable(tt, b, 3)

			self.addsession(tt, c[0], c[1], emptyCom, emptyDemo, "main")	# and clear them from the timetable
			self.addsession(tt, d[0], d[1], emptyCom, emptyDemo, "main")

			self.addComToLegals(tt, a[0])					# Adds the comedian to all legal lists

			self.addDemoToLegals(tt, a[1], "main")					# Adds the two demographics back to their legal lists
			self.addDemoToLegals(tt, b[1], "main")

			self.demoMain_List.sort(key=lambda x: (len(self.LegalComs[x.reference]), self.aveComLen(self.LegalComs[x.reference], "main")))

		elif a=="Test1":							# Last addition was a comedian performing for a single test show
			a=self.LastAddition.pop(len(self.LastAddition)-1)

			self.demoTest_List.append(a[1])

			b=self.findInTimetable(tt, a, 3)

			self.addsession(tt, b[0], b[1], emptyCom, emptyDemo, "main")

			self.addComToLegals(tt, a[0])
			self.addDemoToLegals(tt, a[1], "test")

			self.demoTest_List.sort(key=lambda x: (len(self.LegalTestComs[x.reference]), self.aveComLen(self.LegalTestComs[x.reference], "test"))) # Re-sort the demographic list
		
		elif a=="Test4":							# Last addition was a comedian performing for four test shows
			a=self.LastAddition.pop(len(self.LastAddition)-1)
			b=self.LastAddition.pop(len(self.LastAddition)-1)
			c=self.LastAddition.pop(len(self.LastAddition)-1)
			d=self.LastAddition.pop(len(self.LastAddition)-1)

			self.demoTest_List.append(a[1])						# Add the removed demographics back to the demographics lists
			self.demoTest_List.append(b[1])
			self.demoTest_List.append(c[1])
			self.demoTest_List.append(d[1])

			e=self.findInTimetable(tt, a, 3)						# Find the Comedian, Demographic and test
			f=self.findInTimetable(tt, b, 3)
			g=self.findInTimetable(tt, c, 3)
			h=self.findInTimetable(tt, d, 3)

			self.addsession(tt, e[0], e[1], emptyCom, emptyDemo, "main")	# and clear them from the timetable
			self.addsession(tt, f[0], f[1], emptyCom, emptyDemo, "main")
			self.addsession(tt, g[0], g[1], emptyCom, emptyDemo, "main")
			self.addsession(tt, h[0], h[1], emptyCom, emptyDemo, "main")

			self.addComToLegals(tt, a[0])							# Adds the comedian back to all legal lists

			self.addDemoToLegals(tt, a[1], "test")					# Adds the two demographics back to their legal lists
			self.addDemoToLegals(tt, b[1], "test")
			self.addDemoToLegals(tt, c[1], "test")					# Adds the two demographics back to their legal lists
			self.addDemoToLegals(tt, d[1], "test")

			self.demoTest_List.sort(key=lambda x: (len(self.LegalTestComs[x.reference]), self.aveComLen(self.LegalTestComs[x.reference], "test"))) # Re-sort the demographic list
	
	# Used to sort demo lists. Given a list of comedians
	# Returns the average number of demographics those comedians can perform for
	def aveComLen(self, comlist, test):
			total=0
			num=0
			if test=="main":
				for com in comlist:
					total+=len(self.LegalDemos[com.name])
					num+=1
			elif test=="test":
				for com in comlist:
					total+=len(self.LegalTestDemos[com.name])
					num+=1
			if num==0:
				return 0
			return float(total/num)
		
	# Given how many of each show we have left to assign, determines where the next show will go
	def findFree3(self, tt, main, test):
		a=len(self.demoMain_List)
		b=len(self.demoTest_List)
		c=0
		d=0
		if main==True:				# We have assigned a main show by itself
			c=1
		if test==True:				# We have assigned a test show by itself
			d=1
		if a>5-c:									# FILL MONDAY TUESDAY WITH SAME COMEDIANS MAIN SHOWS
			return ["Monday", "Tuesday", int(0.5*(27-a-c)), int(0.5*(27-a-c))]
		elif a==5-c:								# ADD WEDNESDAY THURSDAY MAIN SHOW
			return ["Wednesday", "Thursday", 1, 1]
		elif a==3-c:								# ADD THURSDAY FRIDAY MAIN SHOW
			return ["Thursday", "Friday", 10, 1]
		elif b==25-d:								# ADD WEDNESDAY THURSDAY TEST SHOW
			return ["Wednesday", "Thursday", 2, 2]
		elif b==21-d:								# ADD WEDNESDAY THURSDAY TEST SHOW
			return ["Wednesday", "Thursday", 4, 4]
		elif b==17-d:								# ADD THURSDAY FRIDAY TEST SHOW
			return ["Thursday", "Friday", 6, 6]
		elif b==13-d:								# ADD THURSDAY FRIDAY TEST SHOW
			return ["Thursday", "Friday", 8, 8]
		elif b==9-d:								# ADD WEDNESDAY FRIDAY TEST SHOW
			return ["Wednesday", "Friday", 6, 2]
		elif b==5-d:								# ADD WEDNESDAY FRIDAY TEST SHOW
			return ["Wednesday", "Friday", 8, 4]
			


	# Removes a specific comedian from all LegalDemos lists
	def removeCom(self, tt, com):
		for demo_ref in self.LegalComs:
			if com in self.LegalComs[demo_ref]:				# Comedian has been assigned their shows,
				self.LegalComs[demo_ref].remove(com)		# so no longer a possible choice for anything
		for demo_ref in self.LegalTestComs:
			if com in self.LegalTestComs[demo_ref]:
				self.LegalTestComs[demo_ref].remove(com)
		return True

	# Removes a specific comedian from all LegalComs or LegalTestComs lists
	def removeDemo(self, tt, demo, test):
		if test=="main":
			for com_name in self.LegalDemos:				# Demographic's main show has been assigned,
				if demo in self.LegalDemos[com_name]:		# so no longer a possible choice
					self.LegalDemos[com_name].remove(demo)
			return True
		elif test=="test":
			for com_name in self.LegalTestDemos:			# Demographic's test show has been assigned,
				if demo in self.LegalTestDemos[com_name]:	# so no longer a possible choice
					self.LegalTestDemos[com_name].remove(demo)
			return True
		return False


	# Re-adds a specific comedian to all LegalComs[demo.reference]
	def addComToLegals(self, tt, com):
		for demo in self.demographic_List:
			count=0
			for demo_topic in demo.topics:
				if demo_topic in com.themes:
					count+=1
			if count==len(demo.topics):							# Adds comedian back to possibilities of performing for main or test shows due to a backtrack
				self.LegalComs[demo.reference].append(com)
			if count>=1:
				self.LegalTestComs[demo.reference].append(com)
		return True
	
	# Re-adds a specific demographic to all LegalDemos[com.name]
	def addDemoToLegals(self, tt, demo, test):
		if test=="main":
			for com in self.comedian_List:
				count=0											# Backtrack means this demographic no longer has a main show assigned
				for demo_topic in demo.topics:					# so add back to lists of possibilities
					if demo_topic in com.themes:
						count+=1
				if count == len(demo.topics):
					self.LegalDemos[com.name].append(demo)
		elif test=="test":
			for com in self.comedian_List:
				count=0											# Backtrack means this demographic no longer has a test show assigned
				for demo_topic in demo.topics:					# so add back to lists of possibilities
					count=0
					if demo_topic in com.themes:
						count=1
				if count == 1:
					self.LegalTestDemos[com.name].append(demo)
		return True

	#################################################################################################################################
		# General use functions
	
	# Creates my Order Domain Dictionaries for Main shows
	def createLegalDicts(self):
		for demo in self.demographic_List:
			self.LegalComs[demo.reference]=[]						# Fill LegalComs with empty lists
		for com in self.comedian_List:
			self.LegalDemos[com.name]=[]							# Fill LegalDemos with empty lists
			for demo in self.demographic_List:
				count=0
				for demo_topic in demo.topics:
					if demo_topic in com.themes:
						count+=1
				if count == len(demo.topics):					# Adds only if every topic is one of the comedian's themes
					self.LegalDemos[com.name].append(demo)		# Appends legal demographic to LegalDemos
					self.LegalComs[demo.reference].append(com)	# Appends legal comedian to LegalComs


	# Creates my Order Domain Dictionaries for Test shows
	def createLegalTestDicts(self):
		for demo in self.demographic_List:
			self.LegalTestComs[demo.reference]=[]						# Fill LegalTestComs with empty lists
		for com in self.comedian_List:
			self.LegalTestDemos[com.name]=[]							# Fill LegalTestDemos with empty lists
			for demo in self.demographic_List:
				count=0
				for demo_topic in demo.topics:
					if demo_topic in com.themes:
						count=1
				if count == 1:										# Adds only if one topic is one of the comedian's themes
					self.LegalTestDemos[com.name].append(demo)		# Appends legal demographic to LegalTestDemos
					self.LegalTestComs[demo.reference].append(com)	# Appends legal comedian to LegalTestComs


	# Because preamble does not include the use of timetable.schedule, I mimic all additions to the schedule,
	# and can then access my copy of the schedule
	def addsession(self, tt, day, timeslot, com, demo, test):
		self.schedule[day][timeslot] = [com, demo, test]
		tt.addSession(day, timeslot, com, demo, test)


	def findFreeSlot(self,day,tt):		# Finds a free slot in a day and returns it. Returns 0 if no slot exists
		for time in self.schedule[day]:
			if self.schedule[day][time][0].name=="" and self.schedule[day][time][0].themes==[]:
				return time
		return 0


	def isFull(self,tt):				# Checks whether the schedule is full
		for day in self.schedule:
			if not self.findFreeSlot(day,tt)==0:
				return False
		return True

	# Finds the day and time of [Comedian, Demographic, Show Type] in the timetable
	def findInTimetable(self, tt, comdemotest, task):
		for i in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
			if task==1:
				for j in range(1,6):
					if self.schedule[i][j]==comdemotest:
						return [i,j]
			elif task==2 or task==3:
				for j in range(1,11):
					if self.schedule[i][j]==comdemotest:
						return [i,j]