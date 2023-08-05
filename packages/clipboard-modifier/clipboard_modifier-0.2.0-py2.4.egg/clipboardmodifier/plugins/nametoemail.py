#!/usr/bin/env python
# -*- encoding: latin1 -*-
#
# Copyright 2007 Scott Kirkwood

from _plugin import ClipboardPlugin, TestPlugin
import re
import find_people

def create_plugin():
  return NameToEmail()

class NameToEmail(ClipboardPlugin):
  def __init__(self):
    ClipboardPlugin.__init__(self)
    
  def name(self):
    return 'Name to e-mail'
    
  def description(self):
    return "Convert a person's name into an email"
    
  def convert(self, text):
    """Convert persons name to email
      
    Returns: Text
    """
    
    if len(text) == 0:
      return self._ret_result('Nothing to do', False)
    
    names = find_people.scanTextForNames(text)
    
    message = "Found %d names" % (len(names))
    ret = []
    for name in names:
      ret.append("%s <%s.google.com>" % (name, find_people.momaForName(name)))

    return self._ret_result(message, True, '\n+'.join(ret))

class TestToJava(TestPlugin):
  def setUp(self):
    self.instance = NameToEmail()
  
    
    
if __name__ == "__main__":
  import unittest
  unittest.main()
