#!/usr/bin/python

# Copyright (c) 2008 Michael Carter
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

import traceback
try:
    from twisted.internet.protocol import Factory, Protocol
except:
    import sys
    print >>sys.stderr, "Twisted required to run; see www.twistedmatrix.com"
    # TODO: does the error code matter more than being non-zero?
    #       -mcarter 8/30/08
    sys.exit(1)
    
FRAME_DELIM = '\0'

class StompProtocol(Protocol):
    def __init__(self):
        self.state = 'initial'
        self.buffer = ""
    
    def dataReceived(self, data):
        self.buffer += data
        while FRAME_DELIM in self.buffer:
            try:
                frameData, self.buffer = self.buffer.split(FRAME_DELIM, 1)
                frame = self.parseFrame(frameData)
                getattr(self, 'read_%s' % self.state)(*frame)
            except Exception, e:
                self.sendError(e)
                break
                #raise e
    
    def parseFrame(self, frameData):
        if frameData[0] == '\n':
            frameData = frameData[1:]
        command, frameData = frameData.split('\n', 1)
        # No headers case
        if frameData.find('\n\n') == -1:
            body = frameData[1:]
            headers = {}
        else:
            headerData, body = frameData.split('\n\n', 1)
            headers = dict([ l.split(':')  for l in headerData.split('\n') ])
        for key, val in headers.items():
            if val.startswith(' '):
                headers[key] = val[1:]
        return (command, headers, body)
    
    def sendError(self, e):
        exception, instance, tb = traceback.sys.exc_info()
        tbOutput= "".join(traceback.format_tb(tb))      
        self.sendFrame('ERROR', {'message': str(e) }, tbOutput)
    
    def sendFrame(self, cmd, headers, body):
        output = cmd + '\n'
        output += '\n'.join([ str(k) + ': ' + str(v) for (k, v) in headers.items() ]) + '\n\n'
        output += body + FRAME_DELIM
        self.transport.write(output)
    
    def read_initial(self, cmd, headers, body):
        assert cmd.lower() == 'connect', "Invalid cmd: expected CONNECT"
        self.state = 'connected'
        self.sendFrame('CONNECTED', {}, "")
    
    def read_connected(self, cmd, headers, body):
        return getattr(self, 'frame_%s' % cmd.lower())(headers, body)
    
    def frame_subscribe(self, headers, body):        
        self.factory.subscribe(self, headers['destination'])
    
    def frame_unsubscribe(self, headers, body):
        self.factory.unsubscribe(self, headers['destination'])
    
    def frame_send(self, headers, body):
        self.factory.send(headers['destination'], body)
    
    def frame_disconnect(self, headers, body):
        self.transport.loseConnection()
    
    def connectionLost(self, reason):
        self.factory.gone(self)
        


class StompFactory(Factory):
    
    def __init__(self):
        self.topics = {}
        self.id = 0
        
    def subscribe(self, proto, topicName):
        if topicName not in self.topics:
            self.topics[topicName] = []
        if proto not in self.topics[topicName]:
            self.topics[topicName].append(proto)
            
    def unsubscribe(self, proto, topicName):
        if proto in self.topics[topicName]:
            self.topics[topicName].remove(proto)
        else:
            return "error"
        if not self.topics[topicName]:
            del self.topics[topicName]
    
    
    def gone(self, proto):
        # TODO: Don't run in n^(n^7) time.
        #       (or keep this memory optimization in place)
        #       -mcarter 8/30/2008
        for subscribers in self.topics.values():
            if proto in subscribers:
                subscribers.remove(proto)
    
    def send(self, dest, body):
        self.id+=1
        id = self.id
        for subscriber in self.topics[dest]:
            subscriber.sendFrame('MESSAGE', {'dest': dest, 'message-id': id}, body)
        
    protocol = StompProtocol



def main(): 
    from optparse import OptionParser
    import sys
    parser = OptionParser()
    parser.add_option(
        "-p",
        "--port",
        dest="port",
        type="int",
        default=61613,
        help="listening port value"
    )
    parser.add_option(
        "-i",
        "--interface",
        dest="interface",
        type="string",
        default="",
        help="hostname the daemon should bind to (default: all interfaces)"
    )
    
    (options, args) = parser.parse_args(sys.argv)
    from twisted.internet import reactor
    reactor.listenTCP(options.port, StompFactory(), interface=options.interface)
    print "Starting Morbid Stomp server @ stomp://" + options.interface+ ":" + str(options.port)
    reactor.run()
    
if __name__ == "__main__":
    main()