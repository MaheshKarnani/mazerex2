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

#Load previous calibration data
# scale_cal=[1,1,1,1,1,1,1,1]
# scale_tare=[0,0,0,0,0,0,0,0]
scale_cal_filepath="/home/rex2/Documents/Data/ScaleCal.json"
scale_tare_filepath="/home/rex2/Documents/Data/ScaleTare.json"
with open(scale_cal_filepath, 'r') as file:
    scale_cal=json.load(file)
with open(scale_tare_filepath, 'r') as file:
    scale_tare=json.load(file)
    
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

def calibrate_scale(mux,port):
    global scale_cal
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
    print("Taring.")
    nau.calculateZeroOffset()
    scale_tare[port]=nau.getZeroOffset()
    nau.setZeroOffset(scale_tare[port])
    print("Zero offset is : {0}\n".format(scale_tare[port]))
    weight=nau.getWeight() * 1000
    print("Mass {0:0.3f} g".format(weight))
    input("Put 25g weight on scale and press enter")
    cal=float(0.025)
    print("Calibrating.")
    nau.calculateCalibrationFactor(cal)
    scale_cal[port]=nau.getCalibrationFactor()
    nau.setCalibrationFactor(scale_cal[port])
    weight=nau.getWeight() * 1000
    print("Mass {0:0.3f} g".format(weight))
    disable_port(mux, port)
    return weight, scale_cal

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
    return weight

mux = create_instance()

for i, val in enumerate(mux):
    print(i)
    mux[i]["scales"] = initialize_scales(mux[i]["instance"])
get_reading(mux[0]["instance"],3)
get_reading(mux[0]["instance"],1)
# get_reading(mux[0]["instance"],4)
# get_reading(mux[0]["instance"],6)
calibrate_scale(mux[0]["instance"],3)
calibrate_scale(mux[0]["instance"],1)
# calibrate_scale(mux[0]["instance"],4)
# calibrate_scale(mux[0]["instance"],6)
with open(scale_cal_filepath, 'w') as file:
    json.dump(scale_cal, file)
with open(scale_tare_filepath, 'w') as file:
    json.dump(scale_tare, file)
get_reading(mux[0]["instance"],3)
get_reading(mux[0]["instance"],1)
# get_reading(mux[0]["instance"],4)
# get_reading(mux[0]["instance"],6)