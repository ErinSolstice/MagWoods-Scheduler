from kivy.app import App

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.properties import ObjectProperty, StringProperty, ListProperty

import pandas
import ast
from random import randint
from time import sleep

class autoScheduler():
	shifts = [[{'name':'0'}, {'name':'0'}, {'name':'0'}, {'name':'0'}], [{'name':'0'}, {'name':'0'}, {'name':'0'}, {'name':'0'}], [{'name':'0'}, {'name':'0'}, {'name':'0'}, {'name':'0'}], [{'name':'0'}, {'name':'0'}, {'name':'0'}, {'name':'0'}], [{'name':'0'}, {'name':'0'}, {'name':'0'}, {'name':'0'}], [{'name':'0'}, {'name':'0'}, {'name':'0'}, {'name':'0'}], [{'name':'0'}, {'name':'0'}, {'name':'0'}, {'name':'0'}], [{'name':'0'}, {'name':'0'}, {'name':'0'}, {'name':'0'}], [{'name':'0'}, {'name':'0'}, {'name':'0'}, {'name':'0'}], [{'name':'0'}, {'name':'0'}, {'name':'0'}, {'name':'0'}], [{'name':'0'}, {'name':'0'}, {'name':'0'}, {'name':'0'}], [{'name':'0'}, {'name':'0'}, {'name':'0'}, {'name':'0'}]]

	def schedule(self):
		fields = []
		inputError = []
		
		# Function for assigning people to shifts considering role, max shifts, no repeat assignments, number of shifts
		def assignShifts(reps:int, personnel:list):
			for i in range(len(shifts)):
				generated = False
				for j in range(reps):
					# Randomly selects a person to add to the shift until one is added
					for k in range(100):
		###				sleep(1)
						# Random index for personnel list generated
						num = randint(0, len(personnel) - 1)
		###				print(num)
						person = personnel[num]
		###				print(person)
						# Check if current # of shifts < max shifts
		###				print(person["shifts"] < person["max shifts"])
						if person["shifts"] >= person["max shifts"]:
							personnel.pop(num)
						else:
							# Check if not already assigned to shift
		###					print(i not in person["shift days"])
							if i not in person["shift days"]:
								# Check if person does not have more shifts than anyone else
		###						print(person["shifts"] == min([row["shifts"] for row in personnel]))
								if person["shifts"] == min([row["shifts"] for row in personnel]):
									shifts[i].append(person)
									person["shifts"] += 1
									person["shift days"].append(i)
									if i in person["shifts open"]:
										person["shifts open"].remove(i)
									generated = True
									break
				if not(generated):
					print("Schedule failed to fill some shifts.\nCheck that there are enough guards available to cover all shifts.")
		
		csv = csvHandler()
		allPersonnel = csv.csvReader('temporary')
		
		print(allPersonnel)
		
		# Prints out the lines with errors in the role if there are any
		if len(inputError) != 0:
			print("There was an error in parsing the role data from the following rows.")
			print(*inputError, sep = "\n")
		
		# Defines all the names of the shifts
		shiftNames = ["mon1", "tue1", "tue2", "wed1", "wed2", "thu1", "thu2", "fri1", "fri2", "sat1", "sat2", "sun1"]
		
		for row in allPersonnel.index:
			for i, day in enumerate(shiftNames):
				if allPersonnel.loc[row, 'pressed'][day] == 0:
					allPersonnel.loc[row, 'shifts open'].append(i)
			# Checking number of days in time on to determine max possible shifts
			allPersonnel.loc[row, 'max shifts'] = sum([allPersonnel.at[row, 'pressed'][key] == 0 for key in shiftNames])
			# Decreasing max shifts to account for not assigning double shifts
			for i in range(len(shiftNames) - 1):
				if shiftNames[i][:3] == shiftNames[i+1][:3]:
					if allPersonnel.loc[row, 'pressed'][shiftNames[i]] == 0 and allPersonnel.loc[row, 'pressed'][shiftNames[i+1]] == 0:
						allPersonnel.loc[row, 'max shifts'] -= 1
		
		###headGuards = allPersonnel[allPersonnel['role'] == 'Head Guard'].to_dict('records')
		###allGuards = allPersonnel[allPersonnel['role'].isin(['Head Guard', 'Guard'])].to_dict('records')
		allPersonnel = allPersonnel.to_dict('records')
		
		headGuards = []
		allGuards = []
		inputError = []
		
		for person in allPersonnel:
			if person["role"] == "Head Guard":
				headGuards.append(person)
				allGuards.append(person)
			elif person["role"] == "Guard":
				allGuards.append(person)
			# Catch any errors in the role entry
			else:
				inputError.append(person)
		
		print(allGuards)
		print(allPersonnel)
		
		shifts = [[], [], [], [], [], [], [], [], [], [], [], []]
		
		# Assigning a single Head Guard
		assignShifts(1, headGuards)
		# Assigning two remaining guards
		assignShifts(3, allGuards)
		
		for row in shifts:
			print(*row, sep = "\n")
			print()
		# Test code to see original shifts	
		print("Original Shifts")
		for i, shift in enumerate(shifts):
			print("\n%s" % shiftNames[i])	
			for row in shift:
				# Checks the the person is available for the shift
				if row["pressed"][shiftNames[i]] == 0:
					# Checks the person is only scheduled once for the shift
					if sum([k["name"] == row["name"] for k in shift]) == 1:
						print(row["name"], row["role"], row["shifts"])
					else:
						print(row["name"], row["role"], row["shifts"], "is scheduled twice for this shift")
				else:
					print(row["name"], row["role"], row["shifts"], "has requested this as time off")
		
		conflicts = []
		for i in range(len(shifts)):
			for j in range(len(shifts[i])):
				if shifts[i][j]["pressed"][shiftNames[i]] == 1:
					print(shifts[i][j]["name"], "does not want to work", shiftNames[i])
					conflicts.append((i,j))
		
		###conflictsOld = [[],[]]
		###for i in range(len(shifts)):
		###	for j in range(len(shifts[i])):
		###		if shifts[i][j]["time off"].find(shiftNames[i]) != -1:
		###			print(shifts[i][j]["name"], "does not want to work", shiftNames[i])
		###			conflictsOld[0].append(i)
		###			conflictsOld[1].append(j)
		
		print(conflicts)
		###print(conflictsOld)
		
		inc = 0
		roleLocDict = {"Head Guard":(0,3), "Guard":(0,3)}
		for i in range(1000):
		###	print("i is ", i)
		
			# Checks if inc is out of of the list of conlicts
			if inc > len(conflicts) - 1:
				inc = 0
		
			# Checks that conflicts still exist, if not terminates
			if len(conflicts) > 0:
		###		print(conflicts)
		###		print(inc)
				row1 = conflicts[inc][0]
				col1 = conflicts[inc][1]
				inc += 1
		
				resolved = False
				for j in range(100):
		###			print("j is ", j)
		###			print(shifts[row1][col1]["shifts open"])
		###			print(shifts[row1][col1])
					person1 = shifts[row1][col1]
		
					# Selects day of second shift by looking at shifts the first is able to work
					row2 = person1["shifts open"][randint(0, len(person1["shifts open"]) - 1)]
					# Selects person on second shift by selecting tuple of column range of that role
					col2 = randint(*roleLocDict[person1["role"]])
		
					person2 = shifts[row2][col2]
		# Testing of two guard thing			
					person1, person2 = person2, person1
		
					# Checks if after switching there is still a Head Guard in each shift
					if sum([person["role"] == "Head Guard" for person in shifts[row1]]) >= 1 and sum([person["role"] == "Head Guard" for person in shifts[row2]]) >= 1:
						# Checks if role of selected personnel is compatible
						if (person1["role"] == person2["role"]) or ("Guard" in person1["role"] and "Guard" in person2["role"]):
		
							person2["shift days"].append(row2)
							person2["shift days"].remove(row1)
		###					print("Person1", person2["name"], end = " ")
		###					print(row1 in person2["time on"], end = " ")
		###					print(person2["shifts open"], end = " ")
		###					print(row1)
							if person2['pressed'][shiftNames[row1]] == 0: #row1 in person2["time on"]:
								person2["shifts open"].append(row1)
							if row2 in person2["shifts open"]:
								person2["shifts open"].remove(row2)
		
							person1["shift days"].append(row1)
							person1["shift days"].remove(row2)
		###					print("Person2", person1["name"], end = " ")
		###					print(row2 in person1["time on"], end = " ")
		###					print(person1["shifts open"], end = " ")
		###					print(row2)
							if person1['pressed'][shiftNames[row2]] == 0: #row2 in person1["time on"]:
								person1["shifts open"].append(row2)
							if row1 in person1["shifts open"]:
								person1["shifts open"].remove(row1)
					
							shifts[row1][col1] = person1
							shifts[row2][col2] = person2
		
		###					print(row1 in person1["time on"])
							if person1['pressed'][shiftNames[row1]] == 0: #row1 in person1["time on"]:
		###						print(sum([k["name"] == person1["name"] for k in shifts[row1]]))
								if sum([k["name"] == person1["name"] for k in shifts[row1]]) == 1:
									inc -= 1
									conflicts.pop(inc)
									print("Schedule Complete")
									resolved = True
		
							if (row2, col2) in conflicts:
								if inc >= conflicts.index((row2, col2)):
									inc -= 1
		###						message = "Redundant conflict successfully removed"
								conflicts.remove((row2, col2))
							
							# If conflict has been resolved quit loop
							if resolved:
								break
						else:
							print("Roles did not match, loop iteration quit")
					else:
						person1, person2 = person2, person1
		
			else:
				break
		
		print("Remaining conflicts:", conflicts)
		#####conflictsOld = list(conflicts)
		
		# Making record of people with conflicts before attempting to find replacements
		conflictsPeople = [shifts[row[0]][row[1]] for row in conflicts]
		for (person, entry) in zip(conflictsPeople, conflicts):
			person["conflicts"] = entry
			
		#####print(*conflictsPeople, sep = "\n")
		for person in conflictsPeople:
			print("Conflicts remaining:", person["name"], person["role"], person["conflicts"])
		
		#####conflictsPeopleRem = []
		#####conflictsRemoved = []
		roleListDict = {"Head Guard":allGuards, "Guard":allGuards}
		for i in range(10):
			if len(conflicts) <= 0:
				break
			for entry in conflicts:
				# Randomly selects a desk agent to add to the shift until one is added
				personnel = list(roleListDict[shifts[entry[0]][entry[1]]["role"]])
				for k in range(100):
		###			sleep(1)
					# Random index for personnel list generated
					if len(personnel) == 0:
						break
					num = randint(0, len(personnel) - 1)
		###			print(num)
					person = personnel[num]
		###			print(person)
					# Cheking if person is available for shift
					# print(i in allPersonnel.at[row, 'time on'])
					if entry[0] in person["shifts open"]:
						# Check if current # of shifts < max shifts
		###				print(person["shifts"] < person["max shifts"])
						if person["shifts"] < person["max shifts"]:
							# Check if not already assigned to shift
		###					print(i not in person["shift days"])
							if i not in person["shift days"]:
								# Check if desk agent does not have more shifts than anyone else
		###						print(person["shifts"] == min([row["shifts"] for row in personnel]))
								if person["shifts"] == min([row["shifts"] for row in personnel]):
									shifts[entry[0]][entry[1]]["shift days"].remove(entry[0])
									shifts[entry[0]][entry[1]]["shifts"] -= 1
									conflicts.remove(entry)
		#####							conflictsRemoved.append(entry)
		#####							conflictsPeopleRem.append(shifts[entry[0]][entry[1]])
		#####							conflictsPeopleRem[-1]["conflict"] = entry
									shifts[entry[0]][entry[1]] = person
									person["shifts"] += 1
									person["shift days"].append(entry[0])
									person["shifts open"].remove(entry[0])
									break
						else:
							personnel.pop(num)
					else:
						personnel.pop(num)
		
		print(conflicts)
		#####print(conflictsOld)
		#####print(*conflictsPeople, sep = "\n")
		
		#####print("Conflicts Removed")
		#####print(*conflictsPeopleRem, sep = "\n")
		
		for person in conflictsPeople:
			if person["conflicts"] not in conflicts:
				print("Conflicts removed:", person["name"], person["role"], person["conflicts"])
		
		for person in conflictsPeople:
			if person["conflicts"] in conflicts:
				print("Failed to replace conflict:", person["name"], person["role"], person["conflicts"])
		
		print("New Shifts")
		for i, shift in enumerate(shifts):
			print("\n%s" % shiftNames[i])	
			for row in shift:
				# Checks the the person is available for the shift
				if row["pressed"][shiftNames[i]] == 0:
					# Checks the person is only scheduled once for the shift
					if sum([k["name"] == row["name"] for k in shift]) == 1:
						print(row["name"], row["role"], row["shifts"])
					else:
						print(row["name"], row["role"], row["shifts"], "is scheduled twice for this shift")
				else:
					print(row["name"], row["role"], row["shifts"], "has requested this as time off")
		
		###for row in shifts:
		###	print(*row, sep = "\n")
		###	print()
		autoScheduler.shifts = shifts
		return shifts

class TimeOffScreen(Screen, autoScheduler):
	def __init__(self, **kwargs):
		super(TimeOffScreen, self).__init__(**kwargs)
		self.days = ['mon1', 'tue1', 'tue2', 'wed1', 'wed2', 'thu1', 'thu2', 'fri1', 'fri2', 'sat1', 'sat2', 'sun1']
		self.color = [(1, 1, 1, 1), (1, 0, 1, 1)]
		self.csv = csvHandler()
		self.allPersonnel = self.csv.csvReader()
		self.name = ''
		self.person = self.allPersonnel.loc[0]
		self.pressed = self.person['pressed']

#	def dropdown():
#		dropdown = DropDown()
#		for index in range(10):
#		    # When adding widgets, we need to specify the height manually
#		    # (disabling the size_hint_y) so the dropdown can calculate
#		    # the area it needs.
#		
#		    btn = Button(text='Value %d' % index, size_hint_y=None, height=44)
#		
#		    # for each button, attach a callback that will call the select() method
#		    # on the dropdown. We'll pass the text of the button as the data of the
#		    # selection.
#		    btn.bind(on_release=lambda btn: dropdown.select(btn.text))
#		
#		    # then add the button inside the dropdown
#		    dropdown.add_widget(btn)
	def initialize(self):
		for day in self.days:
			button = self.ids[day]
			button.background_color = self.color[self.pressed[day]]

	def personSelect(self, name):
		self.name = name
		self.person = self.allPersonnel.loc[self.allPersonnel['name'] == self.name].iloc[0]
		self.pressed = self.person['pressed']
		self.initialize()
		
	def button_press(self, day:id):
		self.pressed[day] = 1 - self.pressed[day]
		button = self.ids[day]
		button.background_color = self.color[self.pressed[day]]

	def writeCSV(self, saveFile = 'temporary'):
		self.csv.csvWriter(saveFile)

	def clearAllTimeOff(self):
		for row in self.allPersonnel.index:
			for key in self.allPersonnel.loc[row, 'pressed']:
				self.allPersonnel.loc[row, 'pressed'][key] = 0
		self.initialize()

	def clearTimeOff(self):
		for key in self.person['pressed']:
			self.person['pressed'][key] = 0
		self.initialize()

	def weekOff(self):
		for key in self.person['pressed']:
			self.person['pressed'][key] = 1
		self.initialize()

	def makeSchedule(self):
		self.csv.csvWriter('temporary')
		auto = autoScheduler()
		scheduledShifts = auto.schedule()
		self.manager.current = 'ScheduleScreen'

class ScheduleScreen(Screen, autoScheduler):
	shifts = ListProperty(autoScheduler.shifts)
	def update(self):
		self.shifts = autoScheduler.shifts
	pass

class ScreenManager(ScreenManager):
	manager = ObjectProperty(None)
	pass

class csvHandler():
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.fileRead = "personnelPermanent.txt"
		self.fileWrite = "personnelTemporary.txt"
		self.df = 0

	def clean(self, x):
		return ast.literal_eval(x)

	def csvReader(self, readFile = 'permanent'):
		self.df = pandas.read_csv(self.fileRead, quotechar='"', sep=',',converters={'shift days':self.clean, 'shifts open':self.clean, 'pressed':self.clean})
		if readFile == 'temporary':
			self.df = pandas.read_csv(self.fileWrite, quotechar='"', sep=',',converters={'shift days':self.clean, 'shifts open':self.clean, 'pressed':self.clean})
		return self.df

	def csvWriter(self, saveFile = 'temporary'):
		if saveFile == 'temporary':
			self.df.to_csv(self.fileWrite, index = False)
		elif saveFile == 'permanent':
			self.df.to_csv(self.fileRead, index = False)
		else:
			print('Error file to save to doesn\'t exist')

class SchedulerApp(App):
	def build(self):
		csv = csvHandler()
		df = csv.csvReader()
		man = ScreenManager()
		g = TimeOffScreen()
		dropdown = DropDown()
		for row in df.index:
			button = Button(text=df.loc[row, 'name'], size_hint=(None, None), height=45, width = 150)
			button.bind(on_release=lambda button: dropdown.select(button.text))
			dropdown.add_widget(button)
			dropdown.bind(on_select=lambda instance, x: g.personSelect(x))
#		g.mainbutton = Button(text ='Hello', size_hint =(None, None), pos =(350, 300)) 
  
# show the dropdown menu when the main button is released 
# note: all the bind() calls pass the instance of the caller  
# (here, the mainbutton instance) as the first argument of the callback 
# (here, dropdown.open.). 
		g.mainbutton.bind(on_release = dropdown.open) 
  
# one last thing, listen for the selection in the  
# dropdown list and assign the data to the button text. 
		dropdown.bind(on_select = lambda instance, x: setattr(g.mainbutton, 'text', x)) 	
		man.add_widget(g)
		return man

if __name__ == "__main__":
	SchedulerApp().run()
