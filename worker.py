# -*- coding: utf-8 -*-

#
# Read and group the log entries by userid
#

import os
import threading
import re
import datetime

# Use default values or prompt the user for them, constants could be in a class to avoid global variables

USER_ID_REGEXP = re.compile(r'userid=(.*)"')
TIMESTAMP_REGEXP = re.compile(r'\[(.*)\]')

# Class to manage the user file management
class UserManager:
	def __init__(self, storage, folders):
		self.users = {}
		self.storage = storage + "/repository"	

		# Save the max timestamp for each folder to help the flush mechanism
		self.folders = {}
		for folder in folders:
			self.folders[folder] = datetime.datetime.min

	def set_folder_complete(self, folder):
		self.folders[folder] = datetime.datetime.max

	def __remove_flushed(self, min_date):
		for userid in self.users:
			for t in self.users[userid]:
				if t[0] <= min_date:
					self.users[userid].remove(t)

	def __flush(self, min_date):
		for userid in self.users:	
			with open(self.storage + "/" + userid + ".tmp", "a") as file:
				tuples = self.users[userid];
				for t in tuples:
					if t[0] <= min_date:
						file.write(str(t[1]))					
		
	def flush_if_possible(self):
		# If the sorted buffers has a common (not just equal) max timestamp, we can flush the user entries

		# First, we sort the entries
		for userid in self.users:
			if self.users[userid] is not None:
				self.users[userid].sort(key = lambda tup: tup[0])

		# Get the min date that we can flush from folders
		min_date = datetime.datetime.max
		for folder in self.folders:
			min_date = min(min_date, self.folders[folder])

		# Flush all entries earlier than the min date
		if min_date > datetime.datetime.min:
			self.__flush(min_date)
			self.__remove_flushed(min_date)	

	def create_repository(self):
		if not os.path.exists(self.storage):
			os.makedirs(self.storage)

	def process_entry(self, entry, folder):
		user_id = str(USER_ID_REGEXP.search(entry).group(1))
		str_timestamp = str(TIMESTAMP_REGEXP.search(entry).group(1))
		timestamp = datetime.datetime.strptime(str_timestamp, "%d/%b/%Y:%H:%M:%S +0000")
		
		# Add the entry to the buffer
		if user_id not in self.users or self.users[user_id] is None:
			self.users[user_id] = [(timestamp, entry)]
		else:
			self.users[user_id].append((timestamp, entry))
		
		# Update the last timestamp for the folder		
		if timestamp > self.folders[folder]:			
			self.folders[folder] = timestamp;			

	def get_users(self):
		return self.users;
	
# Worker class
class Worker(threading.Thread):
	def __init__(self, user_manager, folder, lock):
		threading.Thread.__init__(self)
		self.user_manager = user_manager
		self.folder = folder
		self.lock = lock

	def __process_file(self, file_name):
		with open(file_name, "r") as file:
			for line in file:
				self.lock.acquire()
				self.user_manager.process_entry(line, self.folder);		
				self.lock.release()	

	def run(self):
		# We could return from the OS the file list ordered, but it is not the main point of the challenge
		current_file_number = 0;
		file_found = True
		while True:
			file_name = (self.folder + "/access{}.log").format(current_file_number)
			if os.path.isfile(file_name):
				self.__process_file(file_name)	
				current_file_number += 1	
			else:				
				self.lock.acquire()
				self.user_manager.set_folder_complete(self.folder)
				self.user_manager.flush_if_possible()
				self.lock.release()
				break

# Console application
folder_list = ["server01", "server02", "server03", "server04"]

user_manager = UserManager('server01', folder_list)
user_manager.create_repository()	

# One worker for each server/folder
threads = []

# A lock object to synchronize the entry creation
lock = threading.Lock()

for folder in folder_list:
	threads.append(Worker(user_manager, folder, lock))

# Start and wait for threads
[x.start() for x in threads]
[x.join() for x in threads]




