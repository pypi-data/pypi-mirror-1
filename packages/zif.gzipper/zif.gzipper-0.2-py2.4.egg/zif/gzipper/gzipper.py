
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

# Last Modified: 9 May 2006 Jim Washington

"""
WSGI middleware

Gzip-encodes the response.
"""

import time, struct, zlib, tempfile
from queues import TemporaryFileQueue, StringQueue

class GZStreamIter(object):
    #the constant parameters here are guesses
    def __init__(self, data, compressLevel=6, write=65536, read=65536,\
            tempFileTrigger=1048576):
        self.writeBufferSize = write
        self.readBufferSize = read
        self.tempFileTrigger = tempFileTrigger
        self.inputIsNotIterator = False
        #make sure data is an iterator
        if isinstance(data,tuple) or isinstance(data,list):
            data = iter(data)
            self.inputIsNotIterator = True
        elif isinstance(data,basestring):
            data = iter([data])
            self.inputIsNotIterator = True
        self.data = data
        self.queue = StringQueue()
        self.usingTempFile = False
        self.allReceived = False
        #set-up gzipping
        self.initFile()
        self.crc = zlib.crc32('')
        self.size = 0
        self.compressor = zlib.compressobj(compressLevel,
            zlib.DEFLATED, -zlib.MAX_WBITS, zlib.DEF_MEM_LEVEL, 0)
        self.compress = self.compressor.compress
        self.crc32 = zlib.crc32
        #now, get data...
        self.getData()

    def __len__(self):
        #this is the length of the gzipped object
        return self.size

    def getLength(self):
        return self.size

    def close(self):
        self.queue.__init__()

    def __iter__(self):
        return self

    def initFile(self):
        self.queue.write('\037\213\010\000')
        self.queue.write(struct.pack('<L', long(time.time())))
        self.queue.write('\002\377')

    def getData(self):
        while len(self.queue) < self.readBufferSize and not self.allReceived:
            self.getIter()

    def getIter(self):
        try:
            s = self.data.next()
            self.queue.write(self.compress(s))
            self.size += len(s)
            self.crc = self.crc32(s,self.crc)
            if self.tempFileTrigger:
                if self.size > self.tempFileTrigger and not self.usingTempFile:
                    tmp = TemporaryFileQueue()
                    tmp.write(self.queue.read(None))
                    self.queue.close()
                    self.queue = tmp
                    self.usingTempFile = True
        # ValueError comes from spurious "I/O Operation on closed file"
        # not sure this is the fix that is true and pure...
        #except StopIteration:
        except (StopIteration, ValueError):
            self.endFile()
            self.allReceived = True
            if hasattr(self.data,"close"):
                self.data.close()
            self.data = None

    def endFile(self):
            self.queue.write(self.compressor.flush())
            self.queue.write(struct.pack('<LL',
                self.crc & 0xFFFFFFFFL, self.size & 0xFFFFFFFFL))

    def next(self):
        if self.usingTempFile and self.inputIsNotIterator:
            # no point minimizing memory - get all the rest and release the
            # incoming object
            while not self.allReceived:
                self.getIter()
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

    length = property(getLength)


class middleware(object):

    def __init__(self, application, compress_level=6,nocompress="",
                tempfile="1048576",exclude=''):
        self.application = application
        self.compress_level = int(compress_level)
        self.nocompress = nocompress.split()
        self.tempFile = int(tempfile)
        self.excludes = exclude.split()

    def __call__(self, environ, start_response):
        doNothing = False
        if 'gzip' not in environ.get('HTTP_ACCEPT_ENCODING', ''):
            #do nothing.  return the app output.
            doNothing = True
        myGet = environ.get('PATH_INFO')
        for filename in self.excludes:
            if filename in myGet:
                doNothing = True
        if doNothing:
            return self.application(environ, start_response)
        response = GzipResponse(start_response, self.compress_level,
            self.nocompress, tempFileTrigger=self.tempFile)
        app_iter = self.application(environ,response.initial_decisions)
        if response.doProcessing:
            app_iter = response.finish_response(app_iter)
        return app_iter


class GzipResponse(object):

    def __init__(self, start_response, compress_level, nocompress=[],
                 tempFileTrigger=1048576):
        self.start_response = start_response
        self.doProcessing = False
        self.compress_level = compress_level
        self.nocompress = nocompress
        self.tempFileTrigger = tempFileTrigger

    def initial_decisions(self, status, headers, exc_info=None):
        ct = None
        ce = None
        for name,value in headers:
            name = name.lower()
            if name == 'content-type':
                ct = value
            elif name == 'content-encoding':
                ce = value
        self.doProcessing = False
        if ct:
            self.doProcessing = True
            for k in self.nocompress:
                if k in ct:
                    self.doProcessing = False and self.doProcessing
        if ce:
            self.doProcessing = False
        if self.doProcessing:
            d = None
            # add gzip header
            headers.append(('content-encoding', 'gzip'))
            # zap any given content-length;
            # server will need to be recalculate or
            # decide whether to transfer-encode.
            headers = [(name,value) for name,value in headers
                        if name.lower()<>'content-length']
        return self.start_response(status, headers, exc_info)

    def finish_response(self,app_iter):
        if app_iter:
            try:
                output = GZStreamIter(app_iter,self.compress_level,
                    tempFileTrigger= self.tempFileTrigger)
            finally:
                try:
                    app_iter.close()
                except AttributeError:
                    pass

                if hasattr(app_iter,'__len__') and len(app_iter)==1:
                    # special case; obviously, we want a 1-tuple output
                    # like the input
                    s = ''.join([x for x in output])
                    return (s,)
                return output
        else:
            return app_iter

def filter_factory(global_conf, compress_level="6", nocompress='', tempfile='1048576',exclude=''):
    def filter(application):
        return middleware(application,compress_level,nocompress,tempfile,exclude)
    return filter
