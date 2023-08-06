"""
Python API for 'loop' Linux module.

This module allows Python program to mount file as loop device.


Some parts of this code based on util-linux-ng project (http://userweb.kernel.org/~kzak/util-linux-ng/)

Copyright (C) 2008 Sergey Kirillov, Rainboo Software
 
"""

import os
import re
import stat
import _losetup

DEV_LOOP_PATH = "/dev/loop/"
DEV_PATH = "/dev/"
LOOPMAJOR = 7

class NoLoopSupport(Exception):
    """Loop support is not detected for running system""" 
    pass
class LoopNotFoundError(Exception):
    """Specified loop device is not found""" 
    pass

class NotLoopError(Exception):
    """Specified device is not a loop device""" 
    pass

def is_loop(filename):
    """Check whether specified filename is a loop device"""
    st = os.stat(filename)
    return stat.S_ISBLK(st.st_mode) and (_major(st.st_rdev) == LOOPMAJOR)

def is_used(device):
    """Check whether specified loop device is mounted"""
    if not is_loop(device):
        raise NoyLoopError("Specified device is not a loop device")
    return bool(_losetup.is_used(device))

def mount(filename):
    """
    Mount specified image to first unused loop device.
    If all devices are busy raise LoopNotFoundError
    """
    
    dev = find_unused_loop_device()
    _losetup.mount(dev, filename)
    return dev
    
def unmount(dev):
    """
    Unmount specified device. 
    """ 
    if not is_loop(dev):
        raise NotLoopError("Specified device is not a loop device")
    _losetup.unmount(dev)
                  
def find_unused_loop_device():
    """Find first unused loop device"""
    global _loop_devices
    for num, path in _loop_devices.iteritems():
        if _losetup.is_used(path) == 0:
            return path
        
    raise LoopNotFound("Unable to find free loop device")

def _major(value):
    return (value >> 8) & 0xff;

def _minor(value):
    return value & 0xff;

def _make_device_path(num):
    global _has_dev_loop
    
    if _has_dev_loop:
        return os.path.join(DEV_LOOP_PATH, num)
    else:
        return os.path.join(DEV_PATH, "loop%s" % num)
    
# Initialize loop devices list
_loop_devices = {}


if os.path.isdir(DEV_LOOP_PATH):
    devs = os.listdir(DEV_LOOP_PATH)
    for num in devs:
        path = os.path.join(DEV_LOOP_PATH, num)
        if is_loop(path): 
            _loop_devices[num] = path
else:
    _loop_dev_re = re.compile("^loop(\d+)$")
    for d in os.listdir(DEV_PATH):
        m = _loop_dev_re.match(d)
        if not m:
            continue
        num = m.group(1)
        path = os.path.join(DEV_PATH, d)
        if is_loop(path): 
            _loop_devices[num] = path
    