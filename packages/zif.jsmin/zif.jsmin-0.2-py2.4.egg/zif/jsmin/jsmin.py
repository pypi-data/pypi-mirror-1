
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
#
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

# Last Modified: 10 May 2006 Jim Washington

"""
WSGI middleware

does js and css minimization.
"""


import css
import javascript

class middleware(object):

    def __init__(self, application, compress_level='full',
            compress_types="css js",exclude=''):
        #compress level can be 'safe' or 'full'
        self.application = application
        self.compress_level = compress_level
        self.compress_types = compress_types.split()
        self.excludes = exclude.split()

    def __call__(self, environ, start_response):
        response = MinResponse(start_response, self.compress_level,
            self.compress_types)
        app_iter = self.application(environ,response.initial_decisions)
        myGet = environ.get('PATH_INFO')
        for filename in self.excludes:
            if filename in myGet:
                response.doProcessing = False
        if response.doProcessing:
            app_iter = response.finish_response(app_iter)
        return app_iter

class MinResponse(object):

    def __init__(self, start_response, compress_level, compress_types):
        self.start_response = start_response
        self.compress_level = compress_level
        self.compress_types = compress_types
        self.doProcessing = False
        self.compress_type = None

    def initial_decisions(self, status, headers, exc_info=None):
        ct=None
        ce=None
        for name,value in headers:
            name = name.lower()
            if name == 'content-type':
                ct = value
            elif name == 'content-encoding':
                ce = value

        self.doProcessing = False
        if ct and (('javascript' in ct) or ('ecmascript' in ct) or ('css' in ct)):
            self.doProcessing = True
            if 'css' in ct:
                self.compress_type = 'css'
            else:
                self.compress_type = 'js'
        if ce:
            #don't mess with anything compressed.
            self.doProcessing = False
        #just to be sure that this is really wanted
        if self.compress_type not in self.compress_types:
            self.doProcessing = False
        if self.doProcessing:
            headers = [(name,value)for name,value
                    in headers if name.lower()<>'content-length']
        return self.start_response(status, headers, exc_info)

    def finish_response(self,app_iter):
        #the compressor expects a big string, so we make a big string and
        #js- or css- compress it
        theString = ''.join([x for x in app_iter])
        if self.doProcessing:
            if self.compress_type == 'js':
                compress = javascript.compress
            else:
                compress = css.compress
        output = compress(theString, self.compress_level)
        if hasattr(app_iter,'close'):
            app_iter.close()
        return (output,)

def filter_factory(global_conf, compress_level='safe', compress_types="js css", exclude=''):
    def filter(application):
        return middleware(application, compress_level,compress_types,exclude)
    return filter
