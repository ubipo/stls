
class LogMessage:
    """Represents a log message with timestamp, source and message."""

    def __init__(self, t, src, msg):
        try:
            t = int(t)
        except ValueError:
            raise ValueError(f"First part (t) must be an int")

        if not t >= 0:
            raise ValueError("First part (t) must be larger or equal to zero")

        if not isinstance(src, str):
            raise ValueError("Second part (src) must be a str")

        if not isinstance(msg, str):
            raise ValueError("Third part (msg) must be a str")

        self.__logMessage = (t, src, msg)

    @property
    def t(self):
        return self.__logMessage[0]

    @property
    def src(self):
        return self.__logMessage[1]

    @property
    def msg(self):
        return self.__logMessage[2]

    def asString(self):
        return f"{self.t}: [{self.src}] {self.msg}"

    def __str__(self):
        return f"<LogMessage [t: {self.t}, src: {self.src}, msg: {self.msg}]>"
