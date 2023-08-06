
from twisted.web2.client import http


class HTTPClientChannelRequest(http.HTTPClientChannelRequest):
    """
    """
    def submit(self):
        l = []
        request = self.request
        if request.method == "HEAD":
            # No incoming data will arrive.
            self.length = 0
        
        l.append('%s %s %s\r\n' % (request.method, request.uri,
                                   self.outgoing_version))
        if request.headers is not None:
            for name, valuelist in request.headers.getAllRawHeaders():
                for value in valuelist:
                    l.append("%s: %s\r\n" % (name, value))
        
        if request.stream is not None:
            if request.stream.length is not None:
                l.append("%s: %s\r\n" % ('Content-Length', request.stream.length))
            else:
                # Got a stream with no length. Send as chunked and hope, against
                # the odds, that the server actually supports chunked uploads.
                l.append("%s: %s\r\n" % ('Transfer-Encoding', 'chunked'))
                self.chunkedOut = True

        # EAS: Try doing without this
        # if self.closeAfter:
        #     l.append("%s: %s\r\n" % ('Connection', 'close'))
        # else:
        #     l.append("%s: %s\r\n" % ('Connection', 'Keep-Alive'))
        
        l.append("\r\n")
        self.transport.writeSequence(l)
        
        d = http.stream_mod.StreamProducer(request.stream).beginProducing(self)
        d.addCallback(self._finish).addErrback(self._error)

    ## FIXME: Actually creates Response, function is badly named!
    def createRequest(self):
        print "\ncreateRequest"
        self.stream = http.stream_mod.ProducerStream()
        self.response = http.http.Response(self.code, self.inHeaders, self.stream)
        self.stream.registerProducer(self, True)
        del self.inHeaders

    ## FIXME: Actually processes Response, function is badly named!
    def processRequest(self):
        print "\nprocessRequest"
        self.responseDefer.callback(self.response)



class HTTPClientProtocol(http.HTTPClientProtocol):
    """
    """
    def lineReceived(self, line):
        print "\nlineReceived", line
        if not self.inRequests:
            # server sending random unrequested data.
            self.transport.loseConnection()
            return

        # If not currently writing this request, set timeout
        if self.inRequests[0] is not self.outRequest:
            self.setTimeout(self.inputTimeOut)
            
        if self.firstLine:
            self.firstLine = 0
            self.inRequests[0].gotInitialLine(line)
        else:
            self.inRequests[0].lineReceived(line)

    def rawDataReceived(self, data):
        print "\nrawDataReceived", data
        if not self.inRequests:
            print "Extra raw data!"
            # server sending random unrequested data.
            self.transport.loseConnection()
            return
        
        # If not currently writing this request, set timeout
        if self.inRequests[0] is not self.outRequest:
            self.setTimeout(self.inputTimeOut)
            
        self.inRequests[0].rawDataReceived(data)
        
    def submitRequest(self, request, closeAfter=True):
        """
        @param request: The request to send to a remote server.
        @type request: L{ClientRequest}

        @param closeAfter: If True the 'Connection: close' header will be sent,
            otherwise 'Connection: keep-alive'
        @type closeAfter: C{bool}

        @return: L{twisted.internet.defer.Deferred} 
        @callback: L{twisted.web2.http.Response} from the server.
        """

        # Assert we're in a valid state to submit more
        print "\nsubmitRequest", request, closeAfter
        assert self.outRequest is None
        assert ((self.readPersistent is http.PERSIST_NO_PIPELINE and not self.inRequests)
                or self.readPersistent is http.PERSIST_PIPELINE)
        
        self.manager.clientBusy(self)
        if closeAfter:
            self.readPersistent = False
        
        self.outRequest = chanRequest = HTTPClientChannelRequest(self, request, closeAfter)
        self.inRequests.append(chanRequest)
        
        chanRequest.submit()
        return chanRequest.responseDefer

    def requestWriteFinished(self, request):
        assert request is self.outRequest
        
        self.outRequest = None
        # Tell the manager if more requests can be submitted.
        self.setTimeout(self.inputTimeOut)
        if self.readPersistent is http.PERSIST_PIPELINE:
            self.manager.clientPipelining(self)

    def requestReadFinished(self, request):
        assert self.inRequests[0] is request
        
        del self.inRequests[0]
        self.firstLine = True
        
        if not self.inRequests:
            if self.readPersistent:
                self.setTimeout(None)
                self.manager.clientIdle(self)
            else:
#                 print "No more requests, closing"
                self.transport.loseConnection()

    def setReadPersistent(self, persist):
        self.readPersistent = persist
        if not persist:
            # Tell all requests but first to abort.
            for request in self.inRequests[1:]:
                request.connectionLost(None)
            del self.inRequests[1:]
    
    def connectionLost(self, reason):
        self.readPersistent = False
        self.setTimeout(None)
        self.manager.clientGone(self)
        # Tell all requests to abort.
        for request in self.inRequests:
            if request is not None:
                request.connectionLost(reason)
