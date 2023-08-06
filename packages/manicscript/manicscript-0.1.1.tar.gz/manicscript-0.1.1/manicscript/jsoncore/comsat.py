# Import Django settings
from django.conf import settings

# Import STOMP library
import stomp

# Import JSON tools
from django.utils import simplejson as json

comsat_link = None

def start():
    global comsat_link
    comsat_link = stomp.Connection(
        host_and_ports=settings.STOMP_HOSTS,
        user=settings.STOMP_USERNAME,
        passcode=settings.STOMP_PASSWORD,
    )
    comsat_link.start()
    comsat_link.connect()

def send(destination, data):
        global comsat_link

        # Connect to the STOMP server if necessary
        if comsat_link is None:
                start()

        # Prepare the message for transmission
        msg = json.dumps(data)

        # Send the message
        comsat_link.send(msg, destination=destination)

        # Operation Complete!
