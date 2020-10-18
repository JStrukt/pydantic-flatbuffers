# -*- coding: utf-8 -*-

from fbs.parser import load


def test_comments():
    load("parser-cases/comments.fbs")


def test_constants():
    load("parser-cases/constants.fbs")


def test_include():
    load("parser-cases/include.fbs", include_dirs=["./parser-cases"])


def test_monsters():
    fbs = load("parser-cases/monster_test.fbs")
    assert fbs.root == "Monster"
    assert fbs.file_extension == "mon"
    assert fbs.file_identifier == "MONS"

    stats = fbs.__fbs_meta__["tables"][2]
    assert stats._fspec["id1"] == (False, "[string]", [])
    assert stats.attributes == [["BaseStat"]]


def test_thrift2fbs():
    load("parser-cases/thrift2fbs.fbs")
