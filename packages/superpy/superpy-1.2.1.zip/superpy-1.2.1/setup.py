"""Setup script for installing/distribuging package.
"""

from superpyMisc.ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages
setup(
    name = "superpy",
    #version = "1.1.0.dev" would be a pre-release tag of dev,
    #version = "1.1.0-p1" would be a post-release tag of -p1,    
    version = "1.2.1",
    packages = find_packages(),
    package_dir = {'superpy.demos.pyfog' : 'superpy/demos/pyfog'},
    package_data={'superpy.demos.pyfog' : ['defaults/*.txt']},
    test_suite = 'superpyTesting.unitTestsFromSrc.MakeMainSuperpyDoctest',
    scripts = ['superpy/scripts/%s' %s for s in [
    'CleanOldTasks.py', 'ShowServer.py', 'Spawn.py', 'SpawnAsService.py',
    'StartSuperWatch.py']] + ['superpy/demos/pyfog/fogGUI.py'],
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
Superpy distributes python programs across a cluster of machines or across multiple processors on a single machine. This is a coarse-grained form of parallelism in the sense that remote tasks generally run in separate processes and do not share memory with the caller.

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

The ultimate vision for superpy is that you:
 1. Install it as an always on service on a cloud of machines
 1. Use the superpy scheduler to easily send python jobs into the cloud as needed
 1. Use the {{{SuperWatch}}} GUI to track progress, kill tasks, etc.

For smaller deployments, you can use superpy to take advantage of multiple processors on a single machine or multiple machines to maximize computing power.

What makes superpy different than the many other excellent parallel
processing packages already available for python? The superpy package
is designed to allow sending jobs across a large number of machines
(both Windows and LINUX). This requires the ability to monitor, debug,
and otherwise get information about the status of jobs.

While superpy is currently used in production for a number of different purposes, there are still many features we want to add. For a list of future plans and opportunities to help out or add to the discussion, please visit http://code.google.com/p/superpy/wiki/HelpImproveSuperpy.

For a quick example of some of the the things superpy can do, check out http://code.google.com/p/superpy/wiki/Demos or in particular the demo application PyFog at http://code.google.com/p/superpy/wiki/PyFog.

To install, you can use easy_install to try superpy via "easy_install superpy" or download a python egg from http://code.google.com/p/superpy/downloads. Of course, you will need python installed and if you are using windows, you should also install the python windows tools from http://sourceforge.net/projects/pywin32/files. See http://code.google.com/p/superpy/wiki/InstallFAQ if you have more questions about installation.
"""
    
    # could also include long_description, download_url, classifiers, etc.
)
