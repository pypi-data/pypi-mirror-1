
# Load logging framework
import logging
logger = logging.getLogger(__name__)

# Load Twisted/STOMP framework
from twisted.internet import reactor

class DjChatSession(object):
        @classmethod
        def sessionize(klass, bot, room, handle, session_table=None, **kwa):
                if session_table is None:
                        session_table = bot.sessions

                if (room, handle) not in session_table:
                        logger.info('starting a new %s session in %s for %s' % (klass.__name__, room, handle))
                        session_table[(room, handle)] = klass( bot=bot, room=room, handle=handle, session_table=session_table, **kwa )

                return session_table[(room, handle)]

        def __init__(self, bot, room, handle, session_table, timeout=0):
                self.bot = bot
                self.room = room
                self.handle = handle
                self.timeout = timeout
                self.session_table = session_table

                if timeout > 0:
                        self._timeout = reactor.callLater( self.timeout, self.on_expire )
                else:
                        self._timeout = None


        def say(self, msg):
                msg = '%s: %s' % (self.handle, msg)
                reactor.callFromThread( self.bot.do_chat, self.room, msg)

        def touch(self):
                if self._timeout is not None:
                        if self.timeout > 0:
                                self._timeout.reset(self.timeout)
                        else:
                                self._timeout.cancel()
                                self._timeout = None

        def on_expire(self):
                logger.info('expiring a %s session in %s for %s' % (self.__class__.__name__, self.room, self.handle))
                del self.session_table[(self.room, self.handle)]

        def on_cmd(self, cmd, extras=None):
                pass
