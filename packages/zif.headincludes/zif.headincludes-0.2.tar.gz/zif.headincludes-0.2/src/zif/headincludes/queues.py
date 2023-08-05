# Copyright (c) 2006, Virginia Polytechnic Institute and State University
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#    * Neither the name of the University nor the names of its contributors may
#      be used to endorse or promote products derived from this software without
#      specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# Last Modified: 9 May 2006 Jim Washington

"""
useful queues for wsgi middleware
"""

import tempfile

class TemporaryFileQueue(object):
    def __init__(self):
        self.file = tempfile.TemporaryFile()
        self.readPointer = 0
        self.writePointer = 0

    def read(self,bytes=None):
        self.file.flush()
        self.file.seek(self.readPointer)
        if bytes:
            s = self.file.read(bytes)
        else:
            s = self.file.read()
        self.readPointer = self.file.tell()
        return s

    def write(self,data):
        self.file.seek(self.writePointer)
        self.file.write(data)
        self.writePointer = self.file.tell()

    def __len__(self):
        #this is the length of the unread queue
        return self.writePointer - self.readPointer

    def close(self):
        self.file.close()
        self.file = None


class StringQueue(object):
    # This is Python Licensed
    # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/426060
    def __init__(self, data=""):
        self.l_buffer = []
        self.s_buffer = ""
        self.write(data)

    def write(self, data):
        #check type here, as wrong data type will cause error on self.read,
        #which may be confusing.
        if not isinstance(data,basestring):
            raise TypeError, "argument 1 must be string, not %s" % \
                type(data).__name__
        #append data to list, no need to "".join just yet.
        self.l_buffer.append(data)

    def _build_str(self):
        #build a new string out of list
        new_string = "".join(self.l_buffer)
        #join string buffer and new string
        self.s_buffer = "".join((self.s_buffer, new_string))
        #clear list
        self.l_buffer = []

    def __len__(self):
        #calculate length without needing to _build_str
        return sum(len(i) for i in self.l_buffer) + len(self.s_buffer)

    def close(self):
        self.__init__()

    def read(self, count=None):
        #if string doesnt have enough chars to satisfy caller, or caller is
        #requesting all data
        if count > len(self.s_buffer) or count==None: self._build_str()
        #if i don't have enough bytes to satisfy caller, return nothing.
        if count > len(self.s_buffer): return ""
        #get data requested by caller
        result = self.s_buffer[:count]
        #remove requested data from string buffer
        self.s_buffer = self.s_buffer[len(result):]
        return result
