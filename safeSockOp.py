from typeguard import typechecked
import socket


class SafeSockException(Exception):
    pass


def safeSockOp(sockOp: callable):
    try:
        return sockOp()
    except BrokenPipeError:
        raise (SafeSockException("connection closed unexpectedly"))
    except socket.timeout:
        raise (SafeSockException("connection timed out"))
    except ConnectionResetError:
        raise (SafeSockException("connection reset"))
