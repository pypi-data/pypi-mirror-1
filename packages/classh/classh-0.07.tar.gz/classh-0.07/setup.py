#!/usr/bin/env python
from distutils.core import setup

setup(
    name='classh',
    version='0.07',
    author='James T. Dennis',
    author_email='answrguy@gmail.com',
    license='PSF',
    url='http://bitbucket.org/jimd/classh/',
    py_modules=['classh'],
    scripts   =['classh'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Python Software Foundation License",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Topic :: System :: Clustering",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities"
    ],
    description="Cluster Administrators' ssh Wrapper",
    long_description='''

    classh is yet another wrapper around ssh for running jobs on multiple 
    targets.  It can support tens of thousands of targets (tested on over 
    25,000 at once) and runs a configurable number of jobs concurrently. 
    It separately gathers results, output and error messages, displaying 
    summary/status information it comes in (asynchronously) and more 
    detailed data after all jobs have completed.

    classh provides an SSHJobMan class which can be imported into your own
    Python code and easily used to handle specialized display or other 
    disposition of results.  (For example the names of all hosts on which
    the job succeeded can be fed into another process while various failure
    modes can be tested and fed into other processes).

    '''
    )
 

