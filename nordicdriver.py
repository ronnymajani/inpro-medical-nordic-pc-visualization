# -*- coding: utf-8 -*-
import bluepy.btle as btle
from bluepy.btle import Scanner, DefaultDelegate
import threading


class NordicDriver(threading.Thread):
    NORDIC_NAME = "InPro"
    UUID_BASE = "D2ACxxxx-E607-4DAA-9E03-9453C15B3FE9"
    INPRO_SERVICE_UUID = "D2AC1523-E607-4DAA-9E03-9453C15B3FE9"
    PRESSURE_SENSOR_UUIDS = (
        "D2AC1524-E607-4DAA-9E03-9453C15B3FE9",  # Pressure Sensor 0 Characteristic UUID
        "D2AC1525-E607-4DAA-9E03-9453C15B3FE9",  # Pressure Sensor 1 Characteristic UUID
        "D2AC1526-E607-4DAA-9E03-9453C15B3FE9",  # Pressure Sensor 2 Characteristic UUID
        "D2AC1527-E607-4DAA-9E03-9453C15B3FE9"  # Pressure Sensor 3 Characteristic UUID
    )
    PRESSURE_SENSOR_LABELS = (
        "Pressure Sensor 0",        
        "Pressure Sensor 1",
        "Pressure Sensor 2",
        "Pressure Sensor 3",
    )
    
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
        self._inpro_service = self.device.getServiceByUUID(NordicDriver.INPRO_SERVICE_UUID)
        
    def _get_pressure_sensor_chars(self):
        self._pressure_sensors_chars = self._inpro_service.getCharacteristics()
        
    def _enable_pressure_sensor_notifications(self):
        on_cmd = int(1).to_bytes(1, byteorder='big', signed=False)
        for sensor_char in self._pressure_sensors_chars:
            sensor_notif_handle = sensor_char.handle + 2
            self.device.writeCharacteristic(sensor_notif_handle, on_cmd)
            
    def _get_pressure_sensor_values(self):
        self.delegate.read_values(self._pressure_sensors_chars)
            
    def initialize(self):
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
        while self.running:
            if self.device.waitForNotifications(1.0):
                # notifications were received and processed
                continue
            else:
                # no notifications received
                continue
            
    def stop(self):
        self.running = False
    
    def get_all_pressure_sensor_values(self):
        vals = self.delegate.values
        pressure_vals = []
        for sensor_char in self._pressure_sensors_chars:
            handle = sensor_char.getHandle()
            if handle in vals:
                pressure_vals.append(vals[handle])
        return [pressure_vals]
        

    class _NordicDelegate(DefaultDelegate):
        def __init__(self):
            DefaultDelegate.__init__(self)
            self.values = {}
            
        def read_values(self, chars):
            for c in chars:
                val = c.read()
                val = int.from_bytes(val, byteorder='big', signed=False)
                self.values[c.getHandle()] = val
                
        def handleNotification(self, cHandle, data):
            val = int.from_bytes(data, byteorder='big', signed=False)
            self.values[cHandle] = val
            
        def handleDiscovery(self, dev, isNewDev, isNewData):
            if isNewDev:
                print("Discovered device", dev.addr)
            elif isNewData:
                print("Received new data from", dev.addr)
            

