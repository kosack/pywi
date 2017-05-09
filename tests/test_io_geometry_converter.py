#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2016 Jérémie DECOCK (http://www.jdhp.org)

# This script is provided under the terms and conditions of the MIT license:
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
This module contains unit tests for the "io.geometry_converter" module.
"""

import ctapipe
from ctapipe.io.hessio import hessio_event_source
import pyhessio

from datapipe.io import geometry_converter

# Old version
from ctapipe.io import camera

# New version
#from ctapipe.instrument import camera

import numpy as np

import unittest

class TestGeometryConverter(unittest.TestCase):
    """
    Contains unit tests for the "io.geometry_converter" module.
    """

    # Test the "geom_to_json_dict" and "json_dict_to_geom" functions ################################

    def test_geom_json_dict_ex1(self):

        simtel_file_path = "/Users/jdecock/data/astri_mini_array/proton/run10001.simtel.gz"
        tel_id = 1

        source = hessio_event_source(simtel_file_path, allowed_tels=[tel_id])

        for ev in source:
            event = ev

        # Get the geometry object with the "guess()" method

        pix_x = event.inst.pixel_pos[tel_id][0]
        pix_y = event.inst.pixel_pos[tel_id][1]
        optical_foclen = event.inst.optical_foclen[tel_id]

        geom = camera.CameraGeometry.guess(pix_x, pix_y, optical_foclen)

        # Convert and write the geom object

        json_dict = geometry_converter.geom_to_json_dict(geom)
        geom2 = geometry_converter.json_dict_to_geom(json_dict)

        # Check whether the input image has changed

        self.assertEqual(geom2.cam_id, geom.cam_id)
        np.testing.assert_array_equal(geom2.pix_id,         geom.pix_id)
        np.testing.assert_array_equal(geom2.pix_x.value,    geom.pix_x.value)
        np.testing.assert_array_equal(geom2.pix_y.value,    geom.pix_y.value)
        np.testing.assert_array_equal(geom2.pix_area.value, geom.pix_area.value)
        self.assertEqual(geom2.neighbors, geom.neighbors)
        self.assertEqual(geom2.pix_type,  geom.pix_type)


    # Test the "geom_to_json_file" and "json_file_to_geom" functions ################################

    def test_geom_json_file_ex1(self):

        simtel_file_path = "/Users/jdecock/data/astri_mini_array/proton/run10001.simtel.gz"
        tel_id = 1
        output_json_file = "/tmp/astri.geom.json"

        source = hessio_event_source(simtel_file_path, allowed_tels=[tel_id])

        for ev in source:
            event = ev

        # Get the geometry object with the "guess()" method

        pix_x = event.inst.pixel_pos[tel_id][0]
        pix_y = event.inst.pixel_pos[tel_id][1]
        optical_foclen = event.inst.optical_foclen[tel_id]

        geom = camera.CameraGeometry.guess(pix_x, pix_y, optical_foclen)

        # Convert and write the geom object

        geometry_converter.geom_to_json_file(geom, output_json_file)
        geom2 = geometry_converter.json_file_to_geom(output_json_file)

        # Check whether the input image has changed

        self.assertEqual(geom2.cam_id, geom.cam_id)
        np.testing.assert_array_equal(geom2.pix_id,         geom.pix_id)
        np.testing.assert_array_equal(geom2.pix_x.value,    geom.pix_x.value)
        np.testing.assert_array_equal(geom2.pix_y.value,    geom.pix_y.value)
        np.testing.assert_array_equal(geom2.pix_area.value, geom.pix_area.value)
        self.assertEqual(geom2.neighbors, geom.neighbors)
        self.assertEqual(geom2.pix_type,  geom.pix_type)
    

if __name__ == '__main__':
    unittest.main()
