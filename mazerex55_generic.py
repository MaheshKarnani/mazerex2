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
savepath="/home/pi/Documents/Data/"

'''combined init for autolindz and rex'''
interval=timedelta(seconds=10)
state3=0 #lindzey tube entry states,
state4=0
timeout_flag=True
timeout_start=datetime.now()
timeout_dur=timedelta(seconds=10) # 2 30: v low; 3 120: none; 30s 30s:
doorA_open=DigitalInputDevice(15)
doorB_open=DigitalInputDevice(14)
tube_active=True
close_flag=False
object_start=datetime.now()
close_time=datetime.now()

mode=0 #experiment mode 0=habituation, 1=bsl, 2=induction, 3=post, 4=induction_repeat, 5=post_repeat
mode_switch=False
#Experiment plan
time_line = np.array(pd.read_csv(savepath+"TimeLine.csv", header=None)).astype(np.datetime64).reshape(-1,1)
print(time_line)
#find current mode
init_time=np.datetime64(datetime.today())
states=(init_time>time_line).ravel().tolist()
mode=max(np.where(states)[0])
print(mode)
#find if today is a transition
states=(init_time+timedelta(hours=12)>time_line).ravel().tolist()
next_mode=max(np.where(states)[0])
print(next_mode)
if mode==next_mode:
    print('no mode transition today')
else:
    mode_switch=True # will trigger mode+1 at 12pm.
    switch_time=datetime.combine(date.today(),time(12,0))
    print('mode transition set for', switch_time)   
  
# mode=2
authorize_puff=DigitalOutputDevice(21)
print("mode is")
print(mode)
if mode==2 or mode==4:
    authorize_puff.on()
    print("puffs authorized")
else:
    authorize_puff.off()
    print("puffs OFF")
if mode_switch:
    print("switching modes today at")
    print(switch_time)
    
#load scale calibration files
scale_cal_filepath=savepath+"ScaleCal.json"
scale_tare_filepath=savepath+"ScaleTare.json"
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
    my_RFID1 = qwiic_rfid.QwiicRFID(0x14)
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
    my_RFID2 = qwiic_rfid.QwiicRFID(0x13)
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
    my_RFID3 = qwiic_rfid.QwiicRFID(0x12)
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
    my_RFID4 = qwiic_rfid.QwiicRFID(0x13)
    if not my_RFID4.begin():
        # print(f"NOT CONNECTED TO : {port} \n")
        disable_port(mux, port)
    tag4 = my_RFID4.get_tag()
#     print(int(tag4))
#     scan_time = my_RFID.get_prec_req_time()
    disable_port(mux, port)
    bus.close()
    return tag4

mux = create_instance()

for i, val in enumerate(mux):
    print(i)
    mux[i]["scales"] = initialize_scales(mux[i]["instance"])
get_reading(mux[0]["instance"],4)
get_reading(mux[0]["instance"],1)

tag1=int(scan_tag1(mux[0]["instance"],2))
tag2=int(scan_tag2(mux[0]["instance"],0))
tag3=int(scan_tag3(mux[0]["instance"],7))
tag4=int(scan_tag4(mux[0]["instance"],6))
print(tag1)
print(tag2)
print(tag3)
print(tag4)

#setup counter channel for FED3 pellets
pel1=0
eat1=DigitalInputDevice(24)
def count_pel1():
    global pel1
    pel1+=1
pel2=0
eat2=DigitalInputDevice(17)
def count_pel2():
    global pel2
    pel2+=1
# puff controls for individual authorisation (not in use, might need later)
puff1=DigitalOutputDevice(5)
puff2=DigitalOutputDevice(6)
puff1.off()
puff2.off()

#RFID interrupts GPIO cluster
detect1 = DigitalInputDevice(16)
detect2 = DigitalInputDevice(13)
detect3 = DigitalInputDevice(19) 
detect4 = DigitalInputDevice(26)

beam1_detect = DigitalInputDevice(12)

#serial to arduino
ser = serial.Serial('/dev/ttyUSB0', 9600)
tim.sleep(2)

animal1=tag1
animal2=tag2
animal3=tag3
animal4=tag4

test_tags=[19647231169,1111110210210]
animal_tags = np.array(pd.read_csv(savepath + "AnimalTags.csv", header=None)).ravel().tolist()
known_tags=test_tags+animal_tags
print(known_tags)

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
    "Weight": [round(float(get_reading(mux[0]["instance"],1)),2)],
    "Unit":2,
    "Pellets" : [pel2],   
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
class SaveData:
    def append_event(self,event_list):
        df_e = pd.DataFrame(event_list)
        datetag=str(date.today())
        if not os.path.isfile(savepath + datetag + "_events.csv"):
            df_e.to_csv(savepath + datetag + "_events.csv", encoding="utf-8-sig", index=False)
        else:
            df_e.to_csv(savepath + datetag + "_events.csv", mode="a+", header=False, encoding="utf-8-sig", index=False)
    def append_lindzey(self,event_list):
        df_e = pd.DataFrame(event_list)
        datetag=str(date.today())
        if not os.path.isfile(savepath + datetag + "_autolindz.csv"):
            df_e.to_csv(savepath + datetag + "_autolindz.csv", encoding="utf-8-sig", index=False)
        else:
            df_e.to_csv(savepath + datetag + "_autolindz.csv", mode="a+", header=False, encoding="utf-8-sig", index=False)

save = SaveData()
save.append_event(event_list1)
save.append_event(event_list2)
save.append_lindzey(event_list3)
save.append_lindzey(event_list4)
event_list1.update({'Mode': [mode]})
event_list2.update({'Mode': [mode]})
event_list3.update({'Mode': [state3]})
event_list4.update({'Mode': [state4]})
upload_flag=False
upload_time=datetime.now()
upload_interval=timedelta(hours=6) #minimum interval between uploads, hours suggested
action_time=datetime.now()
lindz_action_time=datetime.now()
action_interval=timedelta(minutes=15) #safe interval from last detection to start upload, 15 min suggested
ser.write(str.encode('b'))
ser.write(str.encode('c'))
test_started=False
start_time=datetime.now()
# Experiment loop
while True:
    if mode_switch:
        if datetime.now()>switch_time:
            mode=mode+1
            print("mode switched to")
            print(mode)
            if mode==2 or mode==4:
                authorize_puff.on()
                print("puffs authorized at 50% likelihood")
            else:
                authorize_puff.off()
                print("puffs OFF")
            mode_switch=False
            
    eat1.when_activated=count_pel1
    eat2.when_activated=count_pel2

    if detect1.value == 0:
        print("unit1")
        tag1=int(scan_tag1(mux[0]["instance"],2))
        print(tag1)
        if tag1 in known_tags:
            event_list1.update({'Pellets': [pel1]})
            save.append_event(event_list1)
            pel1=0
            event_list1.update({'Start_Time': [datetime.now()]})
            event_list1.update({'Animal': [tag1]})
            weight1=round(float(get_reading(mux[0]["instance"],4)),2) 
            event_list1.update({'Weight': [weight1]})
            action_time=datetime.now()
        
    if detect2.value == 0:
        print("unit2")
        tag2=int(scan_tag2(mux[0]["instance"],0))
        print(tag2)
        if tag2 in known_tags:
            event_list2.update({'Pellets': [pel2]})
            save.append_event(event_list2)
            pel2=0
            event_list2.update({'Start_Time': [datetime.now()]})
            event_list2.update({'Animal': [tag2]})
            weight2=round(float(get_reading(mux[0]["instance"],1)),2)
            event_list2.update({'Weight': [weight2]})
            action_time=datetime.now()
    
    #Lindzey tube:
    if timeout_flag:
        if detect3.value == 0 or detect4.value == 0:
            print('unusual RFID detected during Lindzey timeout')
            tag3=int(scan_tag3(mux[0]["instance"],7))
            print(tag3)
            tag4=int(scan_tag4(mux[0]["instance"],6))
            print(tag4)
        if object_start+interval<datetime.now() and beam1_detect.value==0:
            print('unusual object detected during Lindzey timeout')
            object_start=datetime.now()
        if timeout_start+timeout_dur<datetime.now():
            timeout_flag=False
            tube_active=False
            close_flag=False
            ser.write(str.encode('a'))
            print('TUBE OPEN')
            status_list.update({'Start_Time': [datetime.now()]})
            status_list.update({'Mode': ["OPEN"]})
            save.append_lindzey(status_list)
            detect_list_A=list()
            detect_list_B=list()
                
    if not timeout_flag:
        if detect3.value == 0:
            tag3=int(scan_tag3(mux[0]["instance"],7))
            print(tag3)
            if tag3 in known_tags:
                ser.write(str.encode('b'))
                close_time=datetime.now()
                close_flag=True
                print(known_tags.index(tag3))
                event_list3.update({'Start_Time': [datetime.now()]})
                event_list3.update({'Animal': [tag3]})
                event_list3.update({'Mode': [state3]})
                event_list4.update({'Mode': [state4]})
                save.append_lindzey(event_list3)#for this animal
                state3=state3+1
                if doorA_open.value == 1 and detect_list_A and (tag3 not in detect_list_A):
                    ser.write(str.encode('c'))
                    close_time=datetime.now()
                    close_flag=True
                    print("followerA")
                    status_list.update({'Start_Time': [datetime.now()]})
                    status_list.update({'Mode': ["followerA"]})
                    save.append_lindzey(status_list)
                detect_list_A.append(tag3)
                start_time=datetime.now()
        if detect4.value == 0:
            tag4=int(scan_tag4(mux[0]["instance"],6))
            lindz_action_time=datetime.now()
            if tag4 in known_tags:
                ser.write(str.encode('c'))
                close_time=datetime.now()
                close_flag=True
                print(known_tags.index(tag4))
                event_list4.update({'Start_Time': [datetime.now()]})
                event_list4.update({'Animal': [tag4]})
                event_list3.update({'Mode': [state3]})
                event_list4.update({'Mode': [state4]})
                save.append_lindzey(event_list4)#for this animal
                state4=state4+1
                if doorB_open.value == 1 and detect_list_B and (tag4 not in detect_list_B):
                    ser.write(str.encode('b'))
                    close_time=datetime.now()
                    close_flag=True
                    print("followerB")
                    status_list.update({'Start_Time': [datetime.now()]})
                    status_list.update({'Mode': ["followerB"]})
                    save.append_lindzey(status_list)
                detect_list_B.append(tag4)
                start_time=datetime.now()
        if close_flag and not tube_active and close_time+interval<datetime.now() and beam1_detect.value==1:#unobstructed, a mouse likely triggered and retreated.
            ser.write(str.encode('b'))
            print('a door has closed and tube empty -- timeout and reset')
            ser.write(str.encode('c'))
            state3=0
            state4=0
            tube_active=False
            timeout_start=datetime.now()
            timeout_flag=True #breaks to timeout state, so no more saved data, only printouts
        if not tube_active and (state3>0 or state4>0) and doorA_open.value == 0 and doorB_open.value == 0:
            print('tube closed')
            start_time=datetime.now()
            tube_active=True
            status_list.update({'Start_Time': [datetime.now()]})
            animalsA=set(detect_list_A)
            animalsB=set(detect_list_B)
            if len(animalsA)==1 and len(animalsB)==1:
                if animalsA==animalsB:
                    print('solo traversal')
                    status_list.update({'Mode': ["solo"]})
                else:#dominance test in progress
                    print('dominance test in progress')
                    status_list.update({'Mode': ["start Lindzey"]})
                    test_started=True
            else:#following in progress
                print('sequence in tube')
                status_list.update({'Mode': ["sequence"]})
            save.append_lindzey(status_list)
        if tube_active and start_time+interval<datetime.now():
            if beam1_detect.value==1:#unobstructed
                print('event finished and tube empty')
                state3=0
                state4=0
                tube_active=False
                timeout_start=datetime.now()
                timeout_flag=True #breaks to timeout state, so no more saved data, only printouts
                if test_started:
                    status_list.update({'Start_Time': [datetime.now()]})
                    status_list.update({'Mode': ["End Lindzey"]})
                    save.append_lindzey(status_list)
                    test_started=False
            else:     
                print('tube still active')
                start_time=datetime.now()
            
    # force data collection and upload when user presses alt
    if keyboard.is_pressed('alt'):
        event_list1.update({'Pellets': [pel1]})
        save.append_event(event_list1)
        pel1=0
        event_list2.update({'Pellets': [pel2]})
        save.append_event(event_list2)
        pel2=0
        
        print("last entries saved from all units")
        upload_time=datetime.now()-upload_interval
        action_time=datetime.now()-action_interval
    time_since_upload=datetime.now()-upload_time
    time_since_action=datetime.now()-action_time
    
    if time_since_upload>upload_interval:
        if time_since_action>action_interval:
            if upload_flag:
                try:
                    #deposit weight data to public repository
                    upload_time=datetime.now()
                    g = Github("token")
                    repo = g.get_user().get_repo('mazerex2') # repo name
                    file_list=list()
                    file_names=list()
                    datetag=str(date.today())
                    file_list.append(savepath + datetag + "_events.csv")
                    file_names.append("cohort2/fem4_e_PFChm4di_rex1/" + datetag + "_events.csv")
                    file_list.append(savepath + datetag + "_autolindz.csv")
                    file_names.append("cohort2/fem4_e_PFChm4di_rex1/" + datetag + "_autolindz.csv")
                    datetag=str(date.today()-timedelta(days = 1))
                    file_list.append(savepath + datetag + "_events.csv")
                    file_names.append("cohort2/fem4_e_PFChm4di_rex1/" + datetag + "_events.csv")
                    file_list.append(savepath + datetag + "_autolindz.csv")
                    file_names.append("cohort2/fem4_e_PFChm4di_rex1/" + datetag + "_autolindz.csv")
                    file_list.append(savepath + "rig1output.svg")
                    file_names.append("cohort2/fem4_e_PFChm4di_rex1/rig1output.svg")
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
                upload_flag=False
            try:
                import rex1_fig_generator.py
            except:
                print("fig creation raised messages")
            upload_flag=True #forces another round through code before upload
