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

        However, its driver can be obtained from /proc/devices.

        There is no reliable relationship between the driver in /proc/devices
        and the driver associated with any of the devices ancestor nodes.
        """
        assert device.driver is None

        subsystem = pyprocdev.DeviceTypes.BLOCK if \
           device.subsystem == 'block' else pyprocdev.DeviceTypes.CHARACTER
        major = os.major(device.device_number)

        assert major in _PROCDEV.majors(subsystem)

        assert _PROCDEV.get_driver(subsystem, major) is not None


class TestSCSI(object):
    """
    Test properties of SCSI devices.
    """
    # pylint: disable=too-few-public-methods

    def test_one_disk_child(self):
        """
        Test that every device with type scsi_device has only one disk
        descendant.
        """
        scsi_devices = _CONTEXT.list_devices().match_property(
           'DEVTYPE',
           'scsi_device'
        )

        def func(dev):
            """
            Returns an enumerate for all child block disk devices of dev.

            :param Device dev: the parent device
            :rtype: Enumerator
            :returns: an enumerator for this subset of devices.
            """
            return _CONTEXT.list_devices(
               subsystem='block',
               DEVTYPE='disk',
               parent=dev
            )

        assert all(len(list(func(d))) in (0, 1) for d in scsi_devices)
