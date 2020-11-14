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

obs_dir = input("Enter the folder in which the observations are stored: ")

print()
database_dir = input("Enter the folder for the database: ")

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

f = open("arfiles.listing", "wb")

find_ar = subprocess.run(["find", obs_dir, "-type", "f", "-name", "*.ar"], stdout=subprocess.PIPE)

f.write(find_ar.stdout)
f.close()

f = open("arfiles.listing", "r")
arfile_list = f.read().split("\n")
f.close()

#subprocess.run(['source', '/home/obsuser/.bashrc'])

subprocess.Popen(["source", "/home/obsuser/.bashrc"], shell=True)

for arfile in arfile_list:
    thisfile_p_dir = "/".join(arfile.split("/")[:-1])
    print(thisfile_p_dir)
    if not os.path.isdir(thisfile_p_dir.replace(obs_dir, database_dir)):
        os.makedirs(thisfile_p_dir.replace(obs_dir, database_dir), exist_ok=True)

    if (1==1):
        antennalist = ['1a', '1c', '1f', '1k', '2a', '2h', '4g', '4j', '5c']
        obsdir = "/".join(thisfile_p_dir.split("/")[:-1])
        print(obsdir)
        for antenna in antennalist:
            try:
                f = open(obsdir + "/" + antenna + "/obs.header")
                f = f.read()
                break
            except FileNotFoundError:
                pass

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

        obs = date + "-" + time


    if "ar_sql.written" not in os.listdir(thisfile_p_dir.replace(obs_dir, database_dir)):
        command = '''insert ignore into pulsar_obs_details (obs_name, source, date, time) values
        ("''' + obs + '''", "''' + source + '''", "''' + date + '''", "''' + time + '''")'''

        cnx = mysql.connector.connect(user=sys.argv[2], password=sys.argv[3], host='127.0.0.1', database='obs_info')

        cnx.cursor().execute(command)
        cnx.commit()
        cnx.close()

        f = open(thisfile_p_dir.replace(obs_dir, database_dir) + "/ar_sql.written", "w")
        f.close()

    if "ar.processed" not in os.listdir(thisfile_p_dir.replace(obs_dir, database_dir)):

        subfolder = thisfile_p_dir.split("/")[-1]

        print(arfile)

        savepath = thisfile_p_dir.replace(obs_dir, database_dir).replace(subfolder, 'ar_images')

        if not os.path.isdir(savepath):
            os.mkdir(savepath)

        subprocess.run(['psrplot', '-pfreq+', '-jDT', '-D' + savepath + '/' + obs + '_' + subfolder + '.ar.png/png', arfile], stdout=sys.stdout)

        #img = Image.open(savepath + "/" + obs + "_" + subfolder + ".ar.png")

        #img = img.resize((int(img.size[0]/2), int(img.size[1]/2)))

        #img.save(savepath + "/" + obs + "_" + subfolder + ".ar.png")

        f = open(thisfile_p_dir.replace(obs_dir, database_dir) + "/ar.processed", "w")
        f.close()
