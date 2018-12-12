DEF_IP = '127.0.0.1'
DEF_PORT = 55175
DEF_BUFFER_SIZE = 1024

DEF_ESC = '+'
DEF_SEP = '$'
DEF_EOM = '*'


from .logMessage import LogMessage
from .parser import Parser
from .safeSockOp import safeSockOp, SafeSockException
from .server import Server
from .stls import run, main

__all__ = ["Server", "Parser", "LogMessage", "safeSockOp", "SafeSockException", "run", "main"]
