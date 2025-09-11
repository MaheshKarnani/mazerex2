import qwiic_tca9548a
import PyNAU7802
import smbus2
import time
from datetime import datetime, date, timedelta, time
import pandas as pd
import os
import json
import requests
import qwiic_rfid
import sys
from gpiozero import DigitalInputDevice, DigitalOutputDevice
from github import Github, InputGitTreeElement
import keyboard
import statistics
import numpy as np

#Initialization routine
mode=0 #experiment mode 0=habituation, 1=bsl, 2=induction, 3=post, 4=induction_repeat, 5=post_repeat
mode_switch=False
#Experiment plan
if date.today()>date(2025,8,29):
    mode=1 #bsl
if date.today()>date(2025,9,5):
    mode=2 #induction1
if date.today()>date(2025,9,9):
    mode=3 #post1
if date.today()>date(2025,9,12):
    mode=5 #post2
# if date.today()>date(2025,8,6):
#     mode=6 #bsl3
# if date.today()>date(2025,8,7):
#     mode=7 #ind3
# if date.today()>date(2025,8,11):
#     mode=8 #remind3
# if date.today()>date(2025,8,14):
#     mode=9 #post3
if (date.today()==date(2025,8,29) or
    date.today()==date(2025,9,5) or
    date.today()==date(2025,9,9)or
    date.today()==date(2025,9,12)):
#     date.today()==date(2025,8,7)or
#     date.today()==date(2025,8,11)or
#     date.today()==date(2025,8,14)):
#     date.today()==date(2025,4,17)):
    mode_switch=True # will trigger mode+1 at 12pm.
    switch_time=datetime.combine(date.today(),time(12,0))
    
authorize_puff=DigitalOutputDevice(21)
print("mode is")
print(mode)
if mode==2 or mode==4 or mode==7:
    authorize_puff.on()
    print("puffs authorized")
elif mode==3 or mode==8:
    authorize_puff.off()
    print("puffs on if weight gain")
else:
    authorize_puff.off()
    print("puffs OFF")
if mode_switch:
    print("switching modes today at")
    print(switch_time)

#individual data for reminder calculation
known_tags=[19647231169,
1111111120121,11111112223,1111111168169,1111110189189,
1111111140141,1111111117116,1111111170171,11111112120]
weight_history_file="/home/pi/Documents/Data/WeigthHistory.csv"
weight_history = np.array(pd.read_csv(weight_history_file))
print(weight_history)
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
    bus = smbus2.SMBus(1) #change to bus 0 and back to 1 to resolve IOerror.
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
    my_RFID1 = qwiic_rfid.QwiicRFID(0x12) #was13 
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
    my_RFID2 = qwiic_rfid.QwiicRFID(0x15) #was12
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
    my_RFID3 = qwiic_rfid.QwiicRFID(0x14)
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
    my_RFID4 = qwiic_rfid.QwiicRFID(0x13)#was15
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
    get_reading(mux[i]["instance"],4)
get_reading(mux[0]["instance"],4)
get_reading(mux[0]["instance"],6)
get_reading(mux[0]["instance"],3)
get_reading(mux[0]["instance"],1)

tag1=int(scan_tag1(mux[0]["instance"],5))
tag2=int(scan_tag2(mux[0]["instance"],7))
tag3=int(scan_tag3(mux[0]["instance"],2))
tag4=int(scan_tag4(mux[0]["instance"],0))
print(tag1)
print(tag2)
print(tag3)
print(tag4)

# reminder puff baseline gathering function
def update_weight_median(tag,weight):
    global weight_history #15rows of prev weights from 8columns of animals
    global known_tags
    an=known_tags.index(tag)
    if weight<1.2*statistics.median(weight_history[:,an]) and weight>0.8*statistics.median(weight_history[:,an]):
        weight_history[:,an]=[*weight_history[1:15,an],weight]#update
 
# reminder puff decision function
def check_weight_gain(tag,weight,unit):
    global weight_history #15rows of prev weights from 8columns of animals
    global known_tags
    an=known_tags.index(tag)
    print(weight_history[:,an])
    if weight>1.2*statistics.median(weight_history[:,an]) or weight<0.8*statistics.median(weight_history[:,an]):
        print('weight artefact')
    else:
        previous_weight=statistics.median(weight_history[0:10,an])
        weight_history[:,an]=[*weight_history[1:15,an],weight]#update
        current_weight=statistics.median(weight_history[8:15,an])
        print(current_weight,previous_weight,current_weight-previous_weight)
        if current_weight-previous_weight>0.2:
            if unit==1:
                puff1.on()
                event_list1.update({'Mode': [99]})
            if unit==2:
                puff2.on()
                event_list2.update({'Mode': [99]})
            if unit==3:
                puff3.on()
                event_list3.update({'Mode': [99]})
            if unit==4:
                puff4.on()
                event_list4.update({'Mode': [99]})

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

# feed1=DigitalOutputDevice(5)
# feed2=DigitalOutputDevice(13)
# feed3=DigitalOutputDevice(6)
# feed4=DigitalOutputDevice(12)
# feed1.on()
# feed2.on()
# feed3.on()
# feed4.on()
# puff controls for weight gain algorithm
puff1=DigitalOutputDevice(5)
puff2=DigitalOutputDevice(13)
puff3=DigitalOutputDevice(6)
puff4=DigitalOutputDevice(12)
puff1.off()
puff2.off()
puff3.off()
puff4.off()
#RFID interrupts as detectors GPIO cluster 16 19 20 26
detect1 = DigitalInputDevice(20, pull_up=False)
detect2 = DigitalInputDevice(26)
detect3 = DigitalInputDevice(19) 
detect4 = DigitalInputDevice(16)

animal1=tag1
animal2=tag2
animal3=tag3
animal4=tag4

savepath="/home/pi/Documents/Data/"

event_list1 = {
    "Mode" : ["initialize"], 
    "Start_Time": [datetime.now()],
    "Animal": [0],
    "Weight": [round(float(get_reading(mux[0]["instance"],4)),2)],
    "Unit":1,
    "Pellets" : [pel1],   
}
event_list2 = {
    "Mode" : ["initialize"], 
    "Start_Time": [datetime.now()],
    "Animal": [0],
    "Weight": [round(float(get_reading(mux[0]["instance"],6)),2)],
    "Unit":2,
    "Pellets" : [pel2],   
}
event_list3 = {
    "Mode" : ["initialize"], 
    "Start_Time": [datetime.now()],
    "Animal": [0],
    "Weight": [round(float(get_reading(mux[0]["instance"],3)),2)],
    "Unit":3,
    "Pellets" : [pel3],   
}
event_list4 = {
    "Mode" : ["initialize"], 
    "Start_Time": [datetime.now()],
    "Animal": [0],
    "Weight": [round(float(get_reading(mux[0]["instance"],1)),2)],
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
    if mode_switch:
        if datetime.now()>switch_time:
            mode=mode+1
            print("mode switched to")
            print(mode)
            if mode==2 or mode==4 or mode==7:
                authorize_puff.on()
                print("puffs authorized at 50% likelihood")
            elif mode==3 or mode==8:
                authorize_puff.off()
                print("puffs on if weight gain")
            else:
                authorize_puff.off()
                print("puffs OFF")
            mode_switch=False
            
    eat1.when_activated=count_pel1
    eat2.when_activated=count_pel2
    eat3.when_activated=count_pel3
    eat4.when_activated=count_pel4

    if detect1.value == 0:
        print("unit1")
        tag1=int(scan_tag1(mux[0]["instance"],5))
        event_list1.update({'Pellets': [pel1]})
        save.append_event(event_list1)
        pel1=0
        event_list1.update({'Start_Time': [datetime.now()]})
        event_list1.update({'Animal': [tag1]})
        weight1=round(float(get_reading(mux[0]["instance"],4)),2) 
        if tag1 in known_tags:
            if mode==3:
                puff1.off()
                event_list1.update({'Mode': [mode]})
                check_weight_gain(tag1,weight1,1)
            elif mode==2:
                update_weight_median(tag1,weight1)
        event_list1.update({'Weight': [weight1]})
        action_time=datetime.now()
        unit_flag1=False
        
    if detect2.value == 0:
        print("unit2")
        tag2=int(scan_tag2(mux[0]["instance"],7))
        event_list2.update({'Pellets': [pel2]})
        save.append_event(event_list2)
        pel2=0
        event_list2.update({'Start_Time': [datetime.now()]})
        event_list2.update({'Animal': [tag2]})
        weight2=round(float(get_reading(mux[0]["instance"],6)),2)
        if tag2 in known_tags:
            if mode==3:
                puff2.off()
                event_list2.update({'Mode': [mode]})
                check_weight_gain(tag2,weight2,2)
            elif mode==2:
                update_weight_median(tag2,weight2)
        event_list2.update({'Weight': [weight2]})
        action_time=datetime.now()
    if detect3.value == 0:
        print("unit3")
        tag3=int(scan_tag3(mux[0]["instance"],2))
        event_list3.update({'Pellets': [pel3]})
        save.append_event(event_list3)
        pel3=0
        event_list3.update({'Start_Time': [datetime.now()]})
        event_list3.update({'Animal': [tag3]})
        weight3=round(float(get_reading(mux[0]["instance"],3)),2) 
        if tag3 in known_tags:
            if mode==3:
                puff3.off()
                event_list3.update({'Mode': [mode]})
                check_weight_gain(tag3,weight3,3)
            elif mode==2:
                update_weight_median(tag3,weight3)
        event_list3.update({'Weight': [weight3]})
        action_time=datetime.now()
    if detect4.value == 0:
        print("unit4")
        tag4=int(scan_tag4(mux[0]["instance"],0 ))
        event_list4.update({'Pellets': [pel4]})
        save.append_event(event_list4)
        pel4=0
        event_list4.update({'Start_Time': [datetime.now()]})
        event_list4.update({'Animal': [tag4]})
        weight4=round(float(get_reading(mux[0]["instance"],1)),2) 
        if tag4 in known_tags:
            if mode==3:
                puff4.off()
                event_list4.update({'Mode': [mode]})
                check_weight_gain(tag4,weight4,4)
            elif mode==2:
                update_weight_median(tag4,weight4)
        event_list4.update({'Weight': [weight4]}) 
        action_time=datetime.now()
            
    # force data collection and upload when user presses alt
    if keyboard.is_pressed('alt'):
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
        print(weight_history)
        df_h = pd.DataFrame(weight_history)
        df_h.to_csv(weight_history_file, header=False, encoding="utf-8-sig", index=False)
        upload_time=datetime.now()-upload_interval
        action_time=datetime.now()-action_interval
    time_since_upload=datetime.now()-upload_time
    time_since_action=datetime.now()-action_time
    
    if time_since_upload>upload_interval:
        if time_since_action>action_interval:
            try:
                import rex1_fig_generator.py
            except:
                print("fig creation raised messages")
            try:
                #deposit weight data to public repository
                upload_time=datetime.now()
                g = Github("token here")
                repo = g.get_user().get_repo('mazerex2') # repo name
                file_list=list()
                file_names=list()
                datetag=str(date.today())
                file_list.append(savepath + datetag + "_events.csv")
                file_names.append("fem3_R5test/" + datetag + "_events.csv")
                datetag=str(date.today()-timedelta(days = 1))
                file_list.append(savepath + datetag + "_events.csv")
                file_names.append("fem3_R5test/" + datetag + "_events.csv")
                file_list.append(savepath + "rig1output.svg")
                file_names.append("fem3_R5test/rig1output.svg")
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
                
                
                