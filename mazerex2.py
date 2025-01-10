import qwiic_tca9548a
import PyNAU7802
import smbus2
import time
from datetime import datetime, date
import pandas as pd
import os
import json
import requests
import qwiic_rfid
import sys
from gpiozero import DigitalInputDevice, DigitalOutputDevice

#Initialization routine
mode=1 #experiment mode 1=bsl, 2=induction, 3=post
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
def initialize_scales(mux):
    scales = []
    bus = create_bus()
    ports = [0, 1, 2, 3, 4, 5, 6, 7]
    for port in ports:
        enable_port(mux, port)
        nau = PyNAU7802.NAU7802()
        if not nau.begin(bus):
            # print(f"NOT CONNECTED TO SCALE: {port} \n")
            disable_port(mux, port)
            continue
        print(f"Connected to port: {port} with mux: {mux.address} \n")
        scales.append({
            "port": port,
            "nau": nau
        })
        disable_port(mux, port)
    print(f"scales initialised: {scales} with mux: {mux.address} \n")
    return scales

# 
# def get_calibration_data_file_name(mux):
#     return "tare_mux_" + str(mux["instance"].address) + ".json"

def get_reading(mux,port):
    scales = []
    bus = create_bus()
    port = port
    enable_port(mux, port)
    nau = PyNAU7802.NAU7802()
    if not nau.begin(bus):
        # print(f"NOT CONNECTED TO SCALE: {port} \n")
        disable_port(mux, port)
    weight=nau.getWeight() * 1000
    print("Mass {0:0.3f} g".format(weight))
    disable_port(mux, port)
    return weight
def scan_tag1(mux,port):
    antennas = []
    bus = create_bus()
    port = port
    enable_port(mux, port)
    my_RFID1 = qwiic_rfid.QwiicRFID(0x7D)
    if not my_RFID1.begin():
        # print(f"NOT CONNECTED TO : {port} \n")
        disable_port(mux, port)
    tag1 = my_RFID1.get_tag()
#     scan_time = my_RFID.get_prec_req_time()
    disable_port(mux, port)
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
    return tag2
def scan_tag3(mux,port):
    antennas = []
    bus = create_bus()
    port = port
    enable_port(mux, port)
    my_RFID3 = qwiic_rfid.QwiicRFID(0x1A)
    if not my_RFID3.begin():
        # print(f"NOT CONNECTED TO : {port} \n")
        disable_port(mux, port)
    tag3 = my_RFID3.get_tag()
#     scan_time = my_RFID.get_prec_req_time()
    disable_port(mux, port)
    return tag3
def scan_tag4(mux,port):
    antennas = []
    bus = create_bus()
    port = port
    enable_port(mux, port)
    my_RFID4 = qwiic_rfid.QwiicRFID(0x2B)
    if not my_RFID4.begin():
        # print(f"NOT CONNECTED TO : {port} \n")
        disable_port(mux, port)
    tag4 = my_RFID4.get_tag()
#     scan_time = my_RFID.get_prec_req_time()
    disable_port(mux, port)
    return tag4

mux = create_instance()

for i, val in enumerate(mux):
    print(i)
    mux[i]["scales"] = initialize_scales(mux[i]["instance"])
    get_reading(mux[i]["instance"],1)
get_reading(mux[0]["instance"],1)
get_reading(mux[0]["instance"],3)
get_reading(mux[0]["instance"],4)
get_reading(mux[0]["instance"],6)

tag1=int(scan_tag1(mux[0]["instance"],0))
tag2=int(scan_tag2(mux[0]["instance"],2))
tag3=int(scan_tag3(mux[0]["instance"],7))
tag4=int(scan_tag4(mux[0]["instance"],5))
print(tag1)
print(tag2)
print(tag3)
print(tag4)

#setup counter channel for FED3 pellets
pel1=0
eat1=DigitalInputDevice(17)
def count_pel1():
    global pel1
    pel1+=1
pel2=0
eat2=DigitalInputDevice(27)
def count_pel2():
    global pel2
    pel2+=1
pel3=0
eat3=DigitalInputDevice(23)
def count_pel3():
    global pel3
    pel3+=1
pel4=0
eat4=DigitalInputDevice(24)
def count_pel4():
    global pel4
    pel4+=1

#RFID interrupts as detectors GPIO cluster 16 19 20 26
detect1 = DigitalInputDevice(16) 

detect2 = DigitalInputDevice(21)

animal1=tag1
animal2=tag2


savepath="/home/pi/Documents/Data/"
#Choose "Animal" or "Test" below
#trial_type = "Test"
trial_type = "Animal"
print(trial_type)
if trial_type == "Test":
    subjects = ["335490249236","x", "y"]
if trial_type == "Animal":  
    subjects = ["19644194143" ,"19644194143", "19644194143"] #out of study,  ""

event_list1 = {
    "Mode" : [], 
    "Start_Time": [],
    "Animal": [],
    "Weight": [],
    "Unit":1,
    "Pellets" : [],   
}
event_list1.update({'Mode': ["initialize"]})
event_list1.update({'Start_Time': [datetime.now()]})
event_list1.update({'Pellets': [pel1]})
event_list1.update({'Animal': [0]})
weight1=int(get_reading(mux[0]["instance"],1)) #changed from no int, and just get_reading - so check for errors!
event_list1.update({'Weight': [weight1]})

class SaveData:
    def append_event(self,event_list1):
        """
        Function used to save event parameters to a .csv file
        example use save.append_event("", "", "initialize", animaltag)
        """
#         global event_list1
        
        df_e = pd.DataFrame(event_list1)
        datetag=str(date.today())
        if not os.path.isfile(savepath + datetag + "_events.csv"):
            df_e.to_csv(savepath + datetag + "_events.csv", encoding="utf-8-sig", index=False)
        else:
            df_e.to_csv(savepath + datetag + "_events.csv", mode="a+", header=False, encoding="utf-8-sig", index=False)

save = SaveData()
save.append_event(event_list1)
event_list1.update({'Mode': [mode]})

# Experiment loop
while True:
    eat1.when_activated=count_pel1
    eat2.when_activated=count_pel2
    eat3.when_activated=count_pel3
    eat4.when_activated=count_pel4
    
    if detect1.value == 0:
        print("unit1")
        tag1=int(scan_tag1(mux[0]["instance"],0))
        event_list1.update({'Pellets': [pel1]})
        save.append_event(event_list1)
        pel1=0
        event_list1.update({'Start_Time': [datetime.now()]})
        event_list1.update({'Animal': [tag1]})
        weight1=int(get_reading(mux[0]["instance"],1)) #changed from no int, and just get_reading - so check for errors!
        event_list1.update({'Weight': [weight1]})
    
          