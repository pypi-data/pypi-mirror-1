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

import time
import threading

from asilib import ASIConnection
from kpwrapper import SIBConnection, Triple

debug = True
def debug_print(*strs):
    if debug:
        print('asi_agent: ', *strs)

class ASIAgent(threading.Thread):
    '''Sample usage:
    sa = SIBAgent()
    aa = ASIAgent()
    aa.set_paired_agent(sa)
    aa.start()
    '''
    
    POLL_INTERVAL = 5  # seconds
    
    def __init__(self):
        super(ASIAgent, self).__init__()
        self.configured_lock = threading.Lock()
        self.configured_lock.acquire()  # release after properly configured

        self.asi_last_updated = None
        self.should_stop = True
        
        self.update_stack = []
        self.update_stack_lock = threading.Lock()

        import os
        conf = {}
        execfile(os.getenv('HOME', '.') + '/.asirc', conf)

        self.ac = ASIConnection(**conf['asi_user_params'])
        self.ac.open()
        self.uid = self.ac.session['entry']['user_id']
    
    def __del__(self):
        if hasattr(self, 'ac'):  # to handle cases where an exception is raised in constructor
            self.ac.close()
    
    def set_paired_agent(self, paired_agent):
        self.paired_agent = paired_agent
        self.configured_lock.release()

    def run(self):
        self.should_stop = False
        self.mainloop()

    def stop(self):
        '''Poor man's "Thread.stop" method'''
        self.should_stop = True
        with self.update_stack_lock:
            pass  # just ensure that we are not inside the update process before returning

    def mainloop(self):
        # Ensure that we are properly configured before going on. Otherwise block here until we are.
        if self.configured_lock.acquire(False):
            debug_print('Configuration has been done, starting.')
        else:
            debug_print('This ASIAgent is not properly configured yet, waiting.')
            self.configured_lock.acquire()
            debug_print('Configuration completed, starting.')

        while not self.should_stop:
            with self.update_stack_lock:
                user = self._get_user()
                if user.updated_at > self.asi_last_updated:
                    debug_print('Updating SIB (%s > %s)' % (user.updated_at, self.asi_last_updated))
                    self.update_stack = []  # ASI changes override other updates, discard them
                    self.paired_agent.receive(user)

                    self.asi_last_updated = user.updated_at
                else:
                    debug_print('No need to update SIB (%s <= %s)' % (user.updated_at, self.asi_last_updated))
                    if self.update_stack:
                        # Only take the last update (topmost item on stack) into account
                        updated_obj = self.update_stack.pop()
                        self.update_stack = []
                        msg = updated_obj['status_message']
                        debug_print('Updating ASI: user.status_message = "%s"' % msg)
                        self.ac.update_user(self.uid, status_message=msg)

            time.sleep(ASIAgent.POLL_INTERVAL)
        
        self.configured_lock.release()

    def _get_user(self):
        return self.ac.get_user(self.uid)

    def receive(self, msg):
        debug_print('Received', msg)
        with self.update_stack_lock:
            self.update_stack.append(msg)
