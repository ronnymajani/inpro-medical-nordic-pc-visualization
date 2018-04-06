#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  5 20:37:21 2018

@author: ronnymajani
"""

from visualization import VisualizationTask
from nordic_driver import NordicBluetoothDriver

import logging
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

#%% Volatiles
pressure_sensor_values = [0, 0, 0, 0]

#%%

if __name__ == "__main__":
    driver = NordicBluetoothDriver()
    driver.find_device()
    driver.connect()
    visualization = VisualizationTask(driver)
    visualization.start()

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