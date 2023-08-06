# Load logging framework
import logging
logger = logging.getLogger(__name__)

# Load timestamp methods
from manicscript.jstime import datetime2epoch, epoch2datetime, datetime

# Load Zope interface infrastructure
from zope.interface import Interface, implements

# Load exceptions
from manicscript.kerby.assertions import ObjectNotYetValid, ObjectExpired, NotAnAddressee, InvalidMessageVerify

# Load crypto methods
from manicscript.kerby.cipher import multimessage_encode, multimessage_peek, multimessage_decode

# K denotes shared secret
# k denotes session key
# T = timestamp
# V = validity period
# A = Alice
# S = Service
# TGT = Ticket Granting Ticket
# TKT = Ticket
# {signed-public-message|private-message}_key

# Service AUTH sequence
# 0 - A -> KDC: A
# 1 - KDC -> A: TGT={A,V|k_A/TGS}_(K_TGS), {TGT|k_A/TGS}_(K_A/KDC)

# Service SESS/PERM sequence
# 0 - A -> KDC: {TGT,A,S,T|}_(k_A/TGS)
# 1 - KDC -> A: TKT={A,S,V|k_A/S}_(K_S/KDC), {TKT|k_A/S}_(k_A/TGS)

# 2 - A -> S: {TKT,T|}_(k_A/S)

class TicketClass(object):
        AUTHENTICATION  = 1 # TGT
        SESSION         = 2 # TKT
        PERMISSION      = 3 # TKT

class PerishableObject(object):
        def from_dicts(self, pub, prv):
                pub = pub.copy()
                pub['valid_from'] = epoch2datetime(pub['valid_from'])
                pub['valid_until'] = epoch2datetime(pub['valid_until'])
                self.load_pub(**pub)
                self.load_prv(**prv)

        def assert_valid(self):
                s=super(PerishableObject, self)
                if hasattr(s, 'assert_valid'): s.assert_valid()

                n = datetime.now()
                if self.valid_from is not None and self.valid_from > n:
                        raise ObjectNotYetValid

                if self.valid_until is not None and self.valid_until < n:
                        raise ObjectExpired

        def load_pub(self, valid_from, valid_until, **kwargs):
                s=super(PerishableObject, self)
                if hasattr(s, 'load_pub'): s.load_pub(**kwargs)
                assert valid_from is None or isinstance(valid_from, datetime), "valid_from should be a datetime object"
                assert valid_until is None or isinstance(valid_until, datetime), "valid_until should be a datetime object"

                self.valid_from = valid_from
                self.valid_until = valid_until

class Secret(object):
        """A shared secret for use in Kerby"""
        def load_prv(self, secret, **kwargs):
                s = super(Secret, self)
                if hasattr(s, 'load_prv'): s.load_prv(**kwargs)
                self.secret = secret

class Ticket(PerishableObject, Secret):
        """A TKT/TGS and its accompanying secret"""
        def load_pub(self, ticket_class, as_principal, for_principal, tkt, session=None, **kwargs):
                s = super(Ticket, self)
                if hasattr(s, 'load_pub'): s.load_pub(**kwargs)
                self.ticket_class = ticket_class
                self.as_principal = as_principal
                self.for_principal = for_principal
                self.session = session
                self.tkt = tkt

def multiticket_encode( msg_pub, msg_prv, tickets ):
        # Prepare secret and ticket tables
        ticket_tab = defaultdict(list)
        for id, ticket in enumerate(tickets):
                tup = (id, ticket.tkt)
                ticket_tab[ticket.as_principal].append(tup)
                ticket_tab[ticket.for_principal].append(tup)
                secret_tab[id] = ticket.secret

        # Encode
        cmsg = multimessage_encode( msg_pub, msg_prv, secret_tab )
        cmsg['_multi_tkt'] = ticket_tab

        return cmsg

def tkt_to_ticket(tkt, ticket_cache, session):
        # Determine the ticket headers
        pub = multimessage_peek(tkt)
        ticket_class = pub['ticket_class']
        as_principal = pub['as_principal']
        for_principal = pub['for_principal']

        # Find a key
        ticket = ticket_cache.getKey(ticket_class, as_principal, for_principal, session)

        # Decode the tkt
        handle = 0
        pub, prv = multimessage_decode(tkt, handle, ticket.secret)

        # Construct the ticket
        ticket = Ticket()
        ticket.from_dicts(pub, prv)
        return ticket

def multiticket_decode( cmsg, ticket_cache, session=None ):
        # Make sure the ticket_cache implements ITicketCache
        assert ITicketCache.implementedBy( ticket_cache ), "ticket_cache must implement ITicketCache"

        # Extract the ticket list
        ident = ticket_cache.getIdentity()
        tkts = cmsg['_multi_tkt'].get(ident, None)
        if tkts is None:
                raise NotAnAddressee

        # Verify tickets
        # We loop over all tickets in order to verify all tickets
        prv_last = None
        first_iter = True
        for id, tkt in tkts:
                # Convert the tkt into a Ticket object, authenticating it
                ticket = tkt_to_ticket(tkt, ticket_cache, session)

                # Impose expiry rules on the ticket
                ticket.assert_valid()

                # Decode and verify the message using the ticket secret
                pub, prv = multimessage_decode( cmsg, id, ticket.secret )

                # Verify that the private message is the same across all 
                if first_iter:
                        prv_last = prv
                        first_iter = False
                if prv_last != prv:
                        raise InvalidMessageVerify

        return pub, prv

class ITicketCache(Interface):
        """Supports caching session keys"""
        def getKey(ticket_class, as_principal, for_principal, session=None):
                """Fetch the ticket/key pair for posing as as_principal to
                   for_principal, consulting optional session parameter session""" 

        def getIdentity():
                """Return the identity string corresponding to the cache owner"""
