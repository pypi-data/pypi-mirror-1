# twisted_goodies.simpleserver.http:
# A virtual hosting twisted.web2 HTTP server that uses subdirectories for
# virtual host content. Subdirectories can be python packages providing dynamic
# content with a root resource object, or sources of static content.
#
# Copyright (C) 2006-2007 by Edwin A. Suominen, http://www.eepatents.com
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the file COPYING for more details.
# 
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA


"""
A non-blocking container resource for WSGI web applications.
"""

import os, threading, sys
import Queue
from zope.interface import implements

from twisted.internet import defer, interfaces, reactor
from twisted.python import log, failure
from twisted.web2 import http, http_headers
from twisted.web2 import iweb, server, stream, resource
from twisted.web2.twcgi import createCGIEnvironment

from asynqueue import ThreadQueue


VERBOSE = False
MAX_PENDING = 10
IP_BAN_SECS = 30.0


class AlreadyStartedResponse(Exception):
    pass


class WSGIMeta(type):
    """
    """
    def __new__(mcls, name, bases, dictionary):
        if not hasattr(mcls, 'globalStuff'):
            gs = mcls.globalStuff = {}
            # Just use one worker in one thread for now            
            gs['queue'] = ThreadQueue(1)
            gs['pending'] = 0
            gs['handlers'] = []
            gs['banned'] = {}
        for name, value in mcls.globalStuff.iteritems():
            dictionary[name] = value
        newClass = super(WSGIMeta, mcls).__new__(mcls, name, bases, dictionary)
        return newClass


class TracerMixin(object):
    """
    Mix me in to trace problems
    """
    isTracing = False
    traceFrame = None
    traceStack = [
        # Bottom frame on up, just like a stack...
        ('cache.py', 'get_changes'),
        ('changeset.py', 'get_changes'),
        ('changeset.py', '_render_html')
        ]
    traceLevels = 5
    
    def settrace(self):
        """
        Call this method to start tracing. If you're using threads, you must
        call it within the same thread whose execution you want to trace.
        """
        sys.settrace(self.trace)
        self.isTracing = True

    def trace(self, frame, event, arg):
        """
        This is the actual trace function.
        """
        def msg(level):
            values = ["." * level]
            values.extend([
                getattr(frame.f_code, "co_%s" % x)
                for x in ('filename', 'firstlineno', 'name')])
            if values != getattr(self, '_prevMsgValues', None):
                self._prevMsgValues = values
                print "%s %s (%04d): %s" % tuple(values)

        def isTraceEntry(k, thisFrame):
            if thisFrame.f_code.co_name == self.traceStack[k][1]:
                tail = "/%s" % self.traceStack[k][0]
                if thisFrame.f_code.co_filename.endswith(tail):
                    return True

        def frameGenerator(N):
            nextFrame = frame
            for k in xrange(N):
                yield k, nextFrame
                nextFrame = nextFrame.f_back

        if not self.isTracing:
            return
        if event == 'call':
            level = 1
            if self.traceFrame is None:
                N = len(self.traceStack)
                for k, thisFrame in frameGenerator(N):
                    if not isTraceEntry(k, thisFrame):
                        return
                else:
                    print "-" * 40
                    self.traceFrame = frame
            else:
                for k, thisFrame in frameGenerator(self.traceLevels):
                    level += 1
                    if thisFrame in (None, self.traceFrame):
                        break
                else:
                    return
            msg(level)
            return self.trace
        elif event == 'return' and frame == self.traceFrame:
            self.traceFrame = None
            print "->", arg


class WSGIResource(TracerMixin, object):
    """
    A web2 Resource which wraps the given WSGI application callable.

    The WSGI application will be called in a separate thread (using
    the reactor threadpool) whenever a request for this resource or
    any lower part of the url hierarchy is received.

    This isn't a subclass of resource.Resource, because it shouldn't do any
    method-specific actions at all. All that stuff is totally up to the
    contained wsgi application
    """
    __metaclass__ = WSGIMeta

    implements(iweb.IResource, interfaces.IFinishableConsumer)

    def __init__(self, application):
        self.application = application
        self.queue.subscribe(self)

    def renderHTTP(self, req):
        def done(result, IP):
            if not result or isinstance(result, failure.Failure):
                if VERBOSE:
                    print "Failed request from %s" % IP
                self.banIP(IP)
            if handler in self.handlers:
                self.handlers.remove(handler)
                
        # Do stuff with WSGIHandler
        IP = req.remoteAddr.host
        if IP in self.banned:
            return self.denial()
        handler = WSGIHandler(self.application, req)
        self.handlers.append(handler)
        # Queue it up for running in the thread
        if self.isTracing:
            d = defer.succeed(None)
        else:
            d = self.queue.call(self.settrace)
        d.addCallback(lambda _: self.queue.call(handler.run))
        d.addBoth(done, IP)
        # We get the result piecemeal from this method call's unique handler,
        # not in some single result of the run method. So there's no need to do
        # anything with the deferred from the queuing call. We can queue some
        # more requests right away if we want.
        return handler.responseDeferred

    def banIP(self, IP):
        """
        Temporarily bans the specified IP address from making connections.
        """
        if IP in self.banned:
            d, delayedCall = self.banned[IP]
            delayedCall.cancel()
            d.callback(IP)
        d = defer.Deferred()
        d.addCallback(self.banned.pop)
        delayedCall = reactor.callLater(IP_BAN_SECS, d.callback, IP)
        self.banned[IP] = d, delayedCall
    
    def denial(self):
        title = "Access Denied"
        html  = "<html>"
        html += "<head><title>%s</title></head>" % title
        html += "<body>"
        html += "<h1>%s</h1>" % title
        html += "<p>Access from your IP has been temporarily denied</p>"
        html += "</body></html>"
        return http.Response(
            200,
            {'content-type': http_headers.MimeType('text', 'html')}, html)
    
    def locateChild(self, request, segments):
        return self, server.StopTraversal

    def registerProducer(self, producer, streaming):
        pass

    def unregisterProducer(self):
        pass

    @classmethod
    def write(cls, new):
        old = cls.pending
        cls.pending = new
        if VERBOSE and new != old:
            print "Pending: %02d -> %02d" % (old, new)
        if new > MAX_PENDING and cls.handlers:
            if new > min([old, 2*MAX_PENDING]):
                oldestHandler = cls.handlers.pop(0)
                if VERBOSE:
                    print "Stopping handler:", oldestHandler
                oldestHandler.stopProducing()

    def finish(self):
        while self.handlers:
            handler = self.handlers.pop(0)
            handler.inputStream.close()
        del self.application


class FinishableBufferedStream(stream.BufferedStream):
    """
    """
    def __init__(self, stream):
        self.running = True
        super(FinishableBufferedStream, self).__init__(stream)

    def _readUntil(self, f):
        """
        Non-borked internal helper function which repeatedly calls f each
        time after more data has been received, until it returns non-None.
        """
        while self.running:
            r = f()
            if r is not None:
                yield r; return
            
            newdata = self.stream.read()
            if isinstance(newdata, defer.Deferred):
                newdata = defer.waitForDeferred(newdata)
                yield newdata
                newdata = newdata.getResult()
            
            if newdata is None:
                # End Of File
                newdata = self.data
                self.data = ''
                yield newdata
                return
            self.data += str(newdata)
    _readUntil = defer.deferredGenerator(_readUntil)
    
    def finish(self):
        self.stream.finish()
        self.running = False


class InputStream(object):
    """
    This class implements the 'wsgi.input' object. The methods are
    expected to have the same behavior as the same-named methods for
    python's builtin file object.
    """
    def __init__(self, newstream):
        # Called in IO thread
        self.stream = FinishableBufferedStream(newstream)
        
    def callInReactor(self, f, *args, **kw):
        """
        Read a line, delimited by a newline. If the stream reaches EOF
        or size bytes have been read before reaching a newline (if
        size is given), the partial line is returned.

        COMPATIBILITY NOTE: the size argument is excluded from the
        WSGI specification, but is provided here anyhow, because
        useful libraries such as python stdlib's cgi.py assume their
        input file-like-object supports readline with a size
        argument. If you use it, be aware your application may not be
        portable to other conformant WSGI servers.
        """
        def call(queue):
            result = defer.maybeDeferred(f, *args, **kw)
            result.addBoth(queue.put)

        from twisted.internet import reactor
        queue = Queue.Queue()
        reactor.callFromThread(call, queue)
        result = queue.get()
        if isinstance(result, failure.Failure):
            result.raiseException()
        return result
        
    def read(self, size=None):
        """
        Read at most size bytes from the input, or less if EOF is
        encountered. If size is ommitted or negative, read until EOF.
        """
        # Called in application thread
        if size < 0:
            size = None
        result = self.callInReactor(self.stream.readExactly, size)
        return result

    def readline(self):
        # Called in application thread
        line = self.callInReactor(self.stream.readline, '\n')
        if line is not None:
            line += '\n'
        return line
    
    def readlines(self, hint=None):
        """
        Read until EOF, collecting all lines in a list, and returns
        that list. The hint argument is ignored (as is allowed in the
        API specification)
        """
        # Called in application thread
        data = self.read()
        lines = data.split('\n')
        last = lines.pop()
        lines = [s+'\n' for s in lines]
        if last != '':
            lines.append(last)
        return lines

    def finish(self):
        """
        Call this if this input stream is backing things up too much.
        """
        if VERBOSE:
            print "Closing laggard input stream..."
        self.stream.finish()

    def __iter__(self):
        """
        Returns an iterator, each iteration of which returns the
        result of readline(), and stops when readline() returns an
        empty string.
        """
        while True:
            line = self.readline()
            if not line:
                return
            yield line

    
class ErrorStream(object):
    """
    This class implements the 'wsgi.error' object.
    """
    def flush(self):
        # Called in application thread
        return

    def write(self, s):
        # Called in application thread
        log.msg("WSGI app error: "+s, isError=True)

    def writelines(self, seq):
        # Called in application thread
        s = ''.join(seq)
        log.msg("WSGI app error: "+s, isError=True)


class WSGIHandler(object):
    """
    """
    implements(interfaces.IPushProducer)

    # This use of class attributes is confusing, IMHO...
    headersSent = False
    stream = None
    
    def __init__(self, application, request):
        # Called in IO thread
        self.setupEnvironment(request)
        self.application = application
        self.request = request
        self.response = None
        self.responseDeferred = defer.Deferred()

    def setupEnvironment(self, request):
        """
        """
        # A cancellable input stream
        self.inputStream = InputStream(request.stream)
        
        # Called in IO thread
        env = createCGIEnvironment(request)
        env['wsgi.version']      = (1, 0)
        env['wsgi.url_scheme']   = env['REQUEST_SCHEME']
        env['wsgi.input']        = self.inputStream
        env['wsgi.errors']       = ErrorStream()
        env['wsgi.multithread']  = True
        env['wsgi.multiprocess'] = False
        env['wsgi.run_once']     = False
        env['wsgi.file_wrapper'] = FileWrapper
        self.environment = env
        
    def startWSGIResponse(self, status, response_headers, exc_info=None):
        """
        """
        # Called in application thread
        if exc_info is not None:
            try:
                if self.headersSent:
                    raise exc_info[0], exc_info[1], exc_info[2]
            finally:
                exc_info = None
        elif self.response is not None:
            raise AlreadyStartedResponse, 'startWSGIResponse(%r)' % status
        status = int(status.split(' ')[0])
        self.response = http.Response(status)
        for key, value in response_headers:
            self.response.headers.addRawHeader(key, value)
        return self.write

    def run(self):
        """
        """
        self.ok = True
        from twisted.internet import reactor
        # Called in application thread
        try:
            result = self.application(self.environment, self.startWSGIResponse)
            self.handleResult(result)
        except:
            if not self.headersSent:
                reactor.callFromThread(self.__error, failure.Failure())
            else:
                reactor.callFromThread(self.stream.finish, failure.Failure())
        return self.ok

    def __callback(self):
        # Called in IO thread
        self.responseDeferred.callback(self.response)
        self.responseDeferred = None

    def __error(self, f):
        # Called in IO thread
        self.responseDeferred.errback(f)
        self.responseDeferred = None
            
    def write(self, output):
        # Called in application thread
        from twisted.internet import reactor
        if self.response is None:
            raise RuntimeError(
                "Application didn't call startResponse before writing data!")
        if not self.headersSent:
            self.stream = self.response.stream = stream.ProducerStream()
            self.headersSent = True
            
            # Threadsafe event objects to communicate paused state.
            self.unpaused = threading.Event()
            
            # After this, we cannot touch self.response from this
            # thread any more
            def _start():
                # Called in IO thread
                self.stream.registerProducer(self, True)
                self.__callback()
                # Notify application thread to start writing
                self.unpaused.set()
            reactor.callFromThread(_start)
        # Wait for unpaused to be true
        self.unpaused.wait()
        reactor.callFromThread(self.stream.write, output)

    def writeAll(self, result):
        # Called in application thread
        from twisted.internet import reactor
        if not self.headersSent:
            if self.response is None:
                raise RuntimeError(
                    "Application didn't call startResponse before "+\
                    "writing data!")
            length = 0
            for item in result:
                length += len(item)
            self.response.stream = stream.ProducerStream(length=length)
            self.response.stream.buffer = list(result)
            self.response.stream.finish()
            reactor.callFromThread(self.__callback)
        else:
            # Has already been started, cannot replace the stream
            def _write():
                # Called in IO thread
                for s in result:
                    self.stream.write(s)
                self.stream.finish()
            reactor.callFromThread(_write)
            
    def handleResult(self, result):
        # Called in application thread
        try:
            from twisted.internet import reactor
            if (isinstance(result, FileWrapper) and 
                   hasattr(result.filelike, 'fileno') and
                   not self.headersSent):
                if self.response is None:
                    raise RuntimeError(
                        "Application didn't call startResponse before "+\
                        "writing data!")
                self.headersSent = True
                # Make FileStream and output it. We make a new file
                # object from the fd, just in case the original one
                # isn't an actual file object.
                self.response.stream = stream.FileStream(
                    os.fdopen(os.dup(result.filelike.fileno())))
                reactor.callFromThread(self.__callback)
                return

            if type(result) in (list,tuple):
                # If it's a list or tuple (exactly, not subtype!),
                # then send the entire thing down to Twisted at once,
                # and free up this thread to do other work.
                self.writeAll(result)
                return
            
            # Otherwise, this thread has to keep running to provide the
            # data.
            for data in result:
                self.write(data)
            
            if not self.headersSent:
                if self.response is None:
                    raise RuntimeError(
                        "Application didn't call startResponse, and didn't "+\
                        "send any data!")
                
                self.headersSent = True
                reactor.callFromThread(self.__callback)
            else:
                reactor.callFromThread(self.stream.finish)
                
        finally:
            if hasattr(result,'close'):
                result.close()

    def pauseProducing(self):
        # Called in IO thread
        self.unpaused.set()

    def resumeProducing(self):
        # Called in IO thread
        self.unpaused.clear()
        
    def stopProducing(self):
        """
        Call this if this WSGI call is backing things up too much or has some
        other connection problem that causes it to terminate prematurely.
        """
        self.ok = False
        if self.inputStream:
            self.inputStream.finish()
        if self.stream:
            self.stream.finish()


class FileWrapper(object):
    """
    Wrapper to convert file-like objects to iterables, to implement
    the optional 'wsgi.file_wrapper' object.
    """
    def __init__(self, filelike, blksize=8192):
        self.filelike = filelike
        self.blksize = blksize
        if hasattr(filelike,'close'):
            self.close = filelike.close
            
    def __iter__(self):
        return self
        
    def next(self):
        data = self.filelike.read(self.blksize)
        if data:
            return data
        raise StopIteration


__all__ = ['WSGIResource']
