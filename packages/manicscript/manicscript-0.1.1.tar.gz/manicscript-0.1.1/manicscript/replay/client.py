
# Django Preamble
from django.conf import settings

# Load logging framework
import logging
logger = logging.getLogger(__name__)

# Load Twisted/STOMP framework
from twisted.internet import reactor

def save_replay(protocol, msg_class, channel, id, body):
        # Prepare a structure to send by JSON/STOMP
        req = {
                'cmd': 'save_replay',
                'class': msg_class,
                'channel': channel,
                'id': id,
                'body': body,
        }

        # Queue the message for transmission
        logging.debug('sending save_replay command for %s:%d' % (channel, id))
        reactor.callLater(0.0, protocol.send, settings.INSTANTREPLAY_SOURCE, req)

def send_replay(protocol, msg_class, channel, destination):
        # Prepare a structure to send by JSON/STOMP
        req = {
                'cmd': 'send_replay',
                'class': msg_class,
                'channel': channel,
                'destination': destination,
        }

        # Queue the message for transmission
        reactor.callLater(0.0, protocol.send, settings.INSTANTREPLAY_SOURCE, req)

def clear_replay(protocol, msg_class, channel, id):
        # Prepare a structure to send by JSON/STOMP
        req = {
                'cmd': 'clear_replay',
                'class': msg_class,
                'channel': channel,
                'id': id,
        }

        # Queue the message for transmission
        logging.debug('sending clear_replay command for %s:%d' % (channel, id))
        reactor.callLater(0.0, protocol.send, settings.INSTANTREPLAY_SOURCE, req)

def clear_replay_class(protocol, msg_class):
        # Prepare a structure to send by JSON/STOMP
        req = {
                'cmd': 'clear_replay_class',
                'class': msg_class,
        }

        # Queue the message for transmission
        reactor.callLater(0.0, protocol.send, settings.INSTANTREPLAY_SOURCE, req)
