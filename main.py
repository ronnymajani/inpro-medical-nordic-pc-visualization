#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  5 20:37:21 2018

@author: ronnymajani
"""

import pygatt
from uuid import UUID

import logging
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

#%%

BLUETOOTH_NAME = "InPro"
UUID_BASE = "D2ACxxxx-E607-4DAA-9E03-9453C15B3FE9"
UUID_PS0 = UUID("D2AC1524-E607-4DAA-9E03-9453C15B3FE9")
UUID_PS1 = UUID("D2AC1525-E607-4DAA-9E03-9453C15B3FE9")
UUID_PS2 = UUID("D2AC1526-E607-4DAA-9E03-9453C15B3FE9")
UUID_PS3 = UUID("D2AC1527-E607-4DAA-9E03-9453C15B3FE9")

#%% Globals
adapter = pygatt.GATTToolBackend()
device_address = None
device = None

#%% Volatiles
pressure_sensor_values = [0, 0, 0, 0]

#%%

try:
    adapter.start()
except:
    print("Please make sure BlueZ is installed and run this program in Linux!")
    adapter.stop()
    quit()
    
while device_address is None:
    # scan for devices until our beloved device is discovered
    try:
        devices = adapter.scan()
    except:
        print("If you are having root permission errors, check this link:")
        print("https://unix.stackexchange.com/questions/96106/bluetooth-le-scan-as-non-root")
        print()
        print("basically yuo should run these two commands:")
        print("$> sudo apt-get install libcap2-bin")
        print("$> sudo setcap 'cap_net_raw,cap_net_admin+eip' `which hcitool`")
        adapter.stop()
        quit()
    # check if our bluetooth device is discovered
    for dev in devices:
        if dev['name'] == BLUETOOTH_NAME:
            device_address = dev['address']
            print("Device found; address:", device_address)
            break
    adapter.reset()  # reset adpter so we can scan again
    print(".", end="")

# Keep trying to connect to the device
while True:
    print("trying to connect...")
    try:
        device = adapter.connect(device_address, address_type=pygatt.BLEAddressType.random)
        print("Successfully connected!")
        break
    except:
        print("failed, to connect!")
        continue

#%% discover characteritics
#keep_trying = True
#while keep_trying:
#    try:
#        device.subscribe(UUID_PS0, lambda h,v: pressure_sensor_changed_callback(0, h, v))
#    except pygatt.BLEError:
#        continue
#    else:
#        keep_trying = False
#        break
#%% callback function
#def pressure_sensor_changed_callback(sensor_number, handle, value):
#    val = int.from_bytes(value, byteorder='big', signed=False)
#    pressure_sensor_values[sensor_number] = val
##    print("Sensor", sensor_number, "value:", val)


#%% Register callbacks
#device.subscribe(UUID_PS0, lambda h,v: pressure_sensor_changed_callback(0, h, v))
#device.subscribe(UUID_PS1, lambda h,v: pressure_sensor_changed_callback(1, h, v))
#device.subscribe(UUID_PS2, lambda h,v: pressure_sensor_changed_callback(2, h, v))
#device.subscribe(UUID_PS3, lambda h,v: pressure_sensor_changed_callback(3, h, v))

#%%
#while True:
#    val = device.char_read(UUID_PS1)
#    val = int.from_bytes(val, byteorder='big', signed=False)
#    print(val)


    

    
#%%
#device.disconnect()
#adapter.stop()