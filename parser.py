from typeguard import typechecked

import stls
from stls import LogMessage


class Parser:
    """Parses encoded log messages."""

    def __init__(self, esc: chr = stls.DEF_ESC, sep: chr = stls.DEF_SEP, eom: chr = stls.DEF_EOM):
        self.esc = esc  # Escape
        self.sep = sep  # Seperator
        self.eom = eom  # End-Of-Message

    class ExtractGroupsRet:
        def __init__(self, groups, unfinishedPart, unfinishedGroup):
            self.groups = groups
            self.unfinishedPart = unfinishedPart
            self.unfinishedGroup = unfinishedGroup

        def __eq__(self, other):
            if not isinstance(other, Parser.ExtractGroupsRet):
                return False
            return self.groups == other.groups and self.unfinishedPart == other.unfinishedPart and self.unfinishedGroup == other.unfinishedGroup
        
        def __str__(self):
            return f"<ExtractGroupsRet [groups: {self.groups}, unfinishedPart: {self.unfinishedPart}, unfinishedGroup: {self.unfinishedGroup}]>"

        __repr__ = __str__


    @typechecked
    def extractGroups(
        self, data: str, unfinishedPart: str = "", unfinishedGroup: list = None
    ) -> ExtractGroupsRet:
        """ Extracts a list of groups composed of message parts.
        Parts are seperated by <self.sep>, groups by <self.eom>.
        
        Arguments:
            data {str} -- data to extract part groups from
        
        Returns:
            {tuple} -- (partGroupList, unfinishedGroup, unfinishedPart)
            <partGroupList> is the list of groups composed of message parts
            <unfinishedGroup> is the last part group if that group was
            not terminated by <self.eom>, otherwise it is None
            <unfinishedPart> is the last part if that part was not terminated
            by <self.sep>, otherwise it is None
        """

        part = unfinishedPart
        group = unfinishedGroup if unfinishedGroup is not None else []
        groups = []

        prevChar = ""
        prevEscaped = False  # Flags that the previous char was escaped
        for char in data:
            if prevChar == self.esc and not prevEscaped:
                if char in (self.esc, self.sep, self.eom):
                    prevEscaped = True
                else:
                    part += prevChar

                prevChar = char

            else:
                prevEscaped = False
                part += prevChar

                if char == self.sep:
                    group.append(part)
                    part = ""
                elif char == self.eom:
                    group.append(part)
                    groups.append(group)
                    part = ""
                    group = []

                if char in (self.sep, self.eom):
                    prevChar = ""
                else:
                    prevChar = char

        part += prevChar
        return Parser.ExtractGroupsRet(groups, unfinishedPart=part, unfinishedGroup=group)

    @typechecked
    def partGroupToLogMsg(self, parts: list):
        if not len(parts) == 3:
            raise ValueError("Log message must contain 3 parts")

        logMessage = LogMessage(*parts)

        return logMessage
