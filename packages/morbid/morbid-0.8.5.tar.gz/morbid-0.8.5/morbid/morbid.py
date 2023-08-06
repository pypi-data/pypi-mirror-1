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
import stomper
import mqsecurity
from messagequeue import QueueError

def error(msg):
    print "MorbidQ Error:",msg
    import sys
    sys.exit(-1)

def report(msg):
    print "MorbidQ:",msg

try:
    from twisted.internet.protocol import Factory, Protocol
except:
    error("Twisted required to run; see www.twistedmatrix.com")

class StompProtocol(Protocol):
    id = 0
    def __init__(self):
        self.state = 'initial'
        self.buffer = ""
        self.stompBuffer = stomper.stompbuffer.StompBuffer()
        self.lastNull = False
        StompProtocol.id += 1
        self.id = StompProtocol.id
        self.avatar = None
        
    def get_groups(self):
        return self.avatar.groups
        
    def dataReceived(self, data):
        # NOTE: Allow each frame to have an optional '\n'
        # NOTE: binary DOES NOT WORK with this hack in place
        self.stompBuffer.appendData(data.replace('\0', '\0\n'))

        while True:
            msg = self.stompBuffer.getOneMessage()
            
            # NOTE: the rest of the optional '\n' hack
            if self.stompBuffer.buffer.startswith('\n'):
                self.stompBuffer.buffer = self.stompBuffer.buffer[1:]
                
            if msg is None:
                break
            if not msg['headers'] and not msg['body'] and not msg['cmd']:
                break
            getattr(self, 'read_%s' % self.state)(**msg)

    def sendError(self, e):
        exception, instance, tb = traceback.sys.exc_info()
        tbOutput= "".join(traceback.format_tb(tb))      
        self.sendFrame('ERROR', {'message': str(e) }, tbOutput)
    
    def sendFrame(self, cmd, headers, body):
        f = stomper.Frame()
        f.cmd = cmd
        f.headers.update(headers)
        f.body = body
        self.transport.write(f.pack())
    
    def read_initial(self, cmd, headers, body):
        assert cmd.lower() == 'connect', "Invalid cmd: expected CONNECT"
        d = None
        if self.factory.mq_portal:
            d = self.factory.mq_portal.stomp_login(**headers)
        if d:
            d.addCallback(self.stomp_connected).addErrback(self.stomp_disconnect)
        else:
            self.stomp_connected((IConnector, Connector("None", ["None"]), lambda: None))

    def stomp_connected(self, *args):
        avatarInterface, avatar, logout_func = args[0]
        self.avatar = avatar
        self.state = 'connected'
        self.sendFrame('CONNECTED', {"session": self.id}, "")
        
    def stomp_disconnect(self, *args):
        self.sendFrame('ERROR', {'message': "Invalid ID or password"}, "Invalid ID or password")
        self.transport.loseConnection()
        
    def read_connected(self, cmd, headers, body):
        return getattr(self, 'frame_%s' % cmd.lower())(headers, body)
    
    def frame_subscribe(self, headers, body):
        try:
            self.factory.mqm.subscribe_queue(self, headers['destination'])
        except QueueError, err:
            self.sendFrame('ERROR',
                           {'message': self.get_message_code(err.code)},
                           self.get_message_text(err.code))
    
    def frame_unsubscribe(self, headers, body):
        self.factory.mqm.leave_queue(self, headers['destination'])
    
    def frame_send(self, headers, body):
        try:
            result = self.factory.mqm.send_message(self, headers['destination'], (headers, body))
        except QueueError, err:
            self.sendFrame('ERROR',
                           {'message': self.get_message_code(err.code)},
                           self.get_message_text(err.code))
    
    def frame_disconnect(self, headers, body):
        self.transport.loseConnection()
    
    def connectionLost(self, reason):
        self.factory.disconnected(self)

    def get_message_code(self, code):
        return {'FAILC': "CREATE error",
                'FAILR': "READ error",
                'FAILW': "WRITE error"}[code]
    
    def get_message_text(self, code):
        return {'FAILC': "Not authorized to create queue",
                'FAILR': "Not authorized to read queue",
                'FAILW': "Not authorized to write to queue"}[code]
        
    def send(self, message):
        '''
        This method is invoked by the message queues.
        Not intended for direct use by the protocol.
        '''
        headers, body = message
        self.sendFrame('MESSAGE', headers, body)      

    def connectionLost(self, *a):
        self.factory.disconnected(self)

class StompFactory(Factory):
    """
    The StompFactory creates an instance of a StompProtocol for each connection.
    Successful authentication results in the creation of an avatar for that user.
    The Avatar is assigned to the StompProtocol.
    """
    protocol = StompProtocol
    
    def __init__(self, mqm=None, filename=None):
        self.id = 0
        if mqm:
            self.mqm = mqm
        else:
            import messagequeue
            self.mqm = messagequeue.MessageQueueManager()
            self.mq_portal = mqsecurity.MQPortal(self.mqm, filename=filename)
        
    def disconnected(self, proto):
        self.mqm.unsubscribe_all_queues(proto)

def load_config(config_file, config_dict):
    import os
    if not os.path.isfile(config_file):
        error('config file "%s" does not exist'%(config_file,))
    f = open(config_file)
    lines = f.readlines()
    f.close()
    for line in lines:
        if "=" not in line:
            error('error parsing config. line: "%s"'%(line,))
        report('loading config option: "%s"'%(line,))
        option, value = line.split("=",1)
        config_dict[option.strip()] = value.strip()

def get_stomp_factory(config_file=""):
    config_dict = {'auth':None}
    if config_file:
        load_config(config_file, config_dict)
    return StompFactory(filename=config_dict['auth'])

def main(): 
    from optparse import OptionParser
    import sys
    parser = OptionParser()
    parser.add_option(
        "-c",
        "--config",
        dest="config",
        type="string",
        default="",
        help="configuration file"
    )
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
    parser.add_option(
        "-a",
        "--auth",
        dest="auth",
        type="string",
        default="",
        help="local path to authentication module"
    )
    
    (options, args) = parser.parse_args(sys.argv)
    
    if options.config:
        load_config(options.config, options)
    
    # TODO: implement remote authentication!
    from twisted.internet import reactor
    
    stomp_factory = StompFactory(filename=options.auth)
    
    reactor.listenTCP(options.port, stomp_factory, interface=options.interface)
    print "Starting Morbid Stomp server @ stomp://" + options.interface+ ":" + str(options.port)
    print "using Security configuration file :", options.security
    reactor.run()
    
if __name__ == "__main__":
    main()