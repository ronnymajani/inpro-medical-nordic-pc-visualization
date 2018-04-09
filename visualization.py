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
        self._setup_plot()
        
    def _setup_plot(self):
        self.fig = plt.figure()
        self.fig.canvas.mpl_connect('close_event', self._handle_close)
        self.ax = self.fig.add_subplot(111)
        self.im = self.ax.imshow(self._get_values(), cmap=matplotlib.cm.YlOrRd)
        plt.show(block=False)
        
    def _get_values(self):
        vals = self.nordicDriver.get_all_pressure_sensor_values()
        vals = [vals[0][:2], vals[0][2:]]
        return vals
        
    def plot(self):
        self.im.set_array(self._get_values())
        self.fig.canvas.draw()
        
    def run(self):
        """
        Display the simulation using matplotlib, using blit for speed
        """
        while self.running:
            self.plot()
            time.sleep(VisualizationWindow.REFRESH_SPEED)
    
        plt.close(self.fig)
        
    def _handle_close(self, evt):
        self.stop()
        self.nordicDriver.stop()
        
    def stop(self):
        """ Stop Visualization Task """
        self.running = False
        

