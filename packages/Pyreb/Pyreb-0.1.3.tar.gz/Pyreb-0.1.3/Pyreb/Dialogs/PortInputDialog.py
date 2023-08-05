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

import wx
from wx.xrc import XRCID, XRCCTRL

class PyrebPortInputDialog (wx.Dialog):
    def __init__(self):
        p = wx.PreDialog()
        self.PostCreate(p)
        self.Bind(wx.EVT_BUTTON, self.OnCloseWindow, id=XRCID("ID_OK"))
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
    
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
