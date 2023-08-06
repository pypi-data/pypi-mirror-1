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

import discovery_enhanced
from smart_m3.Node import ParticipantNode, TCPConnector

instancemethod = type(ParticipantNode.discover)
ParticipantNode._old_discover = ParticipantNode.discover

def discover(self, method = "Manual", browse = True, name = None):
    """Discover available smart spaces. Currently available
    discovery methods are:
      - Manual: give IP address and port
      - preconfigured: IP address and port read from a conffile
      - Bonjour discovery (if pyBonjour package has been installed)
    Returns a handle for smart space if method is Manual or preconfigured
    or browse is True, otherwise returns a list of handles
    Handle is a tuple
    (SSName, (connector class, (connector constructor args)))
    """
    if method == 'preconfigured':
        # Mostly copy-paste code from Node.py
        disc = discovery_enhanced.discover(method, name)
        def _insert_connector(item):
            n, h = item
            c, a = h
            c = TCPConnector
            rv = (n, (c, a))
            return rv
        
        if disc[1][0] == "TCP":
            return _insert_connector(disc)
        else:
            print "Unknown connection type:", item[1][0]
            return None
    else:
        return self._old_discover(method, browse, name)    

ParticipantNode.discover = instancemethod(discover, None, ParticipantNode)
