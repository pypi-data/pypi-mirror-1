#!/usr/bin/env python

# Try to use setuptools from http://peak.telecommunity.com/DevCenter/setuptools
try:
    from setuptools import setup
except:
    try:
        import ez_setup
        ez_setup.use_setuptools()
        from setuptools import setup
    except: # so everybody's happy
        from distutil.core import setup

setup(
    author='Drew Smathers',
    author_email='drew.smathers@gmail.com',
    name='xix_utils',
    version='0.1.1',
    description='',
    url='http://www.cc.gatech.edu/ugrads/d/dpaces/',
    packages=['xix', 'xix.utils', 'xix.utils.comp'],
    package_dir={'xix': 'xix'},
    package_data={'xix': ['*.cfg']},
    )
