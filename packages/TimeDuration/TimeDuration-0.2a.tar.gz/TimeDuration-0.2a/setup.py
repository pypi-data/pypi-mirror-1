#!/usr/bin/python
from distutils.sysconfig import get_python_lib
from distutils.core import setup
from setuptools import setup, find_packages
from os.path import isfile, join
import glob
import os

#if isfile("MANIFEST"):
#    os.unlink("MANIFEST")

# Get PYTHONLIB with no prefix so --prefix installs work.
PYTHONLIB = join(get_python_lib(standard_lib=1, prefix=''), 'site-packages')

setup(name="TimeDuration",
      version = "0.2a",
      description = "TimeDuration is a module that deals with stopwatch time rather than wallclock time",
      author = "Andrew Lee",
      author_email = "fiacre.patrick@gmail.com",
      url = "http://statz.com/libs-TimeDuration",
      license = "GPL License",
      long_description =
"""\
The TimeDuration module provides a Pure Python interface to the creation, manipulation and comparison
of time duration string.  E.g. if 3:21:45.3 and 3:22:30.1 represent stopwatch times, I don't want
to represent or store them as datetime objects but I do want to be able to compare them and
do simple calculations on such string such as find the average of a tuple of TimeDuration objects.
I'd also like to be able to say something like "3 weeks, 5 days 12 hours and 32 minutes" and be
able to convert that to minutes, seconds or hours and be able to convert strings that look like
durations of time to a normalized format.
""",
      packages = ['TimeDuration'],
      install_requires=['setuptools'],
      scripts=['example.py', 'test.py']
      )

