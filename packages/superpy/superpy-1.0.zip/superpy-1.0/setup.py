"""Setup script for installing/distribuging package.
"""

from misc.ez_setup import use_setuptools
use_setuptools()


from setuptools import setup, find_packages
setup(
    name = "superpy",
    version = "1.0",
    packages = find_packages(),
    scripts = ['superpy/scripts/%s' %s for s in [
    'CleanOldTasks.py', 'ShowServer.py', 'Spawn.py', 'SpawnAsService.py',
    'StartSuperWatch.py']],
    # metadata for upload to PyPI
    author = "Emin Martinian, Li Lee, Henry Xu",
    author_email = "emin.martinian@gmail.com",
    description = "Parallel processing tools for supercomputing with python.",
    license = "MIT",
    keywords = "parallel, super, process",
    install_requires = ['Pmw'],
    dependency_links = [
        "http://superpy.googlecode.com/files/Pmw-1.3.2-py2.5.egg"
    ],
    provides = ['superpy'],
    url = "http://code.google.com/p/superpy/",   # project home page
    long_description = """
Superpy distributes python programs across a cluster of machines or
across multiple processors on a single machine. This is a
coarse-grained form of parallelism in the sense that remote tasks
generally run in separate processes and do not share memory with the
caller.

Key features of superpy include:

    * Send tasks to remote servers or to same machine via XML RPC call
    * GUI to launch, monitor, and kill remote tasks
    * GUI can automatically launch tasks every day, hour, etc.
    * Works on the Microsoft Windows operating system
    * Can run as a windows service
    * Jobs submitted to windows can run as submitting user or as service user
    * Inputs/outputs are python objects via python pickle
    * Pure python implementation
    * Supports simple load-balancing to send tasks to best servers 

What makes superpy different than the many other excellent parallel
processing packages already available for python? The superpy package
is designed to allow sending jobs across a large number of machines
(both Windows and LINUX). This requires the ability to monitor, debug,
and otherwise get information about the status of jobs.
"""
    
    # could also include long_description, download_url, classifiers, etc.
)
