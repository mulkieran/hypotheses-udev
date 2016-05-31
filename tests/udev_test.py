# -*- coding: utf-8 -*-
# Copyright (C) 2016 Anne Mulhern <amulhern@redhat.com>

# This library is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation; either version 2.1 of the License, or (at your
# option) any later version.

# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

"""
Test properties of udev.

.. moduleauthor::  mulhern <amulhern@redhat.com>
"""

import os

from hypothesis import given
from hypothesis import settings
from hypothesis import strategies

import pytest

import pyprocdev

from pyudev import Context

_CONTEXT = Context()
_DEVICES = _CONTEXT.list_devices()

_CONTEXT_STRATEGY = strategies.just(_CONTEXT)

_PROCDEV = pyprocdev.ProcDev()


class TestDrivers(object):
    """
    Test properties of drivers.
    """
    # pylint: disable=too-few-public-methods

    _devices = [d for d in _DEVICES if d.subsystem in ('block', 'char')]
    @pytest.mark.skipif(len(_devices) == 0, reason='no special devices')
    @given(strategies.sampled_from(_devices))
    @settings(max_examples=50, min_satisfying_examples=1)
    def test_driver_char_block(self, device):
        """
        If a device is character or block then libudev supplies no driver.

        If the device has a parent, then the parent's driver is the same
        as is obtained from the device's major number and /proc/devices.
        If the device has no parent, then the device may still have a driver
        in /proc/devices.
        """
        assert device.driver is None

        subsystem = pyprocdev.DeviceTypes.BLOCK if \
           device.subsystem == 'block' else pyprocdev.DeviceTypes.CHARACTER
        major = os.major(device.device_number)

        assert major in _PROCDEV.majors(subsystem)

        parent = device.parent
        if parent is not None:
            assert parent.driver == _PROCDEV.get_driver(subsystem, major)
