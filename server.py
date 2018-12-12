from typeguard import typechecked
from enum import Enum
import os, socket, threading, gzip, datetime

import stls
from stls import LogMessage, Parser, safeSockOp, SafeSockException


class Server:
    """Sel TCP logging server. Used to log Sel messages over TCP."""

    def __init__(self, ip = stls.DEF_IP, port = stls.DEF_PORT, logDir = stls.DEF_LOG_DIR, bufferSize = stls.DEF_BUFFER_SIZE):
        self.addr = (ip, port)
        self.bufferSize = bufferSize
        self.logDir = logDir
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.parser = Parser()
        self.logFileOp = False
        self.openLogFile()
    
    def __del__(self):
        self.logFile.close()

    def init(self):
        self.s.bind(self.addr)
        self.s.listen(5)
        print(f"Listening on {self.addr}")

    def openLogFile(self):
        while self.logFileOp:
            pass
        self.logFileOp = True

        if not self.logFileWritable():
            if not os.path.exists(f"{self.logDir}"):
                os.mkdir(f"{self.logDir}")

            self.logFile = open(f"{self.logDir}/stls.log", "a")

        size = os.path.getsize(f"{self.logDir}/stls.log")

        if size > 2**20:
            print("Creating archive!")
            self.logFile.close()
            with open(f"{self.logDir}/stls.log", 'r') as lf:
                with gzip.open(f"{self.logDir}/stls-{datetime.datetime.today().isoformat()}.log.gz", 'wb') as ar:
                    ar.write(bytes(lf.read(), "utf-8"))

            open(f"{self.logDir}/stls.log", 'w').close()
            self.logFile = open(f"{self.logDir}/stls.log", "a")            
        
        self.logFileOp = False
    
    def logFileWritable(self):
        return hasattr(self, "logFile") and self.logFile.writable()

    def serve(self):
        lSocket, addr = self.s.accept()
        lSocket.settimeout(20)
        thread = threading.Thread(target=self.handleConn, args=(lSocket, addr))
        thread.start()

    def serveForever(self):
        while True:
            self.serve()

    class ConnIndicator(Enum):
        OPEN = "+"
        CLOSE = "-"
        INFO = "*"
        LOG = ">"
        PARSERERR = "!"

    def logConnMsg(self, indicator: chr, addr: tuple, msg: str):
        print(f"{indicator.value} {addr}: {msg}")

    def handleConn(self, lSocket: socket.socket, addr: tuple):
        self.logConnMsg(Server.ConnIndicator.OPEN, addr, "connection opened")

        unfinishedPart = ""
        unfinishedGroup = []

        while True:
            raw = ()
            err = None
            try:
                raw = safeSockOp(lambda: lSocket.recv(self.bufferSize))
            except SafeSockException as err:
                self.logConnMsg(Server.ConnIndicator.INFO, addr, err)
                break
            else:
                if not raw:
                    break

                socketErrLogged = False
                for rawLogRet in self.rawLog(raw, unfinishedPart, unfinishedGroup):
                    if not rawLogRet.done:
                        if rawLogRet.err is not None:
                            msg = rawLogRet.err
                            self.logConnMsg(
                                Server.ConnIndicator.PARSERERR, addr, rawLogRet.err
                            )
                        else:
                            msg = "ok"
                            self.logConnMsg(
                                Server.ConnIndicator.LOG, addr, rawLogRet.logMessage.asString()
                            )

                        try:
                            safeSockOp(lambda: lSocket.send(bytes(msg, "utf-8")))
                        except SafeSockException as err:
                            # No need to double-log
                            if socketErrLogged:
                                self.logConnMsg(Server.ConnIndicator.INFO, addr, err)
                                socketErrLogged = True

                    else:
                        unfinishedPart = rawLogRet.unfinishedPart
                        unfinishedGroup = rawLogRet.unfinishedGroup
                        break

        self.logConnMsg(Server.ConnIndicator.CLOSE, addr, "connection closed")

    class RawLogRet:
        def __init__(self, done, err, logMessage="", unfinishedPart="", unfinishedGroup=""):
            self.done = done
            self.err = err
            self.logMessage = logMessage
            self.unfinishedPart = unfinishedPart
            self.unfinishedGroup = unfinishedGroup

    def rawLog(
        self, raw: bytes, unfinishedPart: str = "", unfinishedGroup: list = None
    ):
        if unfinishedGroup is None:
            unfinishedGroup = []

        data = raw.decode("utf-8")
        data = data.strip(" \t\n\r")  # Remove leading and trailing line breaks / spaces
        data = data.replace("\r", "\\r").replace(
            "\n", "\\n"
        )  # Escape internal line breaks

        extractGroupsRet = self.parser.extractGroups(
            data, unfinishedPart, unfinishedGroup
        )

        for partGroup in extractGroupsRet.groups:
            try:
                logMessage = self.parser.partGroupToLogMsg(partGroup)
            except ValueError as err:
                yield Server.RawLogRet(done=False, err=str(err))
            else:
                self.log(logMessage)
                yield Server.RawLogRet(done=False, err=None, logMessage=logMessage)

        yield Server.RawLogRet(
            done=True,
            err=None,
            logMessage=None,
            unfinishedPart=extractGroupsRet.unfinishedPart,
            unfinishedGroup=extractGroupsRet.unfinishedGroup,
        )

    @typechecked
    def log(self, logMessage: LogMessage):
        """
        Logs provided data to <file> in the following format:
        data = <t>: [<src>] <msg>
        sep = "$"
        escape char = "+"

        Ex:
        t = 845
        src = Source++
        msg = $Message

        Appends: 845: [Source++] $Message

        @throws ValueError
        """

        self.openLogFile()
        self.logFile.write(logMessage.asString() + "\n")
        self.logFile.flush()

    def __str__(self):
        return f"<Stls [addr: {self.addr}]>"

    __repr__ = __str__
