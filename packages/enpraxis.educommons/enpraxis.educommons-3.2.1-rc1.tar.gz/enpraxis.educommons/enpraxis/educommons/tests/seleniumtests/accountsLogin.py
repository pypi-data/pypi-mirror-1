##################################################################################
#    Copyright (c) 2009 Massachusetts Institute of Technology, All rights reserved.
#                                                                                 
#    This program is free software; you can redistribute it and/or modify         
#    it under the terms of the GNU General Public License as published by         
#    the Free Software Foundation; either version 2 of the License, or            
#    (at your option) any later version.                                          
#                                                                                 
#    This program is distributed in the hope that it will be useful,              
#    but WITHOUT ANY WARRANTY; without even the implied warranty of               
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                
#    GNU General Public License for more details.                                 
#                                                                                 
#    You should have received a copy of the GNU General Public License            
#    along with this program; if not, write to the Free Software                  
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA    
#                                                                                 
##################################################################################

__author__  = '''Santiago Suarez Ordoñez'''
__version__   = '$ Revision 0.0 $'[11:-2]
# -*- coding: iso-8859-15 -*-

from seleniumWrapper import selenium
import unittest

class AccountsTest(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost",port, browser,url,instance)
        self.selenium.start()
    
    def test_admin_account(self):
        sel = self.selenium
        sel.login("admin","admin")
        self.failUnless(sel.is_element_present('//a[@id="user-name"]/span[text()="admin"]'))
        self.assertEqual("admin (Administrator)",sel.get_text('//li[a[@id="user-name"]]'))

    def test_producer_account(self):
        sel = self.selenium
        sel.login("producer","producer")
        self.failUnless(sel.is_element_present('//a[@id="user-name"]/span[text()="producer"]'))
        self.assertEqual("producer (Producer)",sel.get_text('//li[a[@id="user-name"]]'))

    def test_reviewer_account(self):
        sel = self.selenium
        sel.login("reviewer","reviewer")
        self.failUnless(sel.is_element_present('//a[@id="user-name"]/span[text()="reviewer"]'))
        self.assertEqual("reviewer (Reviewer)",sel.get_text('//li[a[@id="user-name"]]'))

    def test_qa_account(self):
        sel = self.selenium
        sel.login("qa","qa")
        self.failUnless(sel.is_element_present('//a[@id="user-name"]/span[text()="qa"]'))
        self.assertEqual("qa (QA)",sel.get_text('//li[a[@id="user-name"]]'))

    def test_publisher_account(self):
        sel = self.selenium
        sel.login("publisher","publisher")
        self.failUnless(sel.is_element_present('//a[@id="user-name"]/span[text()="publisher"]'))
        self.assertEqual("publisher (Publisher)",sel.get_text('//li[a[@id="user-name"]]'))

    def test_viewer_account(self):
        sel = self.selenium
        sel.login("viewer","viewer")
        self.failUnless(sel.is_element_present('//a[@id="user-name"]/span[text()="viewer"]'))
        self.assertEqual("viewer (Viewer)",sel.get_text('//li[a[@id="user-name"]]'))

    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)
