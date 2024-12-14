import qwiic_tca9548a
import PyNAU7802
import smbus2
import time
import json
import requests
import qwiic_rfid
import sys


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
    print("mux data")    
    print(mux)
    print("end mux data") 
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
        #take readings..
        nau.calculateZeroOffset()
        print("The zero offset is : {0}\n".format(nau.getZeroOffset()))
        n=nau.getWeight() * 1000
        print("Mass {0:0.3f} g".format(n))
        
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
    n=nau.getWeight() * 1000
    print("Mass {0:0.3f} g".format(n))
    disable_port(mux, port)

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
    my_RFID2 = qwiic_rfid.QwiicRFID(0x5B)
    if not my_RFID2.begin():
        # print(f"NOT CONNECTED TO : {port} \n")
        disable_port(mux, port)
    tag2 = my_RFID2.get_tag()
#     scan_time = my_RFID.get_prec_req_time()
    disable_port(mux, port)
    return tag2


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
print(tag1)
print(tag2)