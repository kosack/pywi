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
Denoise FITS and PNG images with the tailcut algorithm.

Example usages:
  ./denoising_with_tailcut.py -h
  ./denoising_with_tailcut.py -T 0.5 -t 0.1 ./test.fits
  ./denoising_with_tailcut.py -T 0.5 -t 0.1 ./test.fits
  ipython3 -- ./denoising_with_tailcut.py -t 0.0001 -s ./test.fits

This snippet requires Numpy, Matplotlib and PIL/Pillow Python libraries.
"""

import argparse
import datetime
import json
import os
import numpy as np

from datapipe.benchmark import assess
from datapipe.io import images

def tailcut(img, high_threshold=0, low_threshold=0, base_file_path="tailcut", verbose=False):

    # COMPUTE MASKS #######################################

    # TODO
#    img_sigma = np.std(img)
    max_value = np.max(img)

    # TODO
#    high_mask = (img > (img_sigma * high_threshold)  
#    low_mask = (img > (img_sigma * low_threshold)  
    high_mask = (img > (max_value * high_threshold))
    low_mask =  (img > (max_value * low_threshold))

#    images.plot(high_mask, title="High mask")
#    images.plot(low_mask, title="Low mask")

    # MERGE MASKS #########################################

    # Dilate the high_mask to create a mask of neighbors.
    # For instance, if high_mask is equals to:
    #    [[0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 1, 0, 0, 0, 1, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0]]
    # the dilated version of high_mask is equals to:
    #    [[0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 1, 1, 1, 0, 1, 1, 1, 0],
    #     [0, 1, 1, 1, 0, 1, 1, 1, 0],
    #     [0, 1, 1, 1, 0, 1, 1, 1, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0]]

    high_mask_dilated = np.zeros(high_mask.shape, dtype=np.bool)
    high_mask_dilated[:] = high_mask

    high_mask_dilated[:-1,:] |= high_mask[1:,:]    # shift up
    high_mask_dilated[1:,:]  |= high_mask[:-1,:]   # shift down

    high_mask_dilated[:,:-1] |= high_mask_dilated[:,1:]   # shift left
    high_mask_dilated[:,1:]  |= high_mask_dilated[:,:-1]  # shift right

    # Merge high_mask_dilated and low_mask (using a logical AND)

    final_mask = high_mask_dilated & low_mask

    # PLOT MASK ###########################################

    if verbose:
        images.plot(final_mask, title="Tailcut mask")
        images.mpl_save(final_mask,
                        "{}_tailcut_mask.pdf".format(base_file_path),
                        title="Tailcut mask")

    # APPLY MASK ##########################################

    filtered_img = img * final_mask

    return filtered_img


def main():

    # PARSE OPTIONS ###########################################################

    parser = argparse.ArgumentParser(description="Denoise FITS and PNG images with the tailcut algorithm.")

    parser.add_argument("--benchmark", "-b", type=int, default=0, metavar="INTEGER", 
                        help="The benchmark method to use to assess the algorithm for the"
                             "given images (0: no benchmark, 1: normalized mean pixel value"
                             "difference, 2: Hillas parameters difference")
    parser.add_argument("--high_threshold", "-T", type=float, default=0, metavar="FLOAT", 
                        help="The 'high' threshold value (between 0 and 1)")
    parser.add_argument("--low_threshold", "-t", type=float, default=0, metavar="FLOAT", 
                        help="The 'low' threshold value (between 0 and 1)")
    parser.add_argument("--hdu", "-H", type=int, default=0, metavar="INTEGER", 
                        help="The index of the HDU image to use for FITS input files")
    parser.add_argument("fileargs", nargs="+", metavar="FILE",
                        help="The files image to process (FITS)")
    args = parser.parse_args()

    benchmark_method = args.benchmark
    high_threshold = args.high_threshold
    low_threshold = args.low_threshold
    hdu_index = args.hdu
    input_file_path_list = args.fileargs

    if benchmark_method > 0:
        score_list = []

    for input_file_path in input_file_path_list:

        # READ THE INPUT FILE ##################################################

        input_img = images.load(input_file_path, hdu_index)

        if input_img.ndim != 2:
            raise Exception("Unexpected error: the input FITS file should contain a 2D array.")


        # TAILCUT FILTER ######################################################

        base_file_path = os.path.basename(input_file_path)
        base_file_path = os.path.splitext(base_file_path)[0]

        filtered_img = tailcut(input_img, high_threshold, low_threshold)

        if benchmark_method == 1:
            reference_img = images.load(input_file_path, 1)
            score = assess.assess_image_cleaning_meth1(input_img, filtered_img, reference_img)
            score_list.append(score)
        elif benchmark_method == 2:
            reference_img = images.load(input_file_path, 1)
            score = assess.assess_image_cleaning_meth2(input_img, filtered_img, reference_img)
            score_list.append(score)
        else:
            images.plot(input_img, title="Original image")
            images.plot(filtered_img, title="Denoised image")
            images.mpl_save(filtered_img,
                            "{}_tailcut_denoised.pdf".format(base_file_path),
                            title="Denoised image (Tailcut)")

    if benchmark_method > 0:
        print(score_list)

        output_dict = {}
        output_dict["algo"] = __file__
        output_dict["algo_params"] = {"high_threshold": high_threshold, "low_threshold": low_threshold}
        output_dict["benchmark_method"] = benchmark_method
        output_dict["date_time"] = str(datetime.datetime.now())
        output_dict["hdu_index"] = hdu_index
        output_dict["system"] = " ".join(os.uname())
        output_dict["input_file_path_list"] = input_file_path_list
        output_dict["score_list"] = score_list

        with open("score_tailcut.json", "w") as fd:
            #json.dump(data, fd)                                 # no pretty print
            json.dump(output_dict, fd, sort_keys=True, indent=4)  # pretty print format


if __name__ == "__main__":
    main()

