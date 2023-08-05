#!/usr/bin/env python
# -*- encoding: latin1 -*-
#
# Copyright 2007 Scott Kirkwood
import wx
import subprocess
import optparse
import re

"""
Clipboard modifier is a wxPython app with a simple purpose.  
When brought to the front, it'll modify the clipboard using a routine that you supply.
An example of this is talking the string "Hello" and putting it in quotes '"Hello'", which
becomes more interesting when you have several lines and some quotes within.
The program is exensible, any .py files found in the plugins subdirectory will get
loaded automatically. For each plugin we need a module level function called 
"""
class ClipboardModifierApp(wx.App):
  def init_vars(self):
    self.methods = []
    self.grabbedClipboard = ''
    self.sendClipboard = ''
    self.beforeTemplate = "From: %0d bytes"
    self.afterTemplate = "To: %0d bytes"
    self.unchanged_after = "Unchanged"
    
  def OnInit(self):
    self.init_vars()
    dialog = wx.Frame(None, -1, "Clipboard Modifier")
    dialog.Show(True)
    self.SetTopWindow(dialog)
    self.FindModules()
    
    self.SetupControls(dialog)
    return True

  def SetupControls(self, dialog):
    vsizer = wx.BoxSizer(wx.VERTICAL)
    
    hsizer = wx.BoxSizer(wx.HORIZONTAL)
    
    self.BeforeSize = wx.TextCtrl(dialog, -1, self.beforeTemplate % (0), size=(-1,20), style=wx.TE_READONLY)
    self.BeforeTooltip = wx.ToolTip("")
    self.BeforeTooltip.SetDelay(1)
    self.BeforeSize.SetToolTip(self.BeforeTooltip)
    hsizer.Add(self.BeforeSize, 1, wx.ALL, 5)
    
    self.AfterSize = wx.TextCtrl(dialog, -1, self.afterTemplate % (0), size=(-1, 20), style=wx.TE_READONLY)
    self.AfterTooltip = wx.ToolTip("")
    self.AfterTooltip.SetDelay(1)
    self.AfterSize.SetToolTip(self.AfterTooltip)
    hsizer.Add(self.AfterSize, 1, wx.ALL, 5)
    
    vsizer.Add(hsizer, 0, wx.ALL | wx.EXPAND, 5)
    
    
    vRadioSizer = wx.StaticBoxSizer(wx.StaticBox(dialog, -1, "Choose the Plugin"), wx.VERTICAL)
    
    # First one has this style, the remainder have a style of 0
    curStyle = wx.RB_GROUP 
    for class_instance in self.ClipboardMethods:
      title = class_instance.name()
      radio = wx.RadioButton(dialog, -1, title, style=curStyle)
      tooltip = class_instance.description()
      radio.SetToolTip(wx.ToolTip(tooltip))
      vRadioSizer.Add(radio, 0, wx.ALL, 5)
      self.Bind(wx.EVT_RADIOBUTTON, self.SetClassToUse, id=radio.GetId())
      self.methods.append((radio, class_instance))
      curStyle = 0

    vsizer.Add(vRadioSizer, 0, wx.ALL | wx.EXPAND, 5)
    
    self.ClassToUse = self.methods[0][-1]
    wx.EVT_ACTIVATE(self, self.OnActivate)
    dialog.SetSizer(vsizer)
    self.sb = dialog.CreateStatusBar()

  def SetClassToUse(self, event):
    """ Scan through the radio buttons to figure out which class is active 
    Also forces a convert with the new class.
    """
    for radio, class_instance in self.methods:
      if radio.GetValue() == True:
        self.ClassToUse = class_instance
        self.ModifyText()
        return
    
  def GrabClipboard(self):
    """ Grab the clipboard data """
    if wx.TheClipboard.Open():
      data = wx.TextDataObject()
      success = wx.TheClipboard.GetData(data)
      wx.TheClipboard.Close()
      self.grabbedClipboard = data.GetText()
    
    return self.grabbedClipboard
  
  def UpdateClipboard(self, text):
    """ Overwrite the clipboard data """
    if wx.TheClipboard.Open():
      data = wx.TextDataObject(text)
      wx.TheClipboard.SetData(data)
      return True
    return False
  
  def RunFunction(self, text, func):
    """ Run the function """
    results = func.convert(text)
    return func.message(), results

  def ModifyText(self):
    message = 'Ok'
    text = self.GrabClipboard()
    if len(text) > 0:
      message, self.sendClipboard = self.RunFunction(self.grabbedClipboard, self.ClassToUse)
    else:
      message = "No clipboard data"
    
    bytes_before = len(self.grabbedClipboard)
    bytes_after = len(self.sendClipboard)
    beforeMessage = self.beforeTemplate % (bytes_before)
    self.BeforeSize.SetValue(beforeMessage)
    afterMessage = ''
    if bytes_after == 0:
      afterMessage = self.unchanged_after
      self.AfterTooltip.SetTip(self.TrimTip(afterMessage))
    else:
      afterMessage = self.afterTemplate % (bytes_after)
      self.AfterTooltip.SetTip(self.TrimTip(self.sendClipboard))
    self.AfterSize.SetValue(afterMessage)
      
    self.BeforeTooltip.SetTip(self.TrimTip(self.grabbedClipboard))
    
    self.sb.SetStatusText(message,0)
    return message

  def TrimTip(self, text):
    """ Make sure the tip isn't too big """
    max = 2048
    if len(text) > max:
      return text[0:2048]+"..."
    return text
    
  def OnActivate(self, event):
    message = 'Ok'
    if event.GetActive():
      message = self.ModifyText()
    else:
      if len(self.sendClipboard) > 0:
        if not self.UpdateClipboard(self.sendClipboard):
          message = "Unable to update the clipboard"

    event.Skip()

  def FindModules(self):
    self.ClipboardMethods = []

    pluginfiles = self._GetPluginFiles()
    self.import_plugin("plugins.donothing")
    for filename in pluginfiles:
      if filename.endswith('.py') \
          and not filename.startswith('_')  \
          and not filename == 'donothing.py':
        import_text = 'plugins.'  + filename.replace('.py', '')
        self.import_plugin(import_text)

  def import_plugin(self, import_text):
    import plugins
    
    print import_text
    try:
      __import__('clipboardmodifier.' + import_text)
    except:
      __import__(import_text) # This works when developing
    self.ClipboardMethods.append(eval(import_text + '.create_plugin()'))
  
  def _GetPluginFiles(self):
    import os
    import plugins
    
    plugindir = os.path.join(plugins.__file__.replace('__init__.pyc', ''))
    ret = os.listdir(plugindir)
    return ret
    
def RunWxApp():
  app = ClipboardModifierApp(0)
  app.MainLoop()
  
if __name__ == '__main__':
  import optparse
  
  parser = optparse.OptionParser()
  (options, args) = parser.parse_args()

  RunWxApp()
