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

import wx, wx.xrc
from wx.xrc import XRCCTRL, XRCIDimport Controls, Dialogsimport sys, os.path, imp
from Server import *

PYREB_VERSION = "0.1.3"
class PyrebApp(wx.App):
    """
    Main Pyreb app.
    """    def __init__(self, *args, **kwargs):
        """
        Requires the directory where this file is installed to start up,
        to find the resource file 'pyreb.xrc'
        """
        if (self.IsFrozen()):
            self.BaseDir = sys.executable
        else:
            self.BaseDir = __file__
        while (not os.path.isdir(self.BaseDir)):
            self.BaseDir = os.path.split(self.BaseDir)[0]
        self.PYREB_VERSION = PYREB_VERSION
        self.XMLRPCServer = None
        wx.App.__init__(self, args, kwargs)
    
    def IsFrozen(self):
        return (hasattr(sys, "frozen") or # new py2exe
            hasattr(sys, "importers") # old py2exe
            or imp.is_frozen("__main__")) # tools/freeze    
    
    def OnSetText(self, event):
        self.dialog.textctrl.SetValue(event.text)
        
    def OnGetText(self, event):
        event.text = self.dialog.textctrl.GetValue()
        
    def OnSetRegex(self, event):
        self.dialog.regexctrl.SetValue(event.text)
        
    def OnGetRegex(self, event):
        event.text = self.dialog.regexctrl.GetValue()

    def OnExit(self):
        if (self.XMLRPCServer):
            self.XMLRPCServer.Mutex.release()
            #Likely the timeout expires, as the server is waiting a connection
            self.XMLRPCServer.join(1.0)

    def OnInit(self):
        """
        Find the resource file, load the GUI and start the application.
        """
        self.CheckWxVersion(2, 6, 0)
        self.ResourceFile = os.path.join(self.BaseDir, 'Resource', 'pyreb_wxglade.xrc')
        try:
            fd = file (self.ResourceFile, "r")
            self.ResourceAsString = fd.read()
            del(fd)
        except IOError, reason:
            msg = "Can't find the resource file 'pyreb.xrc'. Pyreb installation is corrupt.\n%s" % reason
            wx.MessageBox(msg, "Error", wx.OK|wx.ICON_ERROR)
            sys.exit(1)
        self.Resource = wx.xrc.EmptyXmlResource()
        self.Resource.InsertHandler(Controls.PyrebResultsTreeXmlHandler())
        self.Resource.InsertHandler(Controls.PyrebRegexCtrlXmlHandler())
        self.Resource.LoadFromString(self.ResourceAsString)
        del(self.ResourceAsString)
        #~ self.Resource = wx.xrc.XmlResource("pyreb_wxglade.xrc")
        self.SetAssertMode(wx.PYAPP_ASSERT_DIALOG)        self.dialog = self.Resource.LoadFrame(None, "MAIN")        assert self.dialog is not None, "Cannot load main application frame"
        self.dialog.SetTitle ("Pyreb v. %s / wxWidgets %s" % \
            (PYREB_VERSION, wx.VERSION_STRING))
        self.SetTopWindow(self.dialog)
        self.dialog.Show()
        self.dialog.regexctrl = XRCCTRL(self.dialog, "ID_REGEX")
        assert self.dialog.regexctrl is not None, "Cannot get regex control"        self.dialog.textctrl = XRCCTRL(self.dialog, "ID_TEXT")
        assert self.dialog.textctrl is not None, "Cannot get text control"        self.dialog.resultstree = XRCCTRL(self.dialog, "ID_RESULTSTREE")
        assert self.dialog.resultstree is not None, "Cannot get results tree control"        self.dialog.ignorecheck = XRCCTRL(self.dialog, "ID_IGNORECASE")        self.dialog.multicheck = XRCCTRL(self.dialog, "ID_MULTILINE")        self.dialog.dotallcheck = XRCCTRL(self.dialog, "ID_DOTALL")        self.dialog.verbosecheck = XRCCTRL(self.dialog, "ID_VERBOSE")        self.dialog.CreateStatusBar(2, wx.ST_SIZEGRIP)        self.dialog.SetStatusText("Ready")
        self.dialog.SetStatusText("XMLRPC Server not running", 1)
        self.Bind(EVT_EXT_SETTEXT, self.OnSetText)
        self.Bind(EVT_EXT_GETTEXT, self.OnGetText)
        self.Bind(EVT_EXT_SETREGEX, self.OnSetRegex)
        self.Bind(EVT_EXT_GETREGEX, self.OnGetRegex)
        
        self.Bind(wx.EVT_MENU, self.StartXMLRPCServer, id=XRCID("ID_STARTSERVER"))
        
        return True

    def StartXMLRPCServer(self, event):
        if (self.XMLRPCServer):
            wx.MessageBox("Server should be already running.", "Error")
            return
        dlg = self.Resource.LoadDialog(self.dialog, "PORTINPUT")
        dlg.ShowModal()
        self.XMLRPCServer = PyrebXMLRPCServer(self.dialog, dlg.Port)
        self.XMLRPCServer.Mutex.acquire()
        self.XMLRPCServer.setDaemon(True)
        self.XMLRPCServer.start()
        Menu = self.dialog.GetMenuBar()
        assert Menu
        Menu.Enable(XRCID("ID_STARTSERVER"), False)
        self.dialog.SetStatusText("XMLRPC Server running on localhost:%s" % dlg.Port, 1)
        wx.MessageBox("Server started OK")

    def CheckWxVersion(self, Major, Minor, Micro):
        (wxMaj, wxMin, wxMic, wxRes, s) = wx.VERSION
        Req = Major * 100 + Minor * 10 + Micro
        Got = wxMaj * 100 + wxMin * 10 + wxMic
        if (Req > Got):
            msg = "Pyreb requires at least wxWidgets %d.%d.%d, you have %d.%d.%d" % \
                (Major, Minor, Micro, wxMaj, wxMin, wxMic)
            wx.MessageBox(msg, "wxWidgets version check failed", wx.OK|wx.ICON_ERROR)
            sys.exit(1)

def main():
    app = PyrebApp(redirect=True)
    app.MainLoop()

if __name__ == '__main__':
    main()
