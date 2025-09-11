#initialize sensors etc.
import qwiic_rfid
import serial
import time as tim
import sys
from gpiozero import DigitalInputDevice, DigitalOutputDevice
from datetime import datetime, date, timedelta, time
import pandas as pd
import os
import qwiic_tca9548a
import PyNAU7802
import smbus2
import json
import requests
from github import Github, InputGitTreeElement
import keyboard

interval=timedelta(seconds=60)

#Initialization routine
state1=0 #0=start, 1=one detected, 2=two detected, >2=dominance testing
state2=0
state3=0
state4=0
#initialize qwiic hardware
def enable_port(mux: qwiic_tca9548a.QwiicTCA9548A, port):
    mux.enable_channels(port)
def disable_port(mux: qwiic_tca9548a.QwiicTCA9548A, port):
    mux.disable_channels(port)
def initialize_mux(address):
    mux = qwiic_tca9548a.QwiicTCA9548A(address=address)
    return mux
def create_instance():
    mux = []
    addresses = [*range(0x70, 0x77 + 1)]
    for address in addresses:
        instance = initialize_mux(address)
        if not instance.is_connected():
            continue
        print("Connected to mux {0} \n".format(address))
        instance.disable_all()
        mux.append({
            "instance": instance,
            "scales": [],
        })
    return mux
def create_bus():
    bus = smbus2.SMBus(1)
    return bus
def scan_tag1(mux,port):
    antennas = []
    bus = create_bus()
    port = port
    enable_port(mux, port)
    my_RFID1 = qwiic_rfid.QwiicRFID(0x13)
    if not my_RFID1.begin():
        # print(f"NOT CONNECTED TO : {port} \n")
        disable_port(mux, port)
    tag1 = my_RFID1.get_tag()
#     scan_time = my_RFID.get_prec_req_time()
    disable_port(mux, port)
    bus.close()
    return tag1
def scan_tag2(mux,port):
    antennas = []
    bus = create_bus()
    port = port
    enable_port(mux, port)
    my_RFID2 = qwiic_rfid.QwiicRFID(0x12)
    if not my_RFID2.begin():
        # print(f"NOT CONNECTED TO : {port} \n")
        disable_port(mux, port)
    tag2 = my_RFID2.get_tag()
#     scan_time = my_RFID.get_prec_req_time()
    disable_port(mux, port)
    bus.close()
    return tag2
def scan_tag3(mux,port):
    antennas = []
    bus = create_bus()
    port = port
    enable_port(mux, port)
    my_RFID3 = qwiic_rfid.QwiicRFID(0x13)
    if not my_RFID3.begin():
        print(f"NOT CONNECTED TO : {port} \n")
        disable_port(mux, port)
    tag3 = my_RFID3.get_tag()
#     scan_time = my_RFID.get_prec_req_time()
    disable_port(mux, port)
    bus.close()
    return tag3
def scan_tag4(mux,port):
    antennas = []
    bus = create_bus()
    port = port
    enable_port(mux, port)
    my_RFID4 = qwiic_rfid.QwiicRFID(0x12)
    if not my_RFID4.begin():
        print(f"NOT CONNECTED TO : {port} \n")
        disable_port(mux, port)
    tag4 = my_RFID4.get_tag()
#     scan_time = my_RFID.get_prec_req_time()
    disable_port(mux, port)
    bus.close()
    return tag4

mux = create_instance()

for i, val in enumerate(mux):
    print(i)
#     mux[i]["scales"] = initialize_scales(mux[i]["instance"])
#     get_reading(mux[i]["instance"],3)
# get_reading(mux[0]["instance"],3)

tag1=int(scan_tag1(mux[0]["instance"],0))
tag2=int(scan_tag2(mux[0]["instance"],1))
tag3=int(scan_tag3(mux[0]["instance"],2))
tag4=int(scan_tag4(mux[0]["instance"],3))
print(tag1)
print(tag2)
print(tag3)
print(tag4)

#RFID detection interrupts
RFID1_detect = DigitalInputDevice(21)
RFID2_detect = DigitalInputDevice(20, pull_up=False)
RFID3_detect = DigitalInputDevice(16) 
RFID4_detect = DigitalInputDevice(12)

beam1_detect = DigitalInputDevice(17)
beam2_detect = DigitalInputDevice(26)

  #serial to arduino
ser = serial.Serial('/dev/ttyUSB0', 9600)
tim.sleep(2)

tag1=0 #initialize animal
tag2=0
tag3=0 #initialize animal
tag4=0
known_tags=[19647231169,1111110210210,
1111111120121,
11111112223,
1111111168169,
1111110189189,
1111111140141,
1111111117116,
1111111170171,
11111112120]

#saving and uploading
savepath="/home/flan2/Documents/Data/"
event_list1 = {
    "Mode" : ["initialize"], 
    "Start_Time": [datetime.now()],
    "Animal": [tag1],
    "Unit":1,
}

event_list2 = {
    "Mode" : ["initialize"], 
    "Start_Time": [datetime.now()],
    "Animal": [tag2],
    "Unit":2,
}
event_list3 = {
    "Mode" : ["initialize"], 
    "Start_Time": [datetime.now()],
    "Animal": [tag3],
    "Unit":3,
}

event_list4 = {
    "Mode" : ["initialize"], 
    "Start_Time": [datetime.now()],
    "Animal": [tag4],
    "Unit":4,
}

status_list = {
    "Mode" : ["initialize"], 
    "Start_Time": [datetime.now()],
    "Animal": [0],
    "Unit":0,
}

status_list2 = {
    "Mode" : ["initialize"], 
    "Start_Time": [datetime.now()],
    "Animal": [0],
    "Unit":5,
}

class SaveData:
    def append_event(self,event_list):
        df_e = pd.DataFrame(event_list)
        datetag=str(date.today())
        if not os.path.isfile(savepath + datetag + "_autolindz.csv"):
            df_e.to_csv(savepath + datetag + "_autolindz.csv", encoding="utf-8-sig", index=False)
        else:
            df_e.to_csv(savepath + datetag + "_autolindz.csv", mode="a+", header=False, encoding="utf-8-sig", index=False)

save = SaveData()
save.append_event(event_list1)
save.append_event(event_list2)
save.append_event(event_list3)
save.append_event(event_list4)
event_list1.update({'Mode': [state1]})
event_list2.update({'Mode': [state2]})
event_list3.update({'Mode': [state3]})
event_list4.update({'Mode': [state4]})
upload_time=datetime.now()
upload_interval=timedelta(hours=6) #minimum interval between uploads, hours suggested
action_time=datetime.now()
action_time2=datetime.now()
action_interval=timedelta(minutes=15) #safe interval from last detection to start upload, 15 min suggested
ser.write(str.encode('a'))
test_started=False
start_time=datetime.now()
ser.write(str.encode('d'))
test_started2=False
start_time2=datetime.now()

#experiment routine
while True:
    if RFID1_detect.value == 0:
        tag1=int(scan_tag1(mux[0]["instance"],0))
#         print(tag1)
        action_time=datetime.now()
        if tag1 in known_tags:
            ser.write(str.encode('b'))
            print("entry1")
            print(known_tags.index(tag1))
            event_list1.update({'Start_Time': [datetime.now()]})
            event_list1.update({'Animal': [tag1]})
            event_list1.update({'Mode': [state1]})
            event_list2.update({'Mode': [state2]})
            state1=state1+1
            save.append_event(event_list1)#for this animal
            
    if RFID2_detect.value == 0:
        tag2=int(scan_tag2(mux[0]["instance"],1))
        action_time=datetime.now()
        if tag2 in known_tags:
            ser.write(str.encode('c'))
            print("entry2")
            print(known_tags.index(tag2))
            event_list2.update({'Start_Time': [datetime.now()]})
            event_list2.update({'Animal': [tag2]})
            event_list1.update({'Mode': [state1]})
            event_list2.update({'Mode': [state2]})
            state2=state2+1
            save.append_event(event_list2)#for this animal
        
    if state1>0 and state2>0 and not test_started:
        if tag1==tag2:#animal passed through
            print('solo traversal')
            tag1=0
            tag2=1
            state1=0
            state2=0
            ser.write(str.encode('a'))
            status_list.update({'Start_Time': [datetime.now()]})
            status_list.update({'Mode': ["solo"]})
            save.append_event(status_list)
            
        else:#dominance test in progress
            print('dominance test in progress')
            start_time=datetime.now()
            test_started=True
            status_list.update({'Start_Time': [datetime.now()]})
            status_list.update({'Mode': ["start Lindzey"]})
            save.append_event(status_list)
    if test_started and start_time+interval<datetime.now():
        if beam1_detect.value==1:#unobstructed
            print('test has finished and tube empty')
            state1=0
            state2=0
            test_started=False
            ser.write(str.encode('a'))
            status_list.update({'Start_Time': [datetime.now()]})
            status_list.update({'Mode': ["End Lindzey"]})
            save.append_event(status_list)
        else:     
            print('dominance test still in progress')
            start_time=datetime.now()
    if action_time+interval<datetime.now() and (state1>0 or state2>0):
        if beam1_detect.value==1:#unobstructed
            print('tube empty --- resetting')
            tag1=0
            tag2=1
            state1=0
            state2=0
            test_started=False
            ser.write(str.encode('a'))
            status_list.update({'Start_Time': [datetime.now()]})
            status_list.update({'Mode': ["reset"]})
            save.append_event(status_list)

#second tube:

    if RFID3_detect.value == 0:
        tag3=int(scan_tag3(mux[0]["instance"],2))
        print(tag3)
        action_time2=datetime.now()
        if tag3 in known_tags:
            ser.write(str.encode('e'))
            print("entry3")
            print(known_tags.index(tag3))
            event_list3.update({'Start_Time': [datetime.now()]})
            event_list3.update({'Animal': [tag3]})
            event_list3.update({'Mode': [state3]})
            event_list4.update({'Mode': [state4]})
            state3=state3+1
            save.append_event(event_list3)#for this animal
            
    if RFID4_detect.value == 0:
        tag4=int(scan_tag4(mux[0]["instance"],3))
        action_time2=datetime.now()
        if tag4 in known_tags:
            ser.write(str.encode('f'))
            print("entry4")
            print(known_tags.index(tag4))
            event_list4.update({'Start_Time': [datetime.now()]})
            event_list4.update({'Animal': [tag4]})
            event_list3.update({'Mode': [state3]})
            event_list4.update({'Mode': [state4]})
            state4=state4+1
            save.append_event(event_list4)#for this animal
        
    if state3>0 and state4>0 and not test_started2:
        if tag3==tag4:#animal passed through
            print('solo traversal')
            tag3=0
            tag4=1
            state3=0
            state4=0
            ser.write(str.encode('d'))
            status_list2.update({'Start_Time': [datetime.now()]})
            status_list2.update({'Mode': ["solo2"]})
            save.append_event(status_list2)
            
        else:#dominance test in progress
            print('dominance test2 in progress')
            start_time2=datetime.now()
            test_started2=True
            status_list2.update({'Start_Time': [datetime.now()]})
            status_list2.update({'Mode': ["start Lindzey2"]})
            save.append_event(status_list2)
    if test_started2 and start_time2+interval<datetime.now():
        if beam2_detect.value==1:#unobstructed
            print('test2 has finished and tube2 empty')
            state3=0
            state4=0
            test_started2=False
            ser.write(str.encode('d'))
            status_list2.update({'Start_Time': [datetime.now()]})
            status_list2.update({'Mode': ["End Lindzey2"]})
            save.append_event(status_list2)
        else:     
            print('dominance test still in progress')
            start_time2=datetime.now()
    if action_time2+interval<datetime.now() and (state3>0 or state4>0):
        if beam2_detect.value==1:#unobstructed
            print('tube empty --- resetting2')
            tag3=0
            tag4=1
            state3=0
            state4=0
            test_started2=False
            ser.write(str.encode('d'))
            status_list2.update({'Start_Time': [datetime.now()]})
            status_list2.update({'Mode': ["reset2"]})
            save.append_event(status_list2)
