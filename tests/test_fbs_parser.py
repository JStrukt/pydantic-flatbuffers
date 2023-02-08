# -*- coding: utf-8 -*-

from pydantic_flatbuffers.fbs.parser import load
from .parser_cases import COMMENTS, CONSTANTS, INCLUDE, COLOR, MONSTER_TEST, THRIFT2FBS


def test_comments():
    load(str(COMMENTS))


def test_constants():
    load(str(CONSTANTS))


def test_include():
    load(str(INCLUDE), include_dirs=["./parser_cases"])


def test_color():
    load(str(COLOR))


def test_monsters():
    fbs = load(str(MONSTER_TEST))
    assert fbs.root == "Monster"
    assert fbs.file_extension == "mon"
    assert fbs.file_identifier == "MONS"

    stats = fbs.__fbs_meta__["tables"][2]
    assert stats._fspec["id1"] == (False, "[string]", [])
    assert stats.attributes == [["BaseStat"]]


def test_thrift2fbs():
    load(str(THRIFT2FBS))
