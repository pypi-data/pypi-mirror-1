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

from __future__ import print_function

__author__ = 'eemeli.kantola@iki.fi (Eemeli Kantola)'

import collections
import uuid

from kpwrapper import SIBConnection, Triple, uri, literal

debug = True
def debug_print(*strs):
    if debug:
        print('sib_agent: ', *strs)

def to_rdf_ontology(struct, base_uri, base_type):
    rdf = [Triple('%s#%s' % (base_uri, base_type), 'rdf:type', uri('rdfs:Class'))]
    rdf.extend(_dict_to_rdf_ontology(struct, base_uri))
    return rdf

def _dict_to_rdf_ontology(d, u):
    rdf = []
    for k in d.keys():
        v = d[k]
        if isinstance(v, dict):
            rdf.append(Triple('%s#%s' % (u, k.capitalize()), 'rdf:type', uri('rdfs:Class')))
            rdf.extend(_dict_to_rdf_ontology(v, u))

    return rdf

def to_rdf_instance(struct, base_uri, base_type, id_key, id_generator=uuid.uuid4):
    '''to_rdf_instance(struct, base_uri, base_type, id_key) -> list(Triple(...), Triple(...), ...)
    
    Transform a Python dict or list of dicts into a list of RDF triples. The
    struct is meant to be an ASI JSON object, mapped to a corresponding Python
    structure. Map values with the key id_key will be omitted from the
    resulting triples and appended to base_uri to form the object values.
    '''
    if not isinstance(struct, collections.Sequence):
        struct = (struct,)
    
    rdf = []
    for item in struct:
        id = item[id_key]
        instance_uri = '%s/ID#%s' % (base_uri, id)
        rdf.append(Triple(instance_uri, 'rdf:type', uri('%s#%s' % (base_uri, base_type))))
        
        copy = item.copy()
        del copy[id_key]
        rdf.extend(_dict_to_rdf_instance(copy, base_uri, instance_uri, id_generator))
    
    return rdf

def _dict_to_rdf_instance(d, base_uri, instance_uri, id_generator):
    '''Helper function for to_rdf_instance, doing the actual work.'''
    rdf = []
    for k in sorted(d.keys()):
        v = d[k]
        if isinstance(v, collections.Mapping):
            new_instance_uri = '%s#%s' % (base_uri, id_generator())
            rdf.append(Triple(instance_uri, '%s#%s' % (base_uri, k), uri(new_instance_uri)))
            rdf.append(Triple(new_instance_uri, 'rdf:type', uri('%s#%s' % (base_uri, k.capitalize()))))
            rdf.extend(_dict_to_rdf_instance(v, base_uri, new_instance_uri, id_generator))
        else:
            rdf.append(Triple(instance_uri, '%s#%s' % (base_uri, k), v))
    
    return rdf

# Code adapted from http://personalpages.tds.net/~kent37/kk/00013.html
class recursivedefaultdict(collections.defaultdict):
    def __init__(self, *args, **kwargs):
        super(recursivedefaultdict, self).__init__(*args, **kwargs)
        self.default_factory = type(self)
    
    def __repr__(self):  # for dict-like pretty-printing
        return dict.__repr__(self)

def to_struct(triples, id_key='id'):
    '''FIXME This function is not up to date and the test doesn't pass.'''
    if not isinstance(triples, collections.Sequence):
        triples = (triples,)
    
    struct = recursivedefaultdict()
    for triple in triples:
        base_uri, rest = triple.subject.rsplit('/', 1)
        rest = rest.split('#')
        id = rest.pop(0)
        key = (base_uri, id)
        obj = struct[key]
        for param in rest:
            obj = obj[param]
        
        if isinstance(triple.object, literal):
            obj[triple.predicate[:]] = triple.object[:]

    # Add the id that was embedded in subject uri
    for key in struct.iterkeys():
        struct[key][id_key] = key[1]
    return struct

class SIBAgent:
    '''Sample usage:
    aa = ASIAgent()
    sa = SIBAgent()
    sa.set_paired_agent(aa)
    sa.start()
    '''

    RDF_BASE_URI = 'http://cos.alpha.sizl.org/people'
    RDF_BASE_TYPE = 'Person'

    QUERY_STATUS_MESSAGE = Triple(uri('http://cos.alpha.sizl.org/people/ID#bGbllAMtur3QUbaaWPEYjL'),
                                  uri('http://cos.alpha.sizl.org/people#status_message'),
                                  None)

    def __init__(self, asi_updated=None):
        self.paired_agent = self.sc = None
        self.asi_updated = asi_updated
        self.sc = SIBConnection('SIB to ASI', method='preconfigured')
        self.subscribe_tx = None
        self.ontology_check_needed = True

    def __del__(self):
        if hasattr(self, 'sc'):  # to handle cases where an exception is raised in constructor
            self.sc.close()

    def set_paired_agent(self, paired_agent):
        self.paired_agent = paired_agent
    
    def start(self):
        if not self.paired_agent:
            raise Exception('SIBAgent must be properly configured before starting: set ASIAgent with set_paired_agent().')
        
        self.callback_enabled = True
        self.subscribe_tx = self.sc.subscribe(SIBAgent.QUERY_STATUS_MESSAGE, self)
        debug_print('Subscribed to ', SIBAgent.QUERY_STATUS_MESSAGE)

    def stop(self):
        if self.subscribe_tx:
            self.subscribe_tx.close()
            self.subscribe_tx = None
    
    def callback(self, added, removed):
        '''SIB subscribe callback handler'''
        debug_print('Callback called with added=%s, removed=%s' % (added, removed))
        
        if not self.callback_enabled:
            debug_print('Callback is disabled')
            return

        if added:
            debug_print('Change detected, updating ASI.')
            self.paired_agent.receive(dict(status_message=added[0].object))
            update_done = True
        else:
            debug_print('Change detected but no update was needed')

    def check_ontology(self, value):
        debug_print('Checking ontology')
        ont = to_rdf_ontology(value, SIBAgent.RDF_BASE_URI, SIBAgent.RDF_BASE_TYPE)
        new = []
        for t in ont:
            if not self.sc.query(t):
                new.append(t)
        if new:
            debug_print('Adding the missing ontology items: %s' % new)
            self.sc.insert(new)
        else:
            debug_print('Ontology seems to be up to date')

    def receive(self, msg):
        self.callback_enabled = False
        
        if self.ontology_check_needed:
            self.check_ontology(msg)
            self.ontology_check_needed = False
        
        debug_print('Received %s' % msg)
        new = to_rdf_instance(msg, SIBAgent.RDF_BASE_URI, SIBAgent.RDF_BASE_TYPE, 'id')

        # Removing disabled for now, maybe for good
        #old_subjs = set([t.subject for t in to_rdf_instance(msg, 'id', 'http://cos.alpha.sizl.org/people/')])
        
        #debug_print('Removing the previous triples with subjects in ', old_subjs)
        #for s in old_subjs:
        #    self.sc.remove(self.sc.query(Triple(s, None, None)))
        
        debug_print('Inserting ', new)
        self.sc.insert(new)
        
        self.callback_enabled = True
