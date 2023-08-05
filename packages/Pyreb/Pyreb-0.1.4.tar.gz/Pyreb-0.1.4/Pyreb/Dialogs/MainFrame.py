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

        self.regexctrl = None
        self.textctrl = None
        self.resultstree = None
        self.ignorecheck = None
        self.multicheck = None
        self.dotallcheck = None
        self.verbosecheck = None
        self.SetMinSize(wx.Size(640,480))
        self.Bind(wx.EVT_WINDOW_CREATE, self.OnCreate)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

    def OnCreate(self, event):
        Application = wx.GetApp()
        assert Application is not None, "Cannot get main application object"
        res = Application.Resource
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
        if (self.ignorecheck.IsChecked()):
            reflags.append("re.I")
        if (self.multicheck.IsChecked()):
            reflags.append("re.M")
        if (self.dotallcheck.IsChecked()):
            reflags.append("re.S")
        if (self.verbosecheck.IsChecked()):
            reflags.append("re.X")
        try:
            self.regexctrl.Text(self.textctrl.GetValue(), reflags)
        except RuntimeError, msg:
            message = str(msg)

        self.resultstree.ShowMatches(self.regexctrl.MatchObject())
        self.SetStatusText(message)

    def OnOpenRegex(self, event):
        d = wx.FileDialog(self)
        if (wx.ID_OK == d.ShowModal()):
            self.regexctrl.LoadFile(d.GetPath())

    def OnOpenText(self, event):
        d = wx.FileDialog(self)
        if (wx.ID_OK == d.ShowModal()):
            self.textctrl.LoadFile(d.GetPath())

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

