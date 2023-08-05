#!/usr/bin/env python

# Try to use setuptools from http://peak.telecommunity.com/DevCenter/setuptools
try:
    from setuptools import setup
except:
    try:
        from ez_setup import use_setuptools
        use_setuptools()
    except:
        from distutils.core import setup

setup(
    author='Drew Smathers',
    author_email='drew.smathers@gmail.com',
    name='xix-utils',
    version='0.2.2',
    install_requires=['zope.interface>=3.2.0','lxml>=1.1.2'],
    scripts=['scripts/xix-coverage.py'],
    description="""Xix Utils is a drillbit library independent (mostly) of
    any framework ... simple reusable tools for python.""",
    long_description="""Xix utils began as an attemp at designing a 
    templating / content-publshing framework which is now only those remains - xix.utils.
    xix_utils is simply "yet more batteries for python."  Generalized 
    concepts and resulting POCs abstracted from other projects become modules under 
    xix.utils. Known unstable modules should signal warnings at runtime.

    Tested on Python 2.4 and 2.5.
    
    Subversion trunk:
   
        svn co http://svn.xix.python-hosting.com/trunk Xix

    Installation:

        python setup.py install

    Note to Developers: Please run unit tests and provide feedback.  To run suite:

        python runtests.py
    """,
    license='MIT License',
    url='http://xix.python-hosting.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Environment :: Console',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'],
    packages=['xix', 'xix.utils', 'xix.utils.comp', 'xix.utils.tools'],
    package_dir={'xix': 'xix'},
    package_data={'xix': ['*.cfg', 'data/*.css', 'data/*.xsl', 'data/*.py']},
    )
