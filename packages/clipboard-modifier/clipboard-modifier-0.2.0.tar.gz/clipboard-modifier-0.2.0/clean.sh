#!/bin/sh
sudo python setup.py clean
sudo rm -r /usr/lib/python2.4/site-packages/clipboard_modifier-*-py2.?.egg
sudo rm /usr/bin/clipboard-modifier
rm -r build
rm -r dist
rm -r clipboard_modifier.egg-info
rm MANIFEST
