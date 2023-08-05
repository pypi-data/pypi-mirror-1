#! /usr/bin/python
#
# Copyright (C) 2006 Giuseppe Corbelli
#
# This file is part of Pyreb.
#
# Pyreb is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# Pyreb is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Pyreb; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import wx, string
from wx.xrc import XRCID, XRCCTRL

class IntValidator(wx.PyValidator):
    def __init__(self):
        wx.PyValidator.__init__(self)
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        return IntValidator()
        
    def OnChar(self, event):
        key = event.KeyCode()
        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            event.Skip()
            return
        
        if chr(key) in string.digits:
            event.Skip()
            return

        wx.Bell()
        # Returning without calling even.Skip eats the event before it
        # gets to the text control
        return

    def Validate(self, win):
        w = self.GetWindow()
        val = w.GetValue()
        try:
            int(val)
        except:
            return False
        return True
        
    def TransferToWindow(self):
        return True
        
    def TransferFromWindow(self):
        return True

class PyrebPortInputDialog (wx.Dialog):
    def __init__(self):
        p = wx.PreDialog()
        self.PostCreate(p)
        self.Bind(wx.EVT_BUTTON, self.OnCloseWindow, id=XRCID("ID_OK"))
        self.Bind(wx.EVT_INIT_DIALOG, self.OnInit, id=XRCID("PORTINPUT"))
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
    
    def OnInit(self, event):
        w = XRCCTRL(self, "ID_PORT")
        w.SetValidator(IntValidator())
        return
    
    def OnCloseWindow(self, event):
        self.PortCtrl = XRCCTRL(self, "ID_PORT")
        assert self.PortCtrl, "Cannot access port control"
        try:
            self.Port = int(self.PortCtrl.GetValue())
        except ValueError:
            txt = "Invalid value for port: %s" % self.PortCtrl.GetValue()
            wx.MessageDialog(self, txt, "Error", wx.OK|wx.ICON_ERROR).ShowModal()
            self.PortCtrl.SetValue("17787")
            return
        self.Destroy()

