print("Importing libraries...")

import numpy as np
import matplotlib.pyplot as plt
import subprocess
import os
import sys
from PIL import Image
import re

dosql = sys.argv[1]

if dosql == "true":
	dosql = True
	import mysql.connector
else:
	dosql = False

time_break_interval = 60

print("Enter parent stem directory - the directory which contains the folder of all observations: ")
parent_stem = input("Leave blank to autoset to /Volumes/SETI_DATA/ : ")

if parent_stem == '':
	parent_stem = "/Volumes/SETI_DATA/"

print()
print("Enter the subfolder in which the observations are stored: ")
obs_dir = input("Leave blank to autoset to new_obs/ : ")

if obs_dir == '':
	obs_dir = "new_obs/"

print()
print("Enter the folder for the database: ")
database_dir = input("Leave blank to autoset to obs_database/ in the same dir as the obs folder : ")
if database_dir == '':
	database_dir = parent_stem + "obs_database/"

print("Scanning parent directory...")

obs_list = [f.path.split("/")[-1] for f in os.scandir(parent_stem + obs_dir) if f.is_dir()]

print("Initializing database directory...")

if os.path.isdir(database_dir):
	pass
else:
	os.mkdir(database_dir)


dblist = os.listdir(database_dir)

if dosql:
	cnx = mysql.connector.connect(user=sys.argv[2], password=sys.argv[3],
                              host='127.0.0.1',
                              database='obs_info')

	cnx.close()

print("Scanning observation directories...")

for obs in obs_list:
	#check/conditionally make directories for each obs
	if os.path.isdir(database_dir + obs): 
		pass
	else: 
		os.mkdir(database_dir + obs)

