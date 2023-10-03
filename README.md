```
Set and update information on the zoom75 LCD kit on Linux

positional arguments:
  {keep-alive,oneshot}  Subcommand help
    keep-alive          Keep the tool running to continuously update temperature readings
    oneshot             Update a single value once

options:
  -h, --help            show this help message and exit

```

## Configuration:

Either run as root or configure a udev rule (see here https://github.com/trezor/cython-hidapi#udev-rules)

## Example usage:
```
zoom75.py keep-alive --cputemp-module k10temp --cputemp-label Tctl --gputemp-module amdgpu --gputemp-label junction
```

## Requirements:
- psutil
- hidapi

## TODO:
- Weather
- FAN speed
- Net speed
