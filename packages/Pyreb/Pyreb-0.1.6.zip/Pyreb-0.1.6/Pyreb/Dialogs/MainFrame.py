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

import wx, sys, wx.stc
from wx.xrc import XRCID, XRCCTRL
from exceptions import RuntimeError

class PyrebFrame (wx.Frame):
    def __init__(self):
        p = wx.PreFrame()
        self.PostCreate(p)
        self.SetMinSize(wx.Size(640,480))
        self.Bind(wx.EVT_WINDOW_CREATE, self.OnCreate)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

    def OnCreate(self, event):
        Application = wx.GetApp()
        assert Application is not None, "Cannot get main application object"
        self.Bind(wx.EVT_MENU, self.OnCloseWindow, id=XRCID("ID_QUIT"))
        self.Bind(wx.EVT_MENU, self.OnShowAbout, id=XRCID("ID_ABOUT"))
        self.Bind(wx.EVT_MENU, self.OnOpenText, id=XRCID("ID_OPENTEXT"))
        self.Bind(wx.EVT_MENU, self.OnOpenRegex, id=XRCID("ID_OPENREGEX"))
        self.Bind(wx.EVT_MENU, self.OnApplyRegex, id=XRCID("ID_APPLYREGEX"))
        self.Bind(wx.EVT_TEXT, self.OnApplyRegex, id=XRCID("ID_TEXT"))
        self.Bind(wx.stc.EVT_STC_UPDATEUI, self.OnApplyRegex, id=XRCID("ID_REGEX"))
        event.Skip()
        
    def OnApplyRegex(self, event):
        message = "Ready"
        reflags = []
        if (self["ID_IGNORECASE"]):
            reflags.append("re.I")
        if (self["ID_MULTILINE"]):
            reflags.append("re.M")
        if (self["ID_DOTALL"]):
            reflags.append("re.S")
        if (self["ID_VERBOSE"]):
            reflags.append("re.X")
        try:
            self.ID_REGEX.Text(self["ID_TEXT"], reflags)
        except RuntimeError, msg:
            message = str(msg)
        
        self.ID_RESULTSTREE.ShowMatches(self.ID_REGEX.MatchObject())
        self.SetStatusText(message)

    def OnOpenRegex(self, event):
        d = wx.FileDialog(self)
        if (wx.ID_OK == d.ShowModal()):
            self.ID_REGEX.LoadFile(d.GetPath())

    def OnOpenText(self, event):
        d = wx.FileDialog(self)
        if (wx.ID_OK == d.ShowModal()):
            self.ID_TEXT.LoadFile(d.GetPath())

    def OnShowAbout(self, event):
        Application = wx.GetApp()
        res = Application.Resource
        dlg = res.LoadDialog(self, "ABOUTDIALOG")
        VersionCtrl = XRCCTRL(dlg, "ID_APPVERSION")
        assert VersionCtrl is not None, "Cannot get text control"
        VersionCtrl.SetLabel("Pyreb V. %s" % (Application.PYREB_VERSION))
        PlatformCtrl = XRCCTRL(dlg, "ID_PLATFORM")
        assert PlatformCtrl is not None, "Cannot get text control"
        PlatformCtrl.SetWindowStyle(wx.SIMPLE_BORDER|wx.ALIGN_LEFT)
        PlatformText = "Python interpreter:\n\t%s\nHost os:\n\t%s"
        PlatformText %= (sys.version, sys.platform)
        PlatformCtrl.SetLabel(PlatformText)
        dlg.ShowModal()

    def OnCloseWindow(self, event):
        self.Destroy()
    
    def __getitem__(self, key):
        """
        Gustomized widget access using the [] interface.
        By asking a widget ID the value obtained with GetValue is returned.
        """
        #Base class does not have __getitem__ so don't call it
        w = XRCCTRL(self, key)
        if (not w):
            raise KeyError("Control %s not found" % key)
        return w.GetValue()
        
    def __setitem__(self, key, value):
        """
        Gustomized widget access using the [] interface.
        By setting the value for a widget ID the SetValue method of the widget is called.
        """
        w = XRCCTRL(self, key)
        if (not w):
            raise KeyError("Control %s not found" % key)
        w.SetValue(value)

    def __getattribute__(self, name):
        """
        Gustomized widget access using the new class style.
        By asking a widget ID the widget is returned.
        """
        try:
            #First call base-class
            return super(PyrebFrame, self).__getattribute__(name)
        except AttributeError:
            pass
        w = XRCCTRL(self, name)
        if (not w):
            raise AttributeError("Control %s not found" % name)
        return w
    
