#! /usr/bin/python## Copyright (C) 2006 Giuseppe Corbelli## This file is part of Pyreb.## Pyreb is free software; you can redistribute it and/or modify# it under the terms of the GNU General Public License as published by# the Free Software Foundation; either version 2 of the License, or# (at your option) any later version.# # Pyreb is distributed in the hope that it will be useful,# but WITHOUT ANY WARRANTY; without even the implied warranty of# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the# GNU General Public License for more details.# # You should have received a copy of the GNU General Public License# along with Pyreb; if not, write to the Free Software# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""
This is a really simple test suite for Pyreb XMLRPC Server
"""
import os, os.path, sys, unittest, xmlrpclibSERVER_ADDRESS = "http://localhost:17787"class Fixture(unittest.TestCase):    def setUp(self):        self.conn = xmlrpclib.ServerProxy(SERVER_ADDRESS)class FullTest(Fixture):    def testMethods(self):        l = self.conn.system.listMethods()        known = ['Pyreb.getRegex', 'Pyreb.getText', 'Pyreb.setRegex', 'Pyreb.setText',                 'system.listMethods', 'system.methodHelp', 'system.methodSignature']        for methodname in known:            self.assert_(methodname in l)    def test01(self):
        """
        Test getText / setText
        """        x = self.conn.Pyreb.getText()        self.assertEqual( x, '')
        x = self.conn.Pyreb.setText('12345')        self.assertEqual(x, '')        x = self.conn.Pyreb.getText()        self.assertEqual(x, '12345')
        
    def test002(self):
        """
        Test getRegex / setRegex
        """
        x = self.conn.Pyreb.getRegex()        self.assertEqual(x, '')
        x = self.conn.Pyreb.setRegex('[\d]{3}(?P<g1>\d+)')        self.assertEqual(x, '')        x = self.conn.Pyreb.getRegex()        self.assertEqual(x, '[\d]{3}(?P<g1>\d+)')
        #~ self.conn.Pyreb.Quit()def main():    unittest.main()
if __name__ == '__main__':    main()