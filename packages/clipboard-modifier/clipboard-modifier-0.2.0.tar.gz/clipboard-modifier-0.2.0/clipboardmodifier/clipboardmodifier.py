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

Note to self:
Use the same naming conventions as wxPython in this file.
"""
class ClipboardModifierApp(wx.App):
  def init_vars(self):
    self.methods = []
    self.grabbedClipboard = ''
    self.sendClipboard = ''
    self.beforeTemplate = "From: %0d bytes"
    self.afterTemplate = "To: %0d bytes"
    self.unchanged_after = "Unchanged"
    self.class_state = {}
    
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
    self.dialog = dialog 
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
    
    # First one has this style, the remainder have a style of 0
    self.combo = wx.ComboBox(dialog, -1, style=wx.CB_DROPDOWN | wx.CB_READONLY)
    for class_instance in self.clipoard_methods:
      title = class_instance.name()
      self.combo.Append(title)

    self.Bind(wx.EVT_COMBOBOX, self.SetClassToUse, self.combo)
    vsizer.Add(self.combo, 0, wx.ALL | wx.EXPAND, 5)
    self.textDescription = wx.StaticText(dialog, -1, size=(-1, 40), style=wx.TE_READONLY)
    vsizer.Add(self.textDescription, 1, wx.ALL | wx.EXPAND, 10)
    #self.textDescription.Wrap(100)
    self.vsizer = vsizer

    self.plugin_controls_sizer = wx.BoxSizer(wx.VERTICAL)
    self.vsizer.Add(self.plugin_controls_sizer, 0, wx.ALL | wx.EXPAND, 10)

    self.sb = dialog.CreateStatusBar()
    dialog.SetSizer(vsizer)
    self.combo.SetFocus()
    self.SetDefaultClass(0)
    wx.EVT_ACTIVATE(self, self.OnActivate)

  def SetDefaultClass(self, index):
    self.class_to_use = self.clipoard_methods[0]
    self.combo.SetValue(self.class_to_use.name())
    self.SetClassInstance(self.clipoard_methods[0])
    
  def SetClassToUse(self, event):
    """User changed which class to use.

    Also forces a convert with the new class.
    """
    classTitle = event.GetString()
    for class_instance in self.clipoard_methods:
      if class_instance.name() == classTitle:
       self.SetClassInstance(class_instance)
       return

  def SetClassInstance(self, class_instance):
    self.class_state[self.class_to_use.filename] = self.class_to_use.get_state()
    self.class_to_use = class_instance
    self.textDescription.SetLabel(class_instance.description())
    self.ModifyText()
    # This bit of magic resizes the StaticText() so that it wraps if it needs to.
    sizer = self.textDescription.GetContainingSizer()
    sizer.RecalcSizes()
    self.plugin_controls_sizer.DeleteWindows()
    for ctrl in self.class_to_use.control_iter(self.dialog):
      if ctrl:
        self.plugin_controls_sizer.Add(ctrl, 0, wx.ALL | wx.EXPAND, 0)
    if self.class_to_use.filename in self.class_state:
      self.class_to_use.restore_state(self.class_state[self.class_to_use.filename])
    
  def GrabClipboard(self):
    """ Grab the clipboard data """
    if wx.TheClipboard.Open():
      data = wx.TextDataObject()
      success = wx.TheClipboard.GetData(data)
      self.grabbedClipboard = data.GetText()
      wx.TheClipboard.Close()
    
    return self.grabbedClipboard
  
  def UpdateClipboard(self, text):
    """ Overwrite the clipboard data """
    if wx.TheClipboard.Open():
      data = wx.TextDataObject(text)
      wx.TheClipboard.SetData(data)
      wx.TheClipboard.Close()
      return True
    return False
  
  def RunFunction(self, text, func):
    """ Run the function """
    results = func.convert(text)
    return func.message(), results

  def ModifyText(self):
    message = 'Ok'
    if len(self.grabbedClipboard) > 0:
      message, self.sendClipboard = self.RunFunction(self.grabbedClipboard, self.class_to_use)
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
      self.GrabClipboard()
      message = self.ModifyText()
    else:
      if len(self.sendClipboard) > 0:
        if not self.UpdateClipboard(self.sendClipboard):
          message = "Unable to update the clipboard"

    event.Skip()

  def FindModules(self):
    self.clipoard_methods = []

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
    new_plugin = eval(import_text + '.create_plugin()')
    self.clipoard_methods.append(new_plugin)
    setattr(new_plugin, 'parent', self)
    setattr(new_plugin, 'filename', import_text)
  
  def _GetPluginFiles(self):
    import os
    import plugins
    
    plugindir = os.path.join(re.sub('__init__.py.?', '', plugins.__file__))
    ret = os.listdir(plugindir)
    return ret

class MyApp(wx.App):
    def OnInit(self):
        frame = ClipboardModifierApp(None, -1, 'Clipboard Modifier')
        frame.Show(True)
        self.SetTopWindow(frame)
        return True
        
def RunWxApp():
  app = ClipboardModifierApp(0)
  app.MainLoop()
  
if __name__ == '__main__':
  import optparse
  
  parser = optparse.OptionParser()
  (options, args) = parser.parse_args()

  RunWxApp()
