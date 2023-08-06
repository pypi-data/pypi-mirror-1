#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import os
import subprocess

from minihallib.HALManager import HALManager
from minihallib.HALPlugin import make_hal_device


log = logging.getLogger(__name__)

def get_logfile_from_burner_name(burner_name, dev_path, err=False):
    """Return log file from burner name and it's location"""
    dev_path_base = os.path.basename(dev_path)
    logfilename_list = [burner_name.replace(' ', '_'), dev_path_base, 'log']
    if err:
        logfilename_list.insert(-1, 'err')
    return '.'.join(logfilename_list)

def open_file_in_native_app(filepath):
    """Opens file/url with default application for mimetype/extension"""
    log.debug("Opening file: %s", filepath)
    if os.name == 'mac':
        subprocess.call(('open', filepath))
    elif os.name == 'nt':
        subprocess.call(('start', filepath))
    elif os.name == 'posix':
        subprocess.call(('xdg-open', filepath))

def disc_type_to_media_type(string):
    """Converts volume.disc.type value to storage.cdrom property
    and returns True if media is writtable
    """ 
    if 'rom' in string:
        return False
    return string.replace('_', '')

def get_hal_devices(capability='storage.cdrom'):
    """Get all HALDevices by capability"""
    # TODO: this actually gets all cdroms, not only burners
    m = HALManager()
    return [make_hal_device(m.bus, udi) for udi in \
        m.hal_manager.FindDeviceByCapability(capability)]
