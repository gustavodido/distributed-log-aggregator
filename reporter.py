# -*- coding: utf-8 -*-

#
# Generate a report to validate the worker program
#

import sys
import os
import re
import datetime

# Use default values or prompt the user for them, constants could be in a class to avoid global variables

USER_ID_REGEXP = re.compile(r'userid=(.*)"')
TIMESTAMP_REGEXP = re.compile(r'\[(.*)\]')

class Reporter:
	def __init__(self, folders):
		self.folders = folders
		self.users = {} # dictionary for users time stamp
		
	def __analyze_entry(self, entry):
		user_id = str(USER_ID_REGEXP.search(entry).group(1))
		str_timestamp = str(TIMESTAMP_REGEXP.search(entry).group(1))
		timestamp = datetime.datetime.strptime(str_timestamp, "%d/%b/%Y:%H:%M:%S +0000")

		if user_id not in self.users:
			self.users[user_id] = [timestamp, timestamp]
		else:
			pair = self.users[user_id]
			if timestamp < pair[0]:
				self.users[user_id] = [timestamp, pair[1]]
			if timestamp > pair[1]:
				self.users[user_id] = [pair[0], timestamp]

	def __analyze_file(self, file_name):
		with open(file_name, "r") as file:
			for line in file:
				self.__analyze_entry(line);

	def report(self):
		# Source files
		for folder in self.folders:
			file_list = os.listdir(folder)
			for file in file_list:				
				if os.path.isfile(folder + "/" + file):
					self.__analyze_file(folder + "/" + file);
		
		for user in self.users:
			print (user + " - {} - {}").format(self.users[user][0], self.users[user][1])


reporter = Reporter( ["server01", "server02", "server03", "server04"]) # Servers
reporter.report();
