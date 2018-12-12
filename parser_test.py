from pytest import raises

from stls import Parser

parser = Parser()

def test_single():
    data = "8$ABC$def*"
    expected = [["8", "ABC", "def"]]
    actual = parser.extractGroups(data).groups
    assert expected == actual


def test_double():
    data = "8$ABC$def*1$GHI$jkl*"
    expected = [["8", "ABC", "def"], ["1", "GHI", "jkl"]]
    actual = parser.extractGroups(data).groups
    assert expected == actual


def test_unfinished():
    data = "8$ABC$def*1$GHI$jkl"
    expected = Parser.ExtractGroupsRet([["8", "ABC", "def"]], "jkl", ["1", "GHI"])
    actual = parser.extractGroups(data)
    assert expected == actual


def test_ArgUnfinishedPart():
    data = "2$ABC$def*"
    expected = [["12", "ABC", "def"]]
    actual = parser.extractGroups(data, "1").groups
    assert expected == actual


def test_ArgUnfinishedGroup():
    data = "ABC$def*"
    expected = [["8", "ABC", "def"]]
    actual = parser.extractGroups(data, "", ["8"]).groups
    assert expected == actual


def test_escapeSep():
    data = "8$ABC+$def*"
    expected = [["8", "ABC$def"]]
    actual = parser.extractGroups(data).groups
    assert expected == actual


def test_escapeEom():
    data = "8$ABC+$def+*"
    expected = Parser.ExtractGroupsRet([], "ABC$def*", ["8"])
    actual = parser.extractGroups(data)
    assert expected == actual


def test_escapeEsc():
    data = "8$ABC++$def*"
    expected = [["8", "ABC+", "def"]]
    actual = parser.extractGroups(data).groups
    assert expected == actual
