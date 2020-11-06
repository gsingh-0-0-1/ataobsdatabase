print("Importing libraries...")

import numpy as np
from blimpy import Waterfall
import matplotlib.pyplot as plt
from blimpy.io.fil_reader import FilReader
import os
import sys
from PIL import Image

sampling_time = 0.01515151515

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
print("Enter the subfolder for the database: ")
database_dir = input("Leave blank to autoset to obs_database/ : ")
if database_dir == '':
	database_dir = "obs_database/"

print("Scanning parent directory...")

obs_list = [f.path.split("/")[-1] for f in os.scandir(parent_stem + obs_dir) if f.is_dir()]

print("Initializing database directory...")

if os.path.isdir(parent_stem + database_dir):
	pass
else:
	os.mkdir(parent_stem + database_dir)

print("Scanning observation directories...")

#here's where most of the processing occurs
for obs in obs_list:
	#check/conditionally make directories for each obs
	if os.path.isdir(parent_stem + database_dir + obs): 
		pass
	else: 
		os.mkdir(parent_stem + database_dir + obs)

	#get files in the obs dir
	this_obs_subdir = [f.path.split("/")[-1] for f in os.scandir(parent_stem + obs_dir + obs) if f.is_dir()]

	print(obs)

	#get sub-directories inside the obs dir
	for subd in this_obs_subdir:

		f_dir = parent_stem + database_dir + obs + "/" + subd

		obs_f_dir = parent_stem + obs_dir + obs + "/" + subd

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

		if os.path.isdir(f_dir): 
			if "data.written" in os.listdir(parent_stem + database_dir + obs + "/" + subd):
				continue
			else:
				pass
		else: 
			os.mkdir(f_dir)

		print("\t|" + subd)

		#get a list of .fil files inside each sub-directory inside each obs dir
		file_list = [f.path.split("/")[-1] for f in os.scandir(obs_f_dir) if (".fil" in f.path)]

		if "ics" not in subd:
			#extract obs info from the header
			header = open(obs_f_dir + "/obs.header")
			header = header.read().split("\n")
			obs_time_raw = [line for line in header if "TSAMP" in line][0]
			obs_time = ''

			for ch in obs_time_raw:
				if ch.isdigit() or ch == '.':
					obs_time += ch

			print("\t\t|OBS TIME: " + obs_time + "s")


		for file in file_list:

			time_break_interval = 60

			print("\t\t|" + file)

			#get the sampling time
			f = Waterfall(obs_f_dir + "/" + file, t_start=0, t_stop=1)

			sampling_time = f.header['tsamp']

			if "ics" in file:
				fsize = os.path.getsize(obs_f_dir + "/" + file) - sys.getsizeof(f.header)
				samples = round(fsize / (f.header['nchans'] * (f.header['nbits'] / 8)))
				obs_time = samples * sampling_time
				time_break_interval = 60

			for tstamp in range(0, int(float(obs_time)), time_break_interval):
				start = int(tstamp/sampling_time)
				stop = int((tstamp + time_break_interval)/sampling_time)

				f = Waterfall(obs_f_dir + "/" + file, t_start=start, t_stop=stop)

				f.plot_waterfall(logged=False)

				#modify the yticks appropriately
				plt.yticks(np.arange(0, time_break_interval, 5), np.arange(0, time_break_interval, 5) + tstamp)

				plt.savefig(f_dir + "/" + file + '_waterfall_' + str(tstamp) + "s_to_" + str(tstamp+time_break_interval) + 's_.png')
				plt.clf()


				#plot the spectrum
				f.plot_spectrum()

				plt.savefig(f_dir + "/" + file + '_spectrum_' + str(tstamp) + "s_to_" + str(tstamp+time_break_interval) + 's_.png')
				plt.clf()


				#plot the timeseries
				f.plot_time_series()

				#modify the xticks appropriately
				plt.xticks(np.arange(0, time_break_interval, 5), np.arange(0, time_break_interval, 5) + tstamp)

				plt.savefig(f_dir + "/" + file + '_timeseries_' + str(tstamp) + "s_to_" + str(tstamp+time_break_interval) + 's_.png')
				plt.clf()

		f = open(f_dir + "/data.written", "w")
		f.close()
