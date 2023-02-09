from typing import List
from matrix_enum import MatrixEnum, Member
from pydantic_flatbuffers.fbs.fbs import FBSType


class FBSTypes(MatrixEnum):
    BOOL = Member(index=0, title="BOOL").extra(
        namespace=None,
        primitive=True,
        number=True,
        bits=1,
        pytype="bool",
        pyctype="bool",
    )
    BYTE = Member(index=1, title="BYTE").extra(
        namespace=None,
        primitive=True,
        number=True,
        bits=8,
        pytype="int8",
        pyctype="int8",
    )
    UBYTE = Member(index=2, title="UBYTE").extra(
        namespace=None,
        primitive=True,
        number=True,
        bits=8,
        pytype="int8",
        pyctype="uint8",
    )
    SHORT = Member(index=3, title="SHORT").extra(
        namespace=None,
        primitive=True,
        number=True,
        bits=16,
        pytype="int16",
        pyctype="int16",
    )
    USHORT = Member(index=4, title="USHORT").extra(
        namespace=None,
        primitive=True,
        number=True,
        bits=16,
        pytype="int16",
        pyctype="uint16",
    )
    INT = Member(index=5, title="INT").extra(
        namespace=None,
        primitive=True,
        number=True,
        bits=32,
        pytype="int",
        pyctype="int32",
    )
    UINT = Member(index=6, title="UINT").extra(
        namespace=None,
        primitive=True,
        number=True,
        bits=32,
        pytype="int32",
        pyctype="uint32",
    )
    FLOAT = Member(index=7, title="FLOAT").extra(
        namespace=None,
        primitive=True,
        number=True,
        bits=32,
        pytype="float",
        pyctype="float32",
    )
    LONG = Member(index=8, title="LONG").extra(
        namespace=None,
        primitive=True,
        number=True,
        bits=64,
        pytype="int64",
        pyctype="int64",
    )
    ULONG = Member(index=9, title="ULONG").extra(
        namespace=None,
        primitive=True,
        number=True,
        bits=64,
        pytype="uint64",
        pyctype="uint16",
    )
    DOUBLE = Member(index=10, title="DOUBLE").extra(
        namespace=None,
        primitive=True,
        number=True,
        bits=64,
        pytype="float",
        pyctype="float64",
    )
    STRING = Member(index=11, title="STRING").extra(
        namespace=None,
        primitive=True,
        number=False,
        bits=0,
        pytype="str",
        pyctype="int",
    )
    STRUCT = Member(index=12, title="STRUCT").extra(
        namespace="structs",
        primitive=False,
        number=False,
        bits=0,
        pytype="interface",
        pyctype="int",
    )
    TABLE = Member(index=13, title="TABLE").extra(
        namespace="tables",
        primitive=False,
        number=False,
        bits=0,
        pytype="interface",
        pyctype="int",
    )
    UNION = Member(index=14, title="UNION").extra(
        namespace="unions",
        primitive=False,
        number=False,
        bits=0,
        pytype="interface",
        pyctype="int",
    )
    VECTOR = Member(index=15, title="VECTOR").extra(
        namespace=None,
        primitive=False,
        number=False,
        bits=0,
        pytype="interface",
        pyctype="int",
    )
    # Special type not defined upstream, but used
    # to distinguish enums from unions
    ENUM = Member(index=100, title="ENUM").extra(
        namespace="enums",
        primitive=False,
        number=False,
        bits=0,
        pytype="interface",
        pyctype="int",
    )


NUMBERS: List[FBSType] = [fbs_type for fbs_type in list(FBSTypes) if fbs_type.number]

PRIMITIVES: List[FBSTypes] = [
    fbs_type for fbs_type in list(FBSTypes) if fbs_type.primitive
]
