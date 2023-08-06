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

from kpwrapper import Triple, uri
from asibsync.sib_agent import to_rdf_instance, to_rdf_ontology, to_struct, recursivedefaultdict

def counter(start = 1):
    s = [start]
    def acc():
        t = s[0]
        s[0] += 1
        return t
    return acc

class Test(unittest.TestCase):
    def setUp(self):
        self.uid = '1234'
        
        self.d = dict(id='1234',
                      name='Eric',
                      favorite_food='eggs',
                      address=dict(street_address='Castle of Anthrax', postal_code='00001'),
                      avatar=dict(link=dict(href='http://python.org/favicon.ico', rel='self'), status='set'))
        
        self.ontology = [Triple('http://cos.alpha.sizl.org/people#Person', 'rdf:type', uri('rdfs:Class')),
                         Triple('http://cos.alpha.sizl.org/people#Address', 'rdf:type', uri('rdfs:Class')),
                         Triple('http://cos.alpha.sizl.org/people#Avatar', 'rdf:type', uri('rdfs:Class')),
                         Triple('http://cos.alpha.sizl.org/people#Link', 'rdf:type', uri('rdfs:Class')),
                         #properties...
                         ]
        
        user_uri = 'http://cos.alpha.sizl.org/people/ID#%s' % self.uid
        addr_uri = 'http://cos.alpha.sizl.org/people#1'
        avatar_uri = 'http://cos.alpha.sizl.org/people#2'
        link_uri = 'http://cos.alpha.sizl.org/people#3'

        self.rdf = [Triple(user_uri, 'rdf:type', uri('http://cos.alpha.sizl.org/people#Person')),
                    Triple(user_uri, 'http://cos.alpha.sizl.org/people#name', 'Eric'),
                    Triple(user_uri, 'http://cos.alpha.sizl.org/people#favorite_food', 'eggs'),
                    Triple(user_uri, 'http://cos.alpha.sizl.org/people#address', uri(addr_uri)),
                    Triple(user_uri, 'http://cos.alpha.sizl.org/people#avatar', uri(avatar_uri)),
                    Triple(addr_uri, 'rdf:type', uri('http://cos.alpha.sizl.org/people#Address')),
                    Triple(addr_uri, 'http://cos.alpha.sizl.org/people#street_address', 'Castle of Anthrax'),
                    Triple(addr_uri, 'http://cos.alpha.sizl.org/people#postal_code', '00001'),
                    Triple(avatar_uri, 'rdf:type', uri('http://cos.alpha.sizl.org/people#Avatar')),
                    Triple(avatar_uri, 'http://cos.alpha.sizl.org/people#link', uri(link_uri)),
                    Triple(avatar_uri, 'http://cos.alpha.sizl.org/people#status', 'set'),
                    Triple(link_uri, 'rdf:type', uri('http://cos.alpha.sizl.org/people#Link')),
                    Triple(link_uri, 'http://cos.alpha.sizl.org/people#href', 'http://python.org/favicon.ico'),
                    Triple(link_uri, 'http://cos.alpha.sizl.org/people#rel', 'self'),
                    ]
        
    def test_recursivedefaultdict(self):
        d = recursivedefaultdict()
        d[1][2][3] = 4
        self.assertEquals(4, d[1][2][3])

    def test_to_rdf_ontology(self):
        self.assertEquals(sorted(self.ontology),
                          sorted(to_rdf_ontology(self.d, 'http://cos.alpha.sizl.org/people', 'Person')))

    def test_to_rdf_instance(self):
        self.assertEquals(sorted(self.rdf),
                          sorted(to_rdf_instance(self.d, 'http://cos.alpha.sizl.org/people', 'Person', 'id',
                                               counter())))

    #def test_to_struct(self):
    #    self.assertEquals({('http://cos.alpha.sizl.org/people', '1234'): self.d}, to_struct(self.rdf))

if __name__ == "__main__":
    unittest.main()
