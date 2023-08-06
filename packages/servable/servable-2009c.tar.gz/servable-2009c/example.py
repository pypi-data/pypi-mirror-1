# Copyright (c) 2008, Brandon Martin-Anderson
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Servable project nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from servable import Servable

class Example(Servable):
    def hiworld(self):
        return "hello, world"
    
    def add(self, a, b=100):
        return a + b
    
    def yell(self, stuff):
        return stuff.upper()
    
    def append(self, stuff, adder="yourmom"):
        return stuff + adder
    
    def usage(self):
        ret = ""
        for ppath, pargs, pfunc in self.patterns():
            ret += ppath.pattern
            if len(pargs)>0:
                ret += "?" + "&".join(["%s=VALUE"%x for x in pargs])
            ret += "\n"
        return ret
    usage.path = "/$"
    
    def forbidden_method(self):
        return "a super secret"
    forbidden_method.serve = False
    
    def make_tag(self, tagname):
        return "<%s/>"%tagname
    make_tag.mime = "text/xml"

if __name__=='__main__':
    from sys import argv
    if len(argv) == 2:
        port = int(argv[1])
    else: port = 80
    a = Example()
    print "serving on port %d" % port
    a.run_test_server(port=port)