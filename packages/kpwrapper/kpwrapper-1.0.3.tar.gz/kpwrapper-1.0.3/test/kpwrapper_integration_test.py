#! /usr/bin/env python
# -*- coding: utf8 -*-
#
# Copyright (c) 2009, Nokia Corp.
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of Nokia nor the names of its contributors may be
#       used to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED THE COPYRIGHT HOLDERS AND CONTRIBUTORS ''AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

__author__ = 'eemeli.kantola@iki.fi (Eemeli Kantola)'

import unittest
import time

import kpwrapper
#kpwrapper.debug = True

from kpwrapper import SIBConnection, Triple, uri, literal

ANY_TRIPLE = Triple(None, None, None)

class IntegrationTestBase(unittest.TestCase):
    def setUp(self):
        self.sc = SIBConnection('kpwrapper_test.%s' % self.__class__.__name__, method='preconfigured')
        self.sc.open()
    
    def tearDown(self):
        self.sc.close()

    def query_any_nontype_triple(self):
        return [t for t in self.sc.query(ANY_TRIPLE) if not t.predicate.startswith('http://www.w3.org/')]

class PlainIntegrationTest(IntegrationTestBase):
    def test_connect_and_leave(self):
        pass
        # Should not crash here

    def test_empty_query_tx(self):
        with self.sc.query_tx():
            pass
        # Should not crash here

class IntegrationTestWithPurge(IntegrationTestBase):
    def _purge_db(self):
        all = self.sc.query(ANY_TRIPLE)
        self.assertTrue(self.sc.remove(all))
        self.assertEquals([], self.query_any_nontype_triple())
    
    def setUp(self):
        super(IntegrationTestWithPurge, self).setUp()
        self._purge_db() # ensure the db is empty
    
    def tearDown(self):
        self._purge_db() # no triples shall be left in db afterwards
        super(IntegrationTestWithPurge, self).tearDown()

    def test_insert_and_remove(self):
        triple = Triple('subj', 'pred', 'obj')
        self.assertTrue(self.sc.insert(triple))
        results = self.query_any_nontype_triple()
        self.assertEquals([triple,], results)
        
        self.assertTrue(self.sc.remove(results))
        self.assertEquals([], self.query_any_nontype_triple())

    def test_insert_and_remove_intl_chars(self):
        triple = Triple('subj', 'pred', literal('Ääkköset'))
        self.assertTrue(self.sc.insert(triple))
        results = self.query_any_nontype_triple()
        self.assertEquals([triple,], results)
        
        self.assertTrue(self.sc.remove(results))
        self.assertEquals([], self.query_any_nontype_triple())

    def test_update(self):
        triple = Triple('subj', 'pred', 'val1')
        updated_triple = Triple('subj', 'pred', 'val2')
        self.assertTrue(self.sc.insert(triple))
        self.assertEquals([triple,], self.query_any_nontype_triple())
        
        self.assertTrue(self.sc.update(triple, updated_triple))
        self.assertEquals([updated_triple,], self.query_any_nontype_triple())

    def test_subscribe(self):
        callback_called = [False] # Python 2.x's way of Python 3.x's nonlocal.
                                  # See http://stackoverflow.com/questions/1195577/python-scoping-problem
        triple = Triple('subj', 'pred', 'obj')

        def callback(added, removed):
            self.assertEquals([triple,], added)
            self.assertEquals([], removed)
            callback_called[0] = True
        
        tx = self.sc.subscribe(triple, callback)
        self.assertTrue(tx is not None)
        time.sleep(0.1)  # give subscribe handler time to start up
        self.assertTrue(self.sc.insert(triple))
        time.sleep(0.1)  # give subscribe handler time to act 
        
        self.assertTrue(callback_called[0])
        tx.close()

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
