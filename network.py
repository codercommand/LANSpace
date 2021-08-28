# network.py is custom networking wrapper that provides a simplified API 
# for broadcasting and receiving broadcasts.
#
# Public API:
#   network.BROADCAST(byte_list)                Broadcasts the byte list to all devices on teh network, including self.
#   network.CATCH() -> byte_list      Returns a byte list from a broadcast on the network.
#
import socket

__60FPS_timeout = 0
# I set the timeout so low that it wouldn't affect FPS

# setdefaulttimeout uses seconds
socket.setdefaulttimeout(__60FPS_timeout) # The socket will timeout after x seconds if it receives no data


_PORT = 8080


# UDP socket binding for broadcasts.
__bsocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
__bsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allows multiple applications to use the same socket.
__bsocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) # Sets the socket binding to broadcats mode.


# UDP socket binding for receiving broadcasts.
__csocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
__csocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allows multiple applications to use the same socket.
__csocket.bind(("0.0.0.0", _PORT))


def BROADCAST(data: bytes) -> None:
    __bsocket.sendto(data, ('255.255.255.255', _PORT))


def CATCH() -> bytes:
    try:
        data, address = __csocket.recvfrom(1024)
    except: # An exception is needed encase there is a timeout error 
        data = None

    return data # We ignore returning the sending address because it's irrelevant.
