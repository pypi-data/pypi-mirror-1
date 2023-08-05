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
#    * Neither the name of Virginia Polytechnic Institute and State University
#      nor the names of its contributors may be used to endorse or promote
#      products derived from this software without specific prior written
#      permission.

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

# Last Modified: 16 Dec  2006 Jim Washington

# made stylesheet include a link tag instead of a style tag jmw 20061216


""" wsgi middleware for inserting script and style tags into the <head>
of an html file.  It looks at environ['wsgi.html.head.includes'], which
is a list of the urls to be referenced.  If the url ends in '.js', a script
tag is inserted.  If it ends in ".css", a style tag is inserted.

this filter takes care of creating the 'wsgi.html.head.includes' key; the
application just needs to insert relative or absolute urls for the files that
need to be referenced.  This filter will remove duplicates if the app does
not want to check before adding urls to the list.

urls can be placed in the list at any time that request.environ can be
accessed.  Just append any desired url to the list, e.g.,

  try:
      request.environ['wsgi.html.head.includes'].append('/scripts/my_url.js')
  except KeyError:
      (handle case when the filter is not available)
parameters:
location - where in the head element to place the includes.  'top' is the
           default.  Anything else will place it at the bottom.
"""

from queues import StringQueue

class HeadIncludeIter(object):
    def __init__(self,result,environ,tag,write=65536,read=65536):
        self.readBufferSize = read
        self.writeBufferSize = write
        self.environ = environ
        self.tag = tag
        self.queue = StringQueue()
        self.madeUpdate = False
        if isinstance(result,basestring):
            result = (result,)
        self.data = iter(result)
        self.allReceived = False
        self.getData()

    def __iter__(self):
        return self

    def getData(self):
        while len(self.queue) < self.readBufferSize and not self.allReceived:
            self.getIter()

    def getIter(self):
        try:
            s = self.data.next()
            if (self.tag in s) or (self.tag.upper() in s):
                s = self.makeInsertion(s)
            self.queue.write(s)
        except StopIteration:
            self.allReceived = True
            if hasattr(self.data,"close"):
                self.data.close()
            self.data = None

    def makeInsertion(self,data):
        includes = self.environ.get('wsgi.html.head.includes','')
        if self.tag.upper() in data:
            #OK, we will go with upper-case.
            self.tag = self.tag.upper()
        if includes:
            s = ['<!--start headincludes-->']
            for incfile in includes:
                if isinstance(incfile,unicode):
                    # don't want the file to end up unicode. Bleah!
                    incfile = incfile.encode('ascii')
                if incfile.endswith('.js'):
                    s.append(
                  '<script type="text/javascript" src="%s"></script>' % incfile)
                elif incfile.endswith('.css'):
                    s.append(
#                  '<style type="text/css" src=>@import url(%s)</style>' % incfile)
                  '<link rel="stylesheet" type="text/css" href="%s" />' % incfile)

            s.append('<!--end headincludes-->')
            if not "/" in self.tag:
                s.insert(0,self.tag)
            else:
                s.append(self.tag)
            updated = data.replace(self.tag,"\n".join(s))
        else:
            updated = data
        return updated

    def next(self):
        queueLen = len(self.queue)
        if queueLen == 0 and self.allReceived:
            self.queue.close()
            raise StopIteration
        dataGetSize = min(queueLen,self.writeBufferSize)
        s = self.queue.read(dataGetSize)
        if s == '' and self.allReceived:
            s = self.queue.read(None)
        if not self.allReceived:
            self.getData()
        return s

class middleware(object):

    def __init__(self, application,location="top"):
        self.application = application
        self.location = location
        if location == 'top':
            self.tag = '<head>'
        else:
            self.tag = '</head>'

    def __call__(self, environ, start_response):
        environ['wsgi.html.head.includes'] = []
        response = HeadChangeResponse(start_response,self.location)
        app_iter = self.application(environ,response.initial_decisions)
        if response.doProcessing and len(environ['wsgi.html.head.includes'])>0:
            app_iter = response.finish_response(app_iter,environ,self.tag)
        return app_iter


class HeadChangeResponse(object):

    def __init__(self,start_response,location):
        self.start_response = start_response
        self.location = location
        self.doProcessing = False

    def initial_decisions(self,status,headers,exc_info=None):
        for name,value in headers:
            if name.lower() == 'content-type' and \
                (value.startswith('text/html') or \
                 value.startswith('application/xhtml+xml')):
                self.doProcessing = True
                break
        if self.doProcessing:
            headers = [(name,value) for name,value in headers
                        if name.lower()<>'content-length']
        return self.start_response(status,headers,exc_info)

    def finish_response(self,app_iter,environ,tag):
        if app_iter:
            try:
                output = HeadIncludeIter(app_iter,environ,tag)
            finally:
                try:
                    app_iter.close()
                except AttributeError:
                    pass
                if len(app_iter) == 1:
                    # input was a 1-tuple, so we will return one
                    s = ''.join([x for x in output])
                    return (s,)
                return output
        else:
            return app_iter


def filter_factory(global_conf,location="top"):
    def filter(application):
        return middleware(application,location)
    return filter
