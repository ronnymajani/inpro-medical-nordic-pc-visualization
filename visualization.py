#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  5 20:37:21 2018

@author: ronnymajani
"""

import threading
import matplotlib.cm
import matplotlib.pyplot as plt
import time, datetime
import os
import csv


class VisualizationWindow(threading.Thread):
    # How many seconds to wait between windows updates
    REFRESH_SPEED = 0.25
    OUTPUT_DIR = "logs"
    
    def __init__(self, nordic_driver):
        threading.Thread.__init__(self)
        self.daemon = True
        self.running = True
        self.pressure_values = []
        self.nordicDriver = nordic_driver
        self._setup_data_saving()
        self._setup_plot()
        
    def _setup_data_saving(self):
        # if the output directory doesn't exits, create it
        if not os.path.exists(VisualizationWindow.OUTPUT_DIR):
            os.mkdir(VisualizationWindow.OUTPUT_DIR)
        self.filename = datetime.datetime.fromtimestamp(time.time()).strftime('%Y.%m.%d_%H.%M.%S_log') + ".csv"
        self.filename = os.path.join(VisualizationWindow.OUTPUT_DIR, self.filename)
        self.csv_file = open(self.filename, "w")
        self.csv_writer = csv.writer(self.csv_file)
    
    def _setup_plot(self):
        self.fig = plt.figure()
        self.fig.canvas.mpl_connect('close_event', self._handle_close)
        self.ax = self.fig.add_subplot(111)
        self.im = self.ax.imshow(self._get_values(), cmap=matplotlib.cm.YlOrRd)
        plt.show()

    def _log_values(self, vals):
        if self.csv_writer is not None:
            # flatten the matrix into a 1D list
            vals = [v for row in vals for v in row]
#            print(vals)
            self.csv_writer.writerow(vals)
            self.csv_file.flush()
        
    def _get_values(self):
        vals = self.nordicDriver.get_all_pressure_sensor_values()
        vals = [vals[0][:2], vals[0][2:]]
        return vals
        
    def plot(self):
        vals = self._get_values()
        print(vals)
        self.im.set_array(vals)
        self._log_values(vals)
        self.fig.canvas.draw()
        
    def run(self):
        """
        Display the simulation using matplotlib, using blit for speed
        """
        while self.running:
            self.plot()
            time.sleep(VisualizationWindow.REFRESH_SPEED)
        self.stop()
        
    def _handle_close(self, evt):
        self.stop()
        
    def stop(self):
        """ Stop Visualization Task """
        print('STOPPING')
        self.running = False
        plt.close(self.fig)
        self.csv_writer = None
        self.csv_file.close()
        self.nordicDriver.stop()
        

