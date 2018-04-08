inpro-medical-nordic-pc-visualization
-------

This code uses bluepy and matplotlib
Bluepy: https://github.com/IanHarvey/bluepy



### Usage:
Run the file InPro.py with python3


### Prerequisites:
- Rasberry Pi3b
- python3
- matplotlib
- [bluepy](https://github.com/IanHarvey/bluepy)


### Rasberry Pi Setup:
First Install these libraries:
```bash
$ sudo apt install python3-pip libglib2.0-dev
```
    
Install matplotlib using pip3
```bash
$ pip3 install matplotlib
```

Install bluepy library using pip3
```bash
$ pip3 install bluepy
```

To Run this app without root permissions, run this command 
```bash
$ sudo setcap 'cap_net_raw,cap_net_admin+eip' /PATH/TO/bluepy/bluepy-helper
```

to find out where bluepy was installed, type:
```bash
$ pip3 show bluepy
```

on this device bluepy-helper was installed in:
*/home/pi/.local/lib/python3.5/site-packages/bluepy/bluepy-helper*
so we set its permissions like this:
```bash
$ sudo setcap 'cap_net_raw,cap_net_admin+eip' /home/pi/.local/lib/python3.5/site-packages/bluepy/bluepy-helper
```


### Usefule links:
- For Plotting:
  https://stackoverflow.com/questions/25385216/python-real-time-varying-heat-map-plotting
- For BluePy Permissions Problem:
  https://github.com/IanHarvey/bluepy/issues/190