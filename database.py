print("Importing libraries...")

import numpy as np
from blimpy import Waterfall
import matplotlib.pyplot as plt
from blimpy.io.fil_reader import FilReader
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

config = input("Would you like to initialize from a config file? (y/n) : ")

if config != 'y': config = False
if config == 'y': config = True

if config:
    init_info = open("config.txt", "r")
    init_info = init_info.read()
    init_info = init_info.split("\n")
    parent_stem = init_info[0]
    obs_dir = init_info[1]
    database_dir = init_info[2]
else:
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

#here's where most of the processing occurs
for obs in obs_list:
	#check/conditionally make directories for each obs
	if os.path.isdir(database_dir + obs): 
		pass
	else: 
		os.mkdir(database_dir + obs)

	#get files/directories in the obs dir
	this_obs_subdir = [f.path.split("/")[-1] for f in os.scandir(parent_stem + obs_dir + obs) if f.is_dir()]

	print(obs)

	if "sql.written" in os.listdir(database_dir + obs):
		pass
	else:
		antennalist = ['1a', '1c', '1f', '1k', '2a', '2h', '4g', '4j', '5c']
		for antenna in antennalist:
			try:
				f = open(parent_stem + obs_dir + obs + "/" + antenna + "/obs.header")
				f = f.read()
				break
			except FileNotFoundError:
				pass

		if dosql:
			f = f.split('\n')
			f = [re.sub("\s+", ",", line.strip()) for line in f]

			for line in f:
				elements = line.split(",")
				if "SOURCE" in line:
					source = elements[1]
				if "UTC_START" in line:
					utc = elements[1]

			time = utc.split("-")[-1]
			date = utc.replace(time, '')[:-1]

			command = '''insert into obs_details (obs_name, source, date, time) values
						("''' + obs + '''", "''' + source + '''", "''' + date + '''", "''' + time + '''")
						'''

			cnx = mysql.connector.connect(user=sys.argv[2], password=sys.argv[3],
	                              host='127.0.0.1',
	                              database='obs_info')

			cnx.cursor().execute(command)

			cnx.commit()

			cnx.close()

			f = open(database_dir + obs + "/sql.written", "w")
			f.close()

		else:
			writeheader = open(database_dir + obs + "/obs.header", "w")
			writeheader.write(f)
			writeheader.close()

	#look at sub-directories inside the obs dir
	for subd in this_obs_subdir:

		f_dir = database_dir + obs + "/" + subd

		obs_f_dir = parent_stem + obs_dir + obs + "/" + subd

		if os.path.isdir(f_dir): 
			if "data.written" in os.listdir(database_dir + obs + "/" + subd):
				continue
			else:
				pass
		else: 
			os.mkdir(f_dir)

		if "ics" in subd:
			if "candidates" in os.listdir(obs_f_dir):
				if not os.path.isdir(f_dir + "/candidates"):
					os.mkdir(f_dir + "/candidates")

				if "cands.written" in os.listdir(f_dir + "/candidates"):
					pass

				else:
					imagelist = [f for f in os.scandir(obs_f_dir + "/candidates") if (".png" in f.path)]

					for fname in imagelist:
						img = Image.open(fname.path)
						img = img.resize((int(img.size[0]/2), int(img.size[1]/2)), Image.ANTIALIAS)
						img.save(f_dir + "/candidates/" + fname.path.split("/")[-1])

					f = open(f_dir + "/candidates/cands.written", "w")
					f.close()

		print("\t|" + subd)

		#get a list of .fil files inside each sub-directory inside each obs dir
		file_list = [f.path.split("/")[-1] for f in os.scandir(obs_f_dir) if (".fil" in f.path)]


		for file in file_list:


			print("\t\t|" + file)

			#get the sampling time
			try:
				f = Waterfall(obs_f_dir + "/" + file, t_start=0, t_stop=1)
			except NotImplementedError:
                                print("Flagging " + obs + "...")
                                f = open("obs.flagged", "a")
                                f.write(obs + "/" + subd + "/" + file + "\n")
                                f.close()
                                continue

			sampling_time = f.header['tsamp']

			#if "ics" in file:
			fsize = os.path.getsize(obs_f_dir + "/" + file) - sys.getsizeof(f.header)
			samples = round(fsize / (f.header['nchans'] * (f.header['nbits'] / 8)))
			obs_time = samples * sampling_time
			print("\t\t|OBS TIME: " + str(obs_time) + "s")
			plot_w_log = False
			if (f.header['nbits'] == 32):
				plot_w_log = True

			for tstamp in range(0, int(float(obs_time)), time_break_interval):
				try:
					start = int(tstamp/sampling_time)
					stop = int((tstamp + time_break_interval)/sampling_time)

					f = Waterfall(obs_f_dir + "/" + file, t_start=start, t_stop=stop)

					f.plot_waterfall(logged = plot_w_log)

					#modify the yticks appropriately
					plt.yticks(np.arange(0, time_break_interval, 5), np.arange(0, time_break_interval, 5) + tstamp)

					plt.savefig(f_dir + "/" + file + '_waterfall_' + str(tstamp) + "s_to_" + str(tstamp+time_break_interval) + 's_.png')
					plt.clf()


					#plot the spectrum
					f.plot_spectrum(logged = plot_w_log)

					plt.savefig(f_dir + "/" + file + '_spectrum_' + str(tstamp) + "s_to_" + str(tstamp+time_break_interval) + 's_.png')
					plt.clf()


					#plot the timeseries
					f.plot_time_series()

					#modify the xticks appropriately
					plt.xticks(np.arange(0, time_break_interval, 5), np.arange(0, time_break_interval, 5) + tstamp)

					plt.savefig(f_dir + "/" + file + '_timeseries_' + str(tstamp) + "s_to_" + str(tstamp+time_break_interval) + 's_.png')
					plt.clf()
				except (IndexError, NotImplementedError) as e:
					f = open("obs.flagged", "a")
					f.write(obs + "/" + subd + "/" + file + "\n")
					f.close()

		f = open(f_dir + "/data.written", "w")
		f.close()
