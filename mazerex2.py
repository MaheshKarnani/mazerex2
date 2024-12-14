#Mazerex2 prototype, one unit qwiic
#2024Dec
#02
from __future__ import print_function
import serial
import time
from gpiozero import DigitalInputDevice, DigitalOutputDevice
import os
import pandas as pd
import statistics as stats
import sys
from datetime import datetime
import numpy as np
import qwiic_rfid
import PyNAU7802
import smbus2
import qwiic_tca9548a
# GPIOZERO_PIN_FACTORY=native python3

savepath="/home/pi/Documents/Data/"
#Choose "Animal" or "Test" below
#trial_type = "Test"
trial_type = "Animal"
print(trial_type)
if trial_type == "Test":
    subjects = ["335490249236"]
if trial_type == "Animal":  
    subjects = ["94331472" ,"x", "y"] #out of study,  ""

#general variables
scale_cal=13289366.883 #use a calibration code and 20g weight to find out
weighing_time=1000 #duration of weight aqcuisition in ms

#food module
food = DigitalOutputDevice(24)
eat = DigitalInputDevice(23)

#puff module
puff=DigitalOutputDevice(18)

#mux board
print("\nInitialize SparkFun TCA9548A\n")
muxboard = qwiic_tca9548a.QwiicTCA9548A()
if muxboard.is_connected() == False:
    print("The Qwiic TCA9548A device isn't connected to the system. Please check your connection", \
        file=sys.stderr)
muxboard.list_channels()
time.sleep(0.5)
muxboard.enable_channels([0,1,2])
muxboard.list_channels()
time.sleep(2)
	
#RFID
def scan_tag():
    my_RFID = qwiic_rfid.QwiicRFID(0x5B)
    if my_RFID.begin() == False:
        print("\nThe Qwiic RFID Reader isn't connected to the system. Please check your connection", file=sys.stderr)
        return
    tag = my_RFID.get_tag()
#     scan_time = my_RFID.get_prec_req_time()
    return tag
def clear_scanner():
    my_RFID = qwiic_rfid.QwiicRFID(0x5B)
    if my_RFID.begin() == False:
        print("\nThe Qwiic RFID Reader isn't connected to the system. Please check your connection", file=sys.stderr)
        return
    my_RFID.clear_tags()


#init scale
# Create the bus
bus = smbus2.SMBus(1)
# Create the scale and initialize it.. hardware defined address is 0x2A. mux required for multiple
scale = PyNAU7802.NAU7802()
if scale.begin(bus):
    print("Scale connected!\n")
else:
    print("Can't find the scale, exiting ...\n")
    exit()
# Calculate the zero offset
print("Calculating scale zero offset...")
scale.calculateZeroOffset()
print("The zero offset is : {0}\n".format(scale.getZeroOffset()))
# print("Put a known mass on the scale.")
# cal = float(input("Mass in kg? "))
# Calculate the calibration factor
# print("Calculating the calibration factor...")
# scale.calculateCalibrationFactor(cal)
# print("The calibration factor is : {0:0.3f}\n".format(scale.getCalibrationFactor()))
scale.setCalibrationFactor(scale_cal) #20g 12843262.500 30g 12902791.667 20g 12993162.500

#init flags and timers
food_flag=False
puff_flag=False
puff_timer=int(round(time.time()*1000))
        
class SaveData:
    def append_weight(self,m,w,animaltag):

        weight_list = {
        "m": [],
        "w": [],
        "Date_Time": []
        }
        weight_list.update({'m': [m]})
        weight_list.update({'w': [w]})
        weight_list.update({'Date_Time': [datetime.now()]})
        
        df_w = pd.DataFrame(weight_list)
        #print(df_w)
        animaltag=str(animaltag)
        if not os.path.isfile(savepath + animaltag + "_weight.csv"):
            df_w.to_csv(savepath + animaltag + "_weight.csv", encoding="utf-8-sig", index=False)
            #print("File created sucessfully")
        else:
            df_w.to_csv(savepath + animaltag + "_weight.csv", mode="a+", header=False, encoding="utf-8-sig", index=False)
            #print("File appended sucessfully")
        
    def append_event(self,amount_consumed,latency_to_consumption,event_type,animaltag):
        """
        Function used to save event parameters to a .csv file
        example use save.append_event("", "", "initialize", animaltag)
        """
        global event_list

        event_list = {
            "Date_Time": [],
            "amount_consumed": [],
            "latency_to_consumption": [],
            "Type" : [],   
        }
        amount_consumed=str(amount_consumed)
        latency_to_consumption=str(latency_to_consumption)
        
        event_list.update({'amount_consumed': [amount_consumed]})
        event_list.update({'latency_to_consumption': [latency_to_consumption]})
        event_list.update({'Type': [event_type]})
        event_list.update({'Date_Time': [datetime.now()]})

        df_e = pd.DataFrame(event_list)
        animaltag=str(animaltag)
        if not os.path.isfile(savepath + animaltag + "_events.csv"):
            df_e.to_csv(savepath + animaltag + "_events.csv", encoding="utf-8-sig", index=False)
        else:
            df_e.to_csv(savepath + animaltag + "_events.csv", mode="a+", header=False, encoding="utf-8-sig", index=False)

#initialize
print("init check")   
print('eat pin')
print(eat.value)
print('dispensing food')
food.on()
time.sleep(0.05)
food.off()
puff.off()
time.sleep(0.05)
puff.on()
input('dispensed food - check hopper and press enter')

save = SaveData()
for x in range(np.size(subjects)):
    animaltag=subjects[x]
    save.append_event("", "", "initialize", animaltag)
mode=0
generic_timer=int(round(time.time()*1000))
animaltag=0

#execution loop    
while True:
    #command loop records feeding and logs weights and tags; coupling to airpuff hardwired
    millis = int(round(time.time() * 1000))
    if eat.value==1:
        puff.off() #inverted
        puff_flag=True
        puff_timer=int(round(time.time()*1000))
        save.append_event("", "", "eat", animaltag)
        food_flag=True
        print("eat")
        food.on()
        TTL_timer=int(round(time.time()*1000))
        if millis-TTL_timer>500 and food_flag:
            food.off()
            food_flag=False
    if millis-puff_timer>800 and puff_flag:
        puff.on()
        puff_flag=False
            
    if mode==0: #reset variables, wait for animal
        w=int(10)
        tag=0
        mode=1
        
    if mode==1: #scan tube
        m=[] #mass measurement points
        if millis-generic_timer>500:
            generic_timer=int(round(time.time()*1000))
            n=scale.getWeight() * 1000
            print("Mass {0:0.3f} g".format(n))
            tag=int(scan_tag())
            if tag>999:
                animaltag=tag
                mode=2
                weight_aqcuisition_timer=int(round(time.time()*1000))
                m.append(n)
                    
    if mode==2: #measure weight    
        while int(round(time.time() * 1000))-weight_aqcuisition_timer<weighing_time:
            n=scale.getWeight() * 1000
            m.append(n)
        w=stats.mean(m)
        print(tag)
        print(w)
        print(m)
        save.append_weight(w,m,animaltag)                               
        mode=0
        w=int(10)

#     
#     #troubleshoot loop time
# #     print(millis)
