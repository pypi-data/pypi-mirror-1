#!/usr/bin/env python

from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

# Note to self:
# python setup.py sdist --formats=zip
# To create the zip file

# python setup.py --command-packages=setuptools.command bdist_egg
# To create the egg file

# python setup.py register
# to register with PyPI
# 

# create an egg and upload it
# setup.py register sdist bdist_egg upload

# Set this on command line
# DISTUTILS_DEBUG=true
# 
setup(
    name='clipboard-modifier',
    version='0.2.0',
    description="Change your clipboard text in a variety of ways",
    long_description=
"""A flexible system to modify the text in a clipboard in a variety of ways.
Out of the box we have:
  * Copy a spreadsheet and change the clipboard so that it can be pasted into a
  * wiki, with vertical bars (|) instead of tabs.  Modify your multi-line clipboard text so that it can be pasted into Java or Python as strings.
  * Modify an URL in the clipboard pointing to Amazon so that it has your Associate ID in it. 
  * Run a shell command piping the clipboard to it and retrieving the output from it.
  * Force a clibpboard to text (removing formatting, etc.).
  * Convert a complicated url into it's python equivalent, using urlencode.
  * And many more...

It uses wxPython and when you bring it's window to the front it modifies
the clipboard with the currently selected utility.
""",
    author='Scott Kirkwood',
    author_email='scottakirkwood@gmail.com',
    url='http://code.google.com/p/clipboard-modifier/',
    download_url='http://clipboard-modifier.googlecode.com/files/clipboard-modifier-0.2.0.zip',
    keywords=['clipboard', 'utility', 'wxPython', 'Python'],
    license='GNU GPL',
    platforms=['POSIX', 'Windows'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ], 
    packages=['clipboardmodifier', 'clipboardmodifier/plugins'],
    scripts=['scripts/clipboard-modifier'],
    zip_safe=False,
)
