#!/bin/sh

export PYTHONPATH=.:$PYTHONPATH

# DOCTESTS ####################################################################

echo
echo
python3 -m doctest ./pywi/io/images.py

# UNITTESTS ###################################################################

echo
echo
echo "TEST_BENCHMARK_ASSESS"
./tests/test_benchmark_assess.py

echo
echo
echo "TEST_KILL_ISOLATED_PIXELS"
./tests/test_denoising_kill_isolated_pixels.py

echo
echo
echo "TEST_IO_IMAGES"
./tests/test_io_images.py
