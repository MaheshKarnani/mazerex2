import qwiic_tca9548a
import PyNAU7802
import smbus2
import serial
import time as tim
from datetime import datetime, date, timedelta, time
import pandas as pd
import numpy as np
import os
import json
import requests
import qwiic_rfid
import sys
from gpiozero import DigitalInputDevice, DigitalOutputDevice
from github import Github, InputGitTreeElement
import keyboard
import statistics
#create standard experiment timeline for mazerex54 onwards
time_line=list()
savepath="/home/pi/Documents/Data/"
try:
    previous_TimeLine_file=savepath + "TimeLine.csv"
    previous_time_line = np.array(pd.read_csv(previous_TimeLine_file, header=None))
    print(previous_time_line)
    user_input=input('Above time line was stored in your Data folder. \nDo you want overwrite? Y/N')
    if user_input.lower() in ["yes", "y"]:
        print("Continuing...")
    else:
        sys.exit("Exiting...")
except:
    print('there is no previous time line in your datafolder \nproceeding without overwrite')

print('STANDARD: 7d habituation, 2d baseline, 3d 50:50, 3d post1, 3d 50:50, 5d post2')
user_input=input('Start 7d habituation today? y/n')
if user_input.lower() in ["yes", "y"]:
    print("Making schedule...")
    start=date.today()
    bsl=datetime.combine(start+timedelta(days=7),time(hour=12))
else:
    hab_days=input('How many days of habituation from today?')
    print("Making non-standard schedule...")
    start=date.today()
    bsl=datetime.combine(start+timedelta(days=int(hab_days)),time(hour=12))
print('baseline start:',bsl)
ind=bsl+timedelta(days=2)
print('induction1 start:',ind)
post1=ind+timedelta(days=3)
print('post1 start:',post1)
ind2=post1+timedelta(days=3)
print('induction2 start:',ind2)
post2=ind2+timedelta(days=3)
print('post2 start:',post2)
print('experiment end:',post2+timedelta(days=5))

time_line=[start,bsl,ind,post1,ind2,post2]
df = pd.DataFrame(time_line)
df.to_csv(savepath + "/TimeLine.csv", header=False, encoding="utf-8-sig", index=False)
print('done')