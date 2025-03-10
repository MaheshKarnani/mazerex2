import qwiic_tca9548a
import PyNAU7802
import smbus2
import time
from datetime import datetime, date, timedelta
import pandas as pd
import os
import json
import requests
import qwiic_rfid
import sys
from gpiozero import DigitalInputDevice, DigitalOutputDevice
from github import Github, InputGitTreeElement
import keyboard

#Initialization routine
mode=1 #experiment mode 0=habituation, 1=bsl, 2=induction, 3=post, 4=induction_repeat, 5=post_repeat
#load scale calibration files
scale_cal_filepath="/home/pi/Documents/Data/ScaleCal.json"
scale_tare_filepath="/home/pi/Documents/Data/ScaleTare.json"
with open(scale_cal_filepath, 'r') as file:
    scale_cal=json.load(file)
with open(scale_tare_filepath, 'r') as file:
    scale_tare=json.load(file)
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
def get_reading(mux,port):
    global scale_cal
    scales = []
    bus = create_bus()
    port = port
    enable_port(mux, port)
    nau = PyNAU7802.NAU7802()
    if not nau.begin(bus):
        # print(f"NOT CONNECTED TO SCALE: {port} \n")
        disable_port(mux, port)
    nau.setCalibrationFactor(scale_cal[port])
    nau.setZeroOffset(scale_tare[port])
    weight=nau.getWeight() * 1000
    print("Mass {0:0.3f} g".format(weight))
    disable_port(mux, port)
    bus.close()
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
    my_RFID3 = qwiic_rfid.QwiicRFID(0x2B)
    if not my_RFID3.begin():
        # print(f"NOT CONNECTED TO : {port} \n")
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
    my_RFID4 = qwiic_rfid.QwiicRFID(0x1A)
    if not my_RFID4.begin():
        # print(f"NOT CONNECTED TO : {port} \n")
        disable_port(mux, port)
    tag4 = my_RFID4.get_tag()
#     scan_time = my_RFID.get_prec_req_time()
    disable_port(mux, port)
    bus.close()
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
tag3=int(scan_tag3(mux[0]["instance"],5))
tag4=int(scan_tag4(mux[0]["instance"],7))
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

feed1=DigitalOutputDevice(5)
feed2=DigitalOutputDevice(13)
feed3=DigitalOutputDevice(6)
feed4=DigitalOutputDevice(12)
feed1.on()
feed2.on()
feed3.on()
feed4.on()
#RFID interrupts as detectors GPIO cluster 16 19 20 26
unit1=False


detect1 = DigitalInputDevice(16)
def flag_unit1():
    global unit1
    unit1=True
    print(unit1)
detect2 = DigitalInputDevice(20, pull_up=False)
detect3 = DigitalInputDevice(19) 
detect4 = DigitalInputDevice(26)

animal1=tag1
animal2=tag2
animal3=tag3
animal4=tag4

savepath="/home/pi/Documents/Data/"

event_list1 = {
    "Mode" : ["initialize"], 
    "Start_Time": [datetime.now()],
    "Animal": [0],
    "Weight": [round(float(get_reading(mux[0]["instance"],1)),2)],
    "Unit":1,
    "Pellets" : [pel1],   
}
# event_list1.update({'Mode': ["initialize"]})
# event_list1.update({'Start_Time': [datetime.now()]})
# event_list1.update({'Pellets': [pel1]})
# event_list1.update({'Animal': [0]})
# weight1=int(get_reading(mux[0]["instance"],1)) #changed from no int, and just get_reading - so check for errors!
# event_list1.update({'Weight': [weight1]})
event_list2 = {
    "Mode" : ["initialize"], 
    "Start_Time": [datetime.now()],
    "Animal": [0],
    "Weight": [round(float(get_reading(mux[0]["instance"],3)),2)],
    "Unit":2,
    "Pellets" : [pel2],   
}
event_list3 = {
    "Mode" : ["initialize"], 
    "Start_Time": [datetime.now()],
    "Animal": [0],
    "Weight": [round(float(get_reading(mux[0]["instance"],4)),2)],
    "Unit":3,
    "Pellets" : [pel3],   
}
event_list4 = {
    "Mode" : ["initialize"], 
    "Start_Time": [datetime.now()],
    "Animal": [0],
    "Weight": [round(float(get_reading(mux[0]["instance"],6)),2)],
    "Unit":4,
    "Pellets" : [pel4],   
}

class SaveData:
    def append_event(self,event_list):
        df_e = pd.DataFrame(event_list)
        datetag=str(date.today())
        if not os.path.isfile(savepath + datetag + "_events.csv"):
            df_e.to_csv(savepath + datetag + "_events.csv", encoding="utf-8-sig", index=False)
        else:
            df_e.to_csv(savepath + datetag + "_events.csv", mode="a+", header=False, encoding="utf-8-sig", index=False)

save = SaveData()
save.append_event(event_list1)
save.append_event(event_list2)
save.append_event(event_list3)
save.append_event(event_list4)
event_list1.update({'Mode': [mode]})
event_list2.update({'Mode': [mode]})
event_list3.update({'Mode': [mode]})
event_list4.update({'Mode': [mode]})
upload_time=datetime.now()
upload_interval=timedelta(hours=6) #minimum interval between uploads, hours suggested
action_time=datetime.now()
action_interval=timedelta(minutes=15) #safe interval from last detection to start upload, 15 min suggested
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
        weight1=round(float(get_reading(mux[0]["instance"],1)),2) 
        event_list1.update({'Weight': [weight1]})
        action_time=datetime.now()
        unit_flag1=False
        
    if detect2.value == 0:
        print("unit2")
        tag2=int(scan_tag2(mux[0]["instance"],2))
        event_list2.update({'Pellets': [pel2]})
        save.append_event(event_list2)
        pel2=0
        event_list2.update({'Start_Time': [datetime.now()]})
        event_list2.update({'Animal': [tag2]})
        weight2=round(float(get_reading(mux[0]["instance"],3)),2)
        event_list2.update({'Weight': [weight2]})
        action_time=datetime.now()
    if detect3.value == 0:
        print("unit3")
        tag3=int(scan_tag3(mux[0]["instance"],5))
        event_list3.update({'Pellets': [pel3]})
        save.append_event(event_list3)
        pel3=0
        event_list3.update({'Start_Time': [datetime.now()]})
        event_list3.update({'Animal': [tag3]})
        weight3=round(float(get_reading(mux[0]["instance"],4)),2) 
        event_list3.update({'Weight': [weight3]})
        action_time=datetime.now()
    if detect4.value == 0:
        print("unit4")
        tag4=int(scan_tag4(mux[0]["instance"],7))
        event_list4.update({'Pellets': [pel4]})
        save.append_event(event_list4)
        pel4=0
        event_list4.update({'Start_Time': [datetime.now()]})
        event_list4.update({'Animal': [tag4]})
        weight4=round(float(get_reading(mux[0]["instance"],6)),2) 
        event_list4.update({'Weight': [weight4]}) 
        action_time=datetime.now()
        
    # force data collection and upload when user presses c
    if keyboard.is_pressed('c'):
        try:
            event_list1.update({'Pellets': [pel1]})
            save.append_event(event_list1)
            pel1=0
            event_list2.update({'Pellets': [pel2]})
            save.append_event(event_list2)
            pel2=0
            event_list3.update({'Pellets': [pel3]})
            save.append_event(event_list3)
            pel3=0
            event_list4.update({'Pellets': [pel4]})
            save.append_event(event_list4)
            pel4=0
            print("last entries saved from all units")
        except:
            print("no new data in units")        
        upload_time=datetime.now()-upload_interval
        action_time=datetime.now()-action_interval
    time_since_upload=datetime.now()-upload_time
    time_since_action=datetime.now()-action_time
    
    if time_since_upload>upload_interval:
        if time_since_action>action_interval:
            try:
                #deposit weight data to public repository
                print("Commencing upload. Stand by.")
                upload_time=datetime.now()
                g = Github("token")
                repo = g.get_user().get_repo('mazerex2') # repo name
                file_list=list()
                file_names=list()
                datetag=str(date.today())
                file_list.append(savepath + datetag + "_events.csv")
                file_names.append("fem2_RIctrl/" + datetag + "_events.csv")
                datetag=str(date.today()-timedelta(days = 1))
                file_list.append(savepath + datetag + "_events.csv")
                file_names.append("fem2_RIctrl/" + datetag + "_events.csv")
                commit_message = 'automated upload from rig1'
                master_ref = repo.get_git_ref('heads/main')
                master_sha = master_ref.object.sha
                base_tree = repo.get_git_tree(master_sha)
                element_list = list()
                for i, entry in enumerate(file_list):
                    with open(entry) as input_file:
                        data = input_file.read()
                    element = InputGitTreeElement(file_names[i], '100644', 'blob', data)
                    element_list.append(element)
                tree = repo.create_git_tree(element_list, base_tree)
                parent = repo.get_git_commit(master_sha)
                commit = repo.create_git_commit(commit_message, tree, [parent])
                master_ref.edit(commit.sha)
                print("database updated")
            except:
                print("database update failed")
