
# Django Preamble
from django.conf import settings

# Load logging framework
import logging
logger = logging.getLogger(__name__)

# Load Twisted/STOMP framework
from twisted.internet import reactor
from manicscript.twisted.stomp import StompClientFactory, MakeStompProtocolMaker, MakeEngineMaker, Engine
from manicscript.djchat.client import DjChatCommandEngine

# Declare global variables
_cache = {}

class InvalidReplayCommandException(Exception):
        pass

class InstantReplay(Engine):

        def connected(self, msg):
                res = super(InstantReplay, self).connected(msg)
                reactor.callLater(0.0, self.subscribe, settings.INSTANTREPLAY_SOURCE)
                return res

        def recv(self, request, headers):
                # Determine control command type
                cmd = request['cmd']
                if cmd == 'save_replay':
                        return self.on_save_replay(request, headers)
                elif cmd == 'send_replay':
                        return self.on_send_replay(request, headers)
                elif cmd == 'clear_replay':
                        return self.on_clear_replay(request, headers)
                elif cmd == 'clear_replay_class':
                        return self.on_clear_replay_class(request, headers)
                else:
                        logger.error('Invalid command type: %s' % cmd)

        def on_save_replay(self, request, headers):
                global _cache

                # Extract parameters
                msg_class = request['class'] # djchat/puzzlegrid
                msg_channel = request['channel'] # original destination
                msg_id = request['id'] # id of message (used in comparison)
                msg_body = request['body'] # message to be replayed

                # Get the class-specific cache
                cache_class = _cache.setdefault(msg_class, {})

                # Get the channel-specific cache
                cache_channel = cache_class.setdefault(msg_channel, {})

                # Save the cache record
                cache_channel[msg_id] = msg_body

                logger.debug('[%s] saving %s:%d' % (msg_class, msg_channel, msg_id))

        def on_send_replay(self, request, headers):
                global _cache

                # Extract parameters
                msg_class = request['class'] # djchat/puzzlegrid
                msg_channel = request['channel'] # original destination
                msg_destination = request['destination'] # replay destination

                # Get the class-specific cache
                cache_class = _cache.setdefault(msg_class, {})

                # Get the channel-specific cache
                cache_channel = cache_class.setdefault(msg_channel, {})
                if len(cache_channel) == 0: return

                # Get the id list in order
                ids = sorted(cache_channel.keys())

                # Prepare a delayed call to send replay
                reactor.callLater(0.0, map, self.protocol.send, *zip(*[(msg_destination, cache_channel[id]) for id in ids]))

        def on_clear_replay(self, request, headers):
                global _cache

                # Extract parameters
                msg_class = request['class'] # djchat/puzzlegrid
                msg_channel = request['channel'] # original destination
                msg_id = request['id'] # id of message (used in comparison)

                # Get the class-specific cache
                cache_class = _cache.setdefault(msg_class, {})

                # Get the channel-specific cache
                cache_channel = cache_class.setdefault(msg_channel, {})

                # Remove the requested message from the cache
                logger.debug('[%s] clearing %s:%d' % (msg_class, msg_channel, msg_id))
                del cache_channel[msg_id]

        def on_clear_replay_class(self, request, headers):
                global _cache

                # Extract parameters
                msg_class = request['class'] # djchat/puzzlegrid

                # Get the class-specific cache
                cache_class = _cache.setdefault(msg_class, {})

                # Generate warnings if appropriate
                cache_channels = len(cache_class)
                cache_lines = sum([len(chan) for chan in cache_class.values()])
                logging.warn('dropping %d messages in %d channels from cache class %s'
                             % (cache_lines, cache_channels, msg_class))

                # Clear the class-specific cache
                _cache[msg_class] = {}
                logging.info('clearing replay cache class %s' % msg_class)

class InstantReplayCommand(DjChatCommandEngine):
        pass

def start(host='localhost', port=61613, username=None, password=None):
    """Start twisted event loop and the fun should begin...
    """
    # Launch InstantReplay
    engine_maker = MakeEngineMaker(InstantReplay, username, password)
    protocol_maker = MakeStompProtocolMaker(engine_maker)
    factory = StompClientFactory( protocol_maker )
    reactor.connectTCP(host, port, factory)

    # Launch command engine
    engine_maker = MakeEngineMaker(
                        lambda *a, **kwa:
                                DjChatCommandEngine(
                                        'InstantReplayCmd', settings.CONTROL_ROOMS, *a, **kwa),
                        username, password)
    protocol_maker = MakeStompProtocolMaker(engine_maker)
    factory = StompClientFactory( protocol_maker )
    reactor.connectTCP(host, port, factory)

    # Run
    reactor.run()

def main(       host=settings.STOMP_HOSTS[0][0],
                port=settings.STOMP_HOSTS[0][1],
                username=settings.STOMP_USERNAME,
                password=settings.STOMP_PASSWORD ):
        port = int( port )
        start( host=host, port=port, username=username, password=password )

if __name__ == '__main__':
        main()
