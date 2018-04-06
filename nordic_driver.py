#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  5 20:37:21 2018

@author: ronnymajani
"""

import pygatt
from uuid import UUID
import logging


class NordicBluetoothDriver(object):
    
    BLUETOOTH_NAME = "InPro"
    UUID_BASE = "D2ACxxxx-E607-4DAA-9E03-9453C15B3FE9"
    PRESSURE_SENSOR_UUIDS = (
        UUID("D2AC1524-E607-4DAA-9E03-9453C15B3FE9"),  # Pressure Sensor 0 Characteristic UUID
        UUID("D2AC1525-E607-4DAA-9E03-9453C15B3FE9"),  # Pressure Sensor 1 Characteristic UUID
        UUID("D2AC1526-E607-4DAA-9E03-9453C15B3FE9"),  # Pressure Sensor 2 Characteristic UUID
        UUID("D2AC1527-E607-4DAA-9E03-9453C15B3FE9")  # Pressure Sensor 3 Characteristic UUID
    )
    
    def __init__(self):
        self.address = None
        self.device = None
        self.logger = logging.getLogger(name="NordicBluetoothDriver")
        self.adapter = pygatt.GATTToolBackend()
        self._start()
        
    def _start(self):
        """ Attempts to start the BLE adapter """
        try:
            self.adapter.start()
        except:
            self.logger.error("Please make sure BlueZ is installed and run this program in Linux!")
            self._stop()
            raise RuntimeError("Failed to start BLE adapter!")
            
    def _stop(self):
        """ Stops the BLE adapter """
        self.adapter.stop()
        
    def _scan_for_device(self):
        """ Scans for BLE devices in range. Attempts to find the InPro device,
        and if it is found, it saves it's address """
        try:
            devices = self.adapter.scan()
        except:
            self.logger.error("If you are having root permission errors, check this link:")
            self.logger.error("https://unix.stackexchange.com/questions/96106/bluetooth-le-scan-as-non-root")
            self.logger.error()
            self.logger.error("basically yuo should run these two commands:")
            self.logger.error("$> sudo apt-get install libcap2-bin")
            self.logger.error("$> sudo setcap 'cap_net_raw,cap_net_admin+eip' `which hcitool`")
            self._stop()
            raise RuntimeError("Failed to scan for devices!")
        # check if our bluetooth device is discovered
        for dev in devices:
            if dev['name'] == NordicBluetoothDriver.BLUETOOTH_NAME:
                self.address = dev['address']
                self.logger.info("Device found; address:" + str(self.address))
                break
        self.adapter.reset()  # reset adpter so we can scan again
        self.logger.info(".")
    
    def find_device(self, scan_once=False):
        """ Scans for Bluetooth devices in range, and attempts to find the InPro device and saves its address
        @param[optional] scan_once: If set to False, the function scans indefinitely until the InPro device is detected.
            If set to True, the function will only scan once
        @returns True if the InPro device was successfully found.
        @returns False if the InPro device wasn't found.
        """
        if scan_once:
            self._scan_for_device()
        else:
            # scan for devices until our beloved device is discovered
            while self.address is None:
                self._scan_for_device()
                
        return self.address is not None
    
    def _connect(self):
        """ Attempts to connect to the InPro device 
        @returns True: If connection was successful
        @returns False: If connection failed
        """
        if self.address is None:
            raise RuntimeError("Please set the device's address before attempting to connect!")
            
        self.logger.info("trying to connect...")
        try:
            self.device = self.adapter.connect(self.address, address_type=pygatt.BLEAddressType.random)
            self.logger.info("Successfully connected!")
            return True
        except:
            self.logger.error("failed to connect!")
            return False
    
    def connect(self, try_once=False, address=None):
        """ Attempts to connect to the InPro device 
        @param[optional] try_once: if True, the function will only try to connect once.
            If False, the function will keep trying indefinitely, until successful
        @param[optional] address: If none, the function will use the address previously found by find_device
        @returns True: If connection was successful
        @returns False: If connection failed
        """
        if address is not None:
            self.address = address
        else:
            if self.address is None:
                raise RuntimeError("Please first set the device's address before attempting to connect. Try calling find_devic()")
        
        success = False
        if try_once:
            success = self._connect()
        else:
            while not success:
                success = self._connect()
        return success
    
    def read_pressure_sensor_value(self, sensor_number):
        if sensor_number >= len(NordicBluetoothDriver.PRESSURE_SENSOR_UUIDS) or sensor_number < 0:
            raise ValueError("Sensor number %d does not exist" % sensor_number)
        return self.device.char_read(NordicBluetoothDriver.PRESSURE_SENSOR_UUIDS[sensor_number])
            
