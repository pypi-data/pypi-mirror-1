
# Load logging framework
import logging
logger = logging.getLogger(__name__)

# Load Twisted
from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ReconnectingClientFactory

# Load STOMP
import stomper
from stomper import stompbuffer

# Load JSON
from django.utils import simplejson

class Engine(stomper.Engine):
    def __init__(self, protocol, username='', password=''):
        super(Engine, self).__init__()
        self.username = username
        self.password = password
        self.protocol = protocol

    def connect(self):
        return stomper.connect(self.username, self.password)

    def disconnect(self):
        pass

    def do_shutdown(self):
        self.protocol.factory.stopTrying()
        self.protocol.transport.loseConnection()

    def connected(self, msg):
        super(Engine, self).connected(msg)

        logger.info("connected: session %s" % msg['headers']['session'])
        return stomper.NO_RESPONSE_NEEDED

    def subscribe(self, channel):
        f = stomper.Frame()
        f.unpack(stomper.subscribe(channel))
        self.protocol.send_frame(f)

    def unsubscribe(self, channel):
        f = stomper.Frame()
        f.unpack(stomper.unsubscribe(channel))
        self.protocol.send_frame(f)

    def recv(self, msg, headers):
        pass

    def send(self, dst, msg, headers=None):
        self.protocol.send(dst, msg, headers)

    def ack(self, json_msg):
        logger.debug("received raw: %s " % json_msg)
        jmsg = unicode(json_msg['body'], 'utf-8')
        msg = simplejson.loads(jmsg)
        self.recv(msg, json_msg['headers'])
        return stomper.NO_REPONSE_NEEDED

class StompProtocol(Protocol):

    def __init__(self, engine_maker):
        self.engine = engine_maker(protocol=self)
        self.stompBuffer = stompbuffer.StompBuffer()

    def connectionMade(self):
        cmd = self.engine.connect()
        self.transport.write(cmd)

    def connectionLost(self, reason):
        self.engine.disconnect()

    def dataReceived(self, data):
        self.stompBuffer.appendData(data)
        while True:
                msg = self.stompBuffer.getOneMessage()
                if msg is None:
                        break
                returned = self.engine.react(msg)
                if returned:
                    self.transport.write(returned)

    def send_frame(self, frame):
        # ActiveMQ specific headers:
        #
        frame.headers['persistent'] = 'true'
        self.transport.write(frame.pack())
        
    def send(self, dst, msg, headers=None):
        f = stomper.Frame()
        msg = simplejson.dumps(msg)
        msg = msg.encode('utf-8')
        dst = dst.encode('utf-8')
        f.unpack(stomper.send(dst, msg))
        if headers is not None:
                f.headers.update(headers)
        self.send_frame(f)

class StompClientFactory(ReconnectingClientFactory):
    def __init__(self, protocol_maker):
        self.protocol = protocol_maker

    def startedConnecting(self, connector):
        pass

    def buildProtocol(self, addr):
        """Transport level connected now create the communication protocol.
        """
        logger.info('connected to %s' % addr)
        return ReconnectingClientFactory.buildProtocol(self, addr)

    def clientConnectionLost(self, connector, reason):
        """Lost connection
        """
        logger.error('Lost connection.  Reason: %s' % reason)
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        """Connection failed
        """
        logger.error('Connection failed. Reason:' % reason)
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)


def MakeStompProtocolMaker(engine_maker):
    def maker():
        return StompProtocol(engine_maker)
    return maker

def MakeEngineMaker(engine_class, username, password):
        if username is None: username = ''
        if password is None: password = ''

        def maker(protocol):
                return engine_class(protocol=protocol, username=username, password=password)
        return maker

def LaunchStompEngine(engine_maker, stomp_host='localhost', stomp_port=61613, stomp_username='', stomp_password='', ssl=False):
        if ssl: raise NotImplementedError

        engine_factory = MakeEngineMaker( engine_maker, username=stomp_username, password=stomp_password)
        protocol_factory = MakeStompProtocolMaker(engine_factory)
        client_factory = StompClientFactory( protocol_factory )
        return reactor.connectTCP(stomp_host, stomp_port, client_factory)
