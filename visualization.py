#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  5 20:37:21 2018

@author: ronnymajani
"""

import threading
import matplotlib.cm
import matplotlib.pyplot as plt
import time


class VisualizationWindow(threading.Thread):
    # How many seconds to wait between windows updates
    REFRESH_SPEED = 0.1
    
    def __init__(self, nordic_driver):
        threading.Thread.__init__(self)
        self.daemon = True
        self.running = True
        self.pressure_values = []
        self.nordicDriver = nordic_driver
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        vals = self.nordicDriver.get_all_pressure_sensor_values()
        self.im = self.ax.imshow(vals)
        plt.show(block=False)
        
    def plot(self):
        vals = self.nordicDriver.get_all_pressure_sensor_values()
        self.im.set_array(vals)
        self.fig.canvas.draw()
        
    def run(self):
        """
        Display the simulation using matplotlib, using blit for speed
        """
        while self.running:
            self.plot()
            time.sleep(VisualizationWindow.REFRESH_SPEED)
    
        plt.close(self.fig)
        
    def stop(self):
        """ Stop Visualization Task """
        self.running = False
        

