# -*- coding: utf-8 -*-
""" 
This code uses bluepy and matplotlib
Bluepy: https://github.com/IanHarvey/bluepy

First Install these libraries:
$ sudo apt install python3-pip libglib2.0-dev
    
Install matplotlib using pip3
$ pip3 install matplotlib

Install bluepy library using pip3
$ pip3 install bluepy

To Run this app without root permissions, run this command 
$ sudo setcap 'cap_net_raw,cap_net_admin+eip' /PATH/TO/bluepy/bluepy-helper

to find out where bluepy was installed, type:
$ pip3 show bluepy

on this device bluepy-helper was installed in:
/home/pi/.local/lib/python3.5/site-packages/bluepy/bluepy-helper
so we set its permissions like this:
$ sudo setcap 'cap_net_raw,cap_net_admin+eip' /home/pi/.local/lib/python3.5/site-packages/bluepy/bluepy-helper
"""
#%%

from nordicdriver import NordicDriver
from visualization import VisualizationWindow

if __name__ == "__main__":
    # start nordic driver
    driver = NordicDriver()
    driver.initialize()
    # start visualization
    visualizer = VisualizationWindow(driver)
    visualizer.start()
    # wait for threads to end
    visualizer.join()
    driver.join()
    
        