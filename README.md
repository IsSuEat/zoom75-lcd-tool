# zoom75-lcd-tool
Display hardware information on the zoom75 LCD kit using Linux

Currently supported features:
- Synchronize time to keyboard 
- CPU temperature
- GPU temperature

## Configuration:

Either run as root or configure a udev rule (see here https://github.com/trezor/cython-hidapi#udev-rules).
The keyboard needs to be connected over USB.

## Example usage:
Find available sensors
```
./zoom75.py -p
```
Configure the correct module for CPU and GPU temperature and keep sending the information to the LCD. Data is sent every second.
```
./zoom75.py keep-alive --cputemp-module k10temp --cputemp-label Tctl --gputemp-module amdgpu --gputemp-label junction
```

## Requirements:
- psutil
- hidapi

## TODO:
- Weather
- FAN speed
- Net speed
