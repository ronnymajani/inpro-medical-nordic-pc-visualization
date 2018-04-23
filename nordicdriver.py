# -*- coding: utf-8 -*-
import bluepy.btle as btle
from bluepy.btle import Scanner, DefaultDelegate
import threading


class NordicDriver(threading.Thread):
    NORDIC_NAME = "InPro"
    # UUID_BASE = "D2ACxxxx-E607-4DAA-9E03-9453C15B3FE9"
    INPRO_SERVICE_UUID = "D2AC1523-E607-4DAA-9E03-9453C15B3FE9"
    #PRESSURE_SENSOR_UUIDS = (
    #    "D2AC1524-E607-4DAA-9E03-9453C15B3FE9",  # Pressure Sensor 0 Characteristic UUID
    #    "D2AC1525-E607-4DAA-9E03-9453C15B3FE9",  # Pressure Sensor 1 Characteristic UUID
    #    "D2AC1526-E607-4DAA-9E03-9453C15B3FE9",  # Pressure Sensor 2 Characteristic UUID
    #    "D2AC1527-E607-4DAA-9E03-9453C15B3FE9"  # Pressure Sensor 3 Characteristic UUID
    #)
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.running = True
        self._found_device_info = None
        self.device = None
        self._inpro_service = None
        self._pressure_sensors_chars = None
        self.delegate = NordicDriver._NordicDelegate()
        self.plot = None

    def set_plot_func(self, func):
        self.plot = func
    
    def _scan(self):
        """ Scans for InPro device in range. If found, saves its info
        @returns True if InPro device was found
        @returns False if InPro device was not found
        """
        scanner = Scanner().withDelegate(self.delegate)
        devices = scanner.scan(2.0)
        for dev in devices:
            print("Device: %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))
            for (adType, desc, value) in dev.getScanData():
                print("   %s = %s" % (desc, value))
                if desc == "Complete Local Name" and value == NordicDriver.NORDIC_NAME:
                    self._found_device_info = dev
                    print("InPro device found!")
                    return True
        return False
    
    def find_device(self):
        """ Keeps scanning for InPro device until it is found """
        while True:
            if self._scan():
                break
            
    def _connect(self, addr=None, addr_type=None):
        if addr is None:
            addr = self._found_device_info.addr
            addr_type = self._found_device_info.addrType
        elif addr_type is None:
            addr_type = btle.ADDR_TYPE_RANDOM
            
        try:
            self.device = btle.Peripheral(addr, addr_type)
            return True
        except btle.BTLEException:
            return False
        
            
    def connect(self, addr=None, addr_type=None, keep_trying=True):
        """ Connect to the Nord device
        @param[optional] addr: the MAC address of the Nord device.
            if not specified the result from find_device() is used
        @param[optional] addr_type: the type of the given MAC address.
            only use if addr field is given. if not specified, 'random' is assumed
        @param[optional] keep_trying: whether to try once or keep trying until success
        """
        if keep_trying:
            while True:
                if self._connect(addr, addr_type):
                    return True
        else:
            return self._connect(addr, addr_type)
        
    def _get_inpro_service(self):
        """ Get the handle of the InPro GATT service from the connected device """
        self._inpro_service = self.device.getServiceByUUID(NordicDriver.INPRO_SERVICE_UUID)
        
    def _get_pressure_sensor_chars(self):
        """ Get a list of characteristics located in the InPro service
        (it is assumed that all these characteristics are pressures sensors)
        call this after _get_inpro_service() has been called.
        """
        self._pressure_sensors_chars = self._inpro_service.getCharacteristics()
        
    def _enable_pressure_sensor_notifications(self):
        """ Enable notifications for all the pressure sensors 
        call this after _get_pressure_sensor_chars() has been called
        """
        on_cmd = int(1).to_bytes(1, byteorder='big', signed=False)
        for sensor_char in self._pressure_sensors_chars:
            sensor_notif_handle = sensor_char.handle + 2
            self.device.writeCharacteristic(sensor_notif_handle, on_cmd)
            
    def _get_pressure_sensor_values(self):
        """ Manually request a read of all the pressure sensor values 
        call this after _get_pressure_sensor_chars() has been called
        """
        self.delegate.read_values(self._pressure_sensors_chars)
            
    def initialize(self):
        """ Performs all initializations and starts the driver.
        This includes, making sure a connection exists, enabling notifications,
        and starting this classes thread that will keep polling for notifications
        """
        if self.device is None:
            self.find_device()
            self.connect()
        # get the InPro service information
        self._get_inpro_service()
        # get the pressure sensor characteristics
        self._get_pressure_sensor_chars()
        # read initial values of pressure sensors
        self._get_pressure_sensor_values()
        # enable notifications
        self._enable_pressure_sensor_notifications()
        # register te delegate class to handle notifications
        self.device.withDelegate(self.delegate)
        # start this classes thread @see run()
        self.start()
        
    def run(self):
        """ poll for new notifications.
        @note: notifications are handled by the _NordicDelegate class instance (self.delegate)
        """
        while self.running:
            if self.device.waitForNotifications(1.0):
                # notifications were received and processed
                continue
            else:
                # no notifications received
                continue
        self.device.disconnect()
            
    def stop(self):
        """ Stop this class's thread (the run() function) """
        self.running = False
    
    def get_all_pressure_sensor_values(self):
        """ Return a 2D matrix of the pressure sensors' values. """
        vals = self.delegate.values
        pressure_vals = []
        for sensor_char in self._pressure_sensors_chars:
            handle = sensor_char.getHandle()
            if handle in vals:
                pressure_vals.append(vals[handle])
        return [pressure_vals]
        

    class _NordicDelegate(DefaultDelegate):
        """ This class handles callbacks related to the BTLE driver """
        def __init__(self):
            DefaultDelegate.__init__(self)
            self.values = {}
            
        def read_values(self, chars):
            """ We defined thsi function to manually poll for and save the values of the given characteristics """
            for c in chars:
                val = c.read()
                val = int.from_bytes(val, byteorder='big', signed=False)
                self.values[c.getHandle()] = val
                
        def handleNotification(self, cHandle, data):
            """ Handles received notification DTUs.
            We simply save them in a dictionary after converting their values into integers (from raw bytes).
            @note: It is assumed that only pressure sensor values are received as notifications!
            """
            val = int.from_bytes(data, byteorder='big', signed=False)
            self.values[cHandle] = val
            
        def handleDiscovery(self, dev, isNewDev, isNewData):
            """ Callbck for discovering new devices during scanning.
            We don't use this function except to show that the scanning functionality is working.
            """
            if isNewDev:
                print("Discovered device", dev.addr)
            elif isNewData:
                print("Received new data from", dev.addr)
            

