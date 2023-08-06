# Django Preamble
from django.conf import settings

# Load logging framework
import logging
logger = logging.getLogger(__name__)

# Load Twisted/STOMP framework
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from manicscript.twisted.stomp import Engine

# Load Regular Expressions
import re

# Load timestamp methods
from manicscript.jstime import datetime2epoch, epoch2datetime

class DjChatClientEngine(Engine):

    def __init__(self, handle, rooms, *args, **kwargs):
        super(DjChatClientEngine, self).__init__(*args, **kwargs)

        self.handle = handle
        self.rooms = rooms
        self._lc = None

    def connected(self, msg):
        res = super(DjChatClientEngine, self).connected(msg)
        if self.handle is not None:
                self._lc = LoopingCall(self.touch_memberships)
                self._lc.start( settings.DJCHAT_TOUCH_INTERVAL )

        for room in self.rooms:
                if room == '.':
                        chan = settings.DJCHAT_BROADCAST
                else:
                        chan = settings.DJCHAT_ROOM_PREFIX + room
                logger.debug('subscribing to %s' % chan)
                reactor.callLater(0.0, self.subscribe, chan)

        return res

    def disconnect(self):
        if self._lc is not None:
                logger.info('stopping room presence calls')
                self._lc.stop()

    def on_chat(self, timestamp, room, handle, message, extras):
        pass

    def on_whisper(self, timestamp, handle, message, extras):
        pass

    def on_broadcast(self, timestamp, handle, message, extras):
        pass

    def on_join(self, room, handle):
        pass

    def on_part(self, room, handle):
        pass

    def do_chat(self, room, msg, handle=None, timestamp=None, log=True, **extras):
        if handle is None:
                handle = self.handle
        msg = {
                'cmd': 'send',
                'room': room,
                'handle': handle,
                'msg': msg,
                'log': log,
                'extras': extras,
        }
        if timestamp is not None:
                msg['timestamp'] = datetime2epoch(timestamp)
        reactor.callFromThread(self.protocol.send, settings.ECHOCHAMBER_SOURCE, msg)

    def touch_memberships(self):
        for room in self.rooms:
                if room == '.': continue
                msg = {
                        'cmd': 'touch',
                        'room': room,
                        'handle': self.handle,
                }
                logger.debug('touching room %s' % room)
                reactor.callLater(0.0, self.protocol.send, settings.ECHOCHAMBER_SOURCE, msg)
                        
                        
    def recv(self, request, headers):
        # Abort on invalid message
        if 'cmd' not in request:
                logger.error('received invalid request to %s: %s' % (headers['destination'], repr(request)))
                return

        # Unpack message 
        cmd = request['cmd']
        handle = request['handle']
        if cmd in ('chat', 'join', 'part'):
                room = request['room']
        else:
                room = None

        if 'timestamp_int' in request:
                timestamp_int = request['timestamp_int']
                timestamp = epoch2datetime(timestamp_int)
        else:
                timestamp = None
        message = request.get('message', None)
        extras = request.get('extras', {})
        #if cmd in ( 'chat', 'broadcast', 'whisper' ):

        # Handle message
        if cmd == 'chat':
                self.on_chat(timestamp, room, handle, message, extras)
        elif cmd == 'whisper':
                self.on_whisper(timestamp, handle, message, extras)
        elif cmd == 'broadcast':
                self.on_broadcast(timestamp, handle, message, extras)
        elif cmd == 'join':
                self.on_join(room, handle)
        elif cmd == 'part':
                self.on_part(room, handle)

class DjChatCommandEngine(DjChatClientEngine):
        cmd_re = re.compile('^/(?P<handle_glob>(\\w|\\*)+)\\s+(?P<cmd>.*)\\Z')
        def __init__(self, *args, **kwargs):
                super(DjChatCommandEngine,self).__init__(*args, **kwargs)
                from random import choice
                import string
                self._killword = ''.join(choice(string.lowercase + string.digits) for i in range(8))
                self.agents = []

        def register_agent(self, agent):
                self.agents.append(agent)

        def unregister_agent(self,agent):
                self.agents.remove(agent)

        def disconnect(self):
                super(DjChatCommandEngine, self).disconnect()

                # Shut down any registered agents
                for agent in self.agents:
                        agent.do_shutdown()

        def on_cmd(self, timestamp, room, handle, cmd):
                args = cmd.split()
                word = args.pop(0)

                if word == 'load':
                        load_level = self.get_reactor_load()
                        self.do_chat( room, 'reactor load %d' % load_level )
                elif word == 'agents':
                        self.do_chat( room, 'I have %d registered agents' % len(self.agents))
                elif word == 'die':
                        if len(args) == 0:
                                self.do_chat( room, 'kill word: %s' % self._killword )
                        elif args[0] == self._killword:
                                self.do_chat( room, 'dying' )
                                reactor.stop()

        def on_chat(self, timestamp, room, handle, message, extras):
                # Exract a command
                m = self.cmd_re.search(message)
                if not m: return
                line = m.groupdict()

                # Detect commands intended for this engine
                hdl_re = '^' + line['handle_glob'].replace('*', '\\w*?') + '\\Z'
                if re.search(hdl_re, self.handle):
                        self.on_cmd(timestamp, room, handle, line['cmd'])

        def get_reactor_load(self):
                return len(reactor.getDelayedCalls())
