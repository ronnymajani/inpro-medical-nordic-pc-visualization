#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  5 20:37:21 2018

@author: ronnymajani
"""

import threading
import matplotlib.cm
import matplotlib.pyplot as plt
import logging


class VisualizationTask(threading.Thread):
    def __init__(self, nordic_driver):
        threading.Thread.__init__(self)
        self.daemon = True
        self.running = True
        self.logger = logging.getLogger("Visualization Task")
        self.pressure_values = []
        self.nordicDriver = nordic_driver
        self.fig, self.ax = plt.subplots(1, 1)
        self._setup_plot()
        
    def _setup_plot(self):
#        self.ax.set_aspect('equal')
        self.ax.hold(True)
        self.ax.set_ylim(0, 255)
        plt.show(False)
        plt.draw()
        
    def run(self):
        """
        Display the simulation using matplotlib, using blit for speed
        """
        
        while self.running:
            labels = self.nordicDriver.get_pressure_sensor_labels()
            vals = self.nordicDriver.get_all_pressure_sensor_values()
            colors = matplotlib.cm.plasma([v/255 for v in vals])
            plt.clf()
            plt.bar(labels, vals, align='center', width=0.5, color=colors)
            plt.draw()
    
        plt.close(self.fig)
        
    def stop(self):
        """ Stop Visualization Task """
        self.running = False
        

