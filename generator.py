# -*- coding: utf-8 -*-

#
# Generate a test scenario for the challenge
#

import sys
import uuid
import random
import datetime
import os

# Use default values or prompt the user for them, constants could be in a class to avoid global variables

LOG_ENTRY_MASK = '177.126.180.83 ­ ­ [{}] "GET /meme.jpg HTTP/1.1" 200 2148 "­" "userid={}"' # Just the time and user id are relevant

# Generator class

class Generator:
	def __init__(self, folders, number_of_files, number_of_entries, number_of_users):
		self.folders = folders
		self.number_of_files = number_of_files
		self.number_of_entries = number_of_entries
		self.number_of_users = number_of_users
		self.base_datetime = datetime.datetime.now()
		
	def __generate_folder(self, folder):
		# Could generate a race condition if the path is created between the if and the mkdir calls
		# however this is a simple application to generate our test scenario
		if not os.path.exists(folder):
			os.makedirs(folder)

	def __generate_users(self):
		# Creates an array of uuids for the users
		self.users = []
		for i in range(0, self.number_of_users):
			str_uuid = str(uuid.uuid4()).replace("-", "")
			self.users.append(str_uuid)	

	def __generate_files(self, file_name, number_of_entries):
		with open(file_name, "w") as file:
			for i in range(0, number_of_entries):
				# Choose a random user
				user = self.users[random.randint(0, self.number_of_users - 1)]	
	
				# Create the timestamp, python datetime objects are "naive", so I am hard coding the UTC time zone for simplicity
				# In addition, I am inserting one entry every second (approximately)
				self.base_datetime = (self.base_datetime + datetime.timedelta(0, 1)) 
				
				# Generate the entry
				file.write(LOG_ENTRY_MASK.format(self.base_datetime.strftime("%d/%b/%Y:%H:%M:%S +0000"), user) + "\n")	

	def generate(self):
		self.__generate_users()
		
		# Shuffle folders for a better experience
		random.shuffle(self.folders)
		
		# The server can have multiple files, but they are time sorted as well		
		for folder in self.folders:
			# Since the user is random, the file can be sequential
			for i in range(0, self.number_of_files):
				self.__generate_folder(folder)

				file_name = folder + "/" + "access" + str(i) + ".log"	
				self.__generate_files(file_name, self.number_of_entries)


# Console application

generator = Generator(	["server01", "server02", "server03", "server04"], # Servers
			10, 						  # Files
			100,						  # Entries in each files
			10)						  # Distinct users
generator.generate()

