import os
from pathlib import Path
from functools import partial
from typing import List

from pydantic_flatbuffers.fbs.fbs import FBSType
from pydantic_flatbuffers.lang.datastructure import FileToGenerate
from pydantic_flatbuffers.lang.get_type import get_type
from pydantic_flatbuffers.lang.common import (
    get_bases,
    get_module_name,
    lookup_fbs_type,
    parse_types,
    pre_process_module,
)
from pydantic_flatbuffers.lang.swift.types import FBSSwiftType

HERE: Path = Path(__file__).parent.resolve()
TEMPLATE: Path = HERE / "template.swift.j2"

SWIFT_KWLIST = {}


def camel_case(text: str) -> str:
    return "".join([x.title() for x in text.split("_")])


def generate(path: Path, tree, separate=False) -> List[FileToGenerate]:
    prefix = path.stem
    if not os.path.exists(prefix):
        os.mkdir(prefix)
    setattr(tree, "module", tree)
    pre_process_module(tree, SWIFT_KWLIST)
    # Type related methods
    setattr(tree, "FBSType", FBSType)
    setattr(tree, "swift_types", FBSSwiftType._VALUES_TO_SWIFT_TYPES)
    setattr(
        tree, "get_type", partial(get_type, primitive=tree.swift_types, module=tree)
    )
    setattr(tree, "get_module_name", partial(get_module_name, module=tree))
    setattr(tree, "lookup_fbs_type", lookup_fbs_type)
    setattr(tree, "parse_types", parse_types)
    setattr(tree, "get_bases", partial(get_bases, module=tree))
    # Strings
    setattr(tree, "camel_case", camel_case)
    setattr(tree, "swift_reserved", SWIFT_KWLIST)
    if not separate:
        _, filename = os.path.split(path)
        swift_filename = os.path.splitext(filename)[0] + ".swift"
        return [FileToGenerate(os.path.join(prefix, swift_filename), tree, TEMPLATE)]

    files_to_generate = []
    for table in tree.__fbs_meta__["tables"]:
        setattr(tree, "table", table)
        files_to_generate.append(
            FileToGenerate(
                os.path.join(prefix, table.__name__ + ".swift"), tree, TEMPLATE
            )
        )

    for fbs_union in tree.__fbs_meta__["unions"]:
        setattr(tree, "fbs_union", fbs_union)
        files_to_generate.append(
            FileToGenerate(
                os.path.join(prefix, fbs_union.__name__ + ".swift"), tree, None
            )
        )

    for fbs_enum in tree.__fbs_meta__["enums"]:
        setattr(tree, "fbs_enum", fbs_enum)
        files_to_generate.append(
            os.path.join(prefix, fbs_enum.__name__ + ".swift"), tree, None
        )
    return files_to_generate
