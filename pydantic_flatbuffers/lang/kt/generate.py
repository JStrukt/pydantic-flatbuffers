import os
from pathlib import Path
from functools import partial
from types import ModuleType
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
from pydantic_flatbuffers.lang.kt.types import FBSKotlinType, optionalize

HERE: Path = Path(__file__).parent.resolve()
TEMPLATE: Path = HERE / "template.kt.j2"
# https://kotlinlang.org/docs/reference/grammar.html#identifiers
KT_KWLIST = {
    "abstract",
    "actual",
    "annotation",
    "as",
    "break",
    "by",
    "catch",
    "class",
    "companion",
    "const",
    "constructor",
    "continue",
    "crossinline",
    "data",
    "delegate",
    "do",
    "dynamic",
    "else",
    "enum",
    "expect",
    "external",
    "field",
    "file",
    "file",
    "final",
    "finally",
    "for",
    "fun",
    "get",
    "if",
    "import",
    "in",
    "infix",
    "init",
    "inline",
    "inner",
    "interface",
    "internal",
    "is",
    "lateinit",
    "noinline",
    "object",
    "open",
    "operator",
    "out",
    "override",
    "package",
    "param",
    "private",
    "property",
    "protected",
    "public",
    "receiver",
    "reified",
    "return",
    "sealed",
    "set",
    "setparam",
    "super",
    "suspend",
    "tailrec",
    "this",
    "throw",
    "try",
    "typealias",
    "typeof",
    "val",
    "var",
    "vararg",
    "when",
    "where",
    "while",
}


def camel_case(text: str) -> str:
    return "".join([x.title() for x in text.split("_")])


def generate(path: Path, tree: ModuleType, separate=False) -> List[FileToGenerate]:
    prefix = path.stem
    if not os.path.exists(prefix):
        os.mkdir(prefix)
    setattr(tree, "module", tree)
    pre_process_module(tree, KT_KWLIST)
    # Type related methods
    setattr(tree, "FBSType", FBSType)
    setattr(tree, "kotlin_types", FBSKotlinType._VALUES_TO_KT_TYPES)
    setattr(
        tree,
        "get_type",
        partial(
            get_type, primitive=tree.kotlin_types, optionalize=optionalize, module=tree
        ),
    )
    setattr(tree, "get_module_name", partial(get_module_name, module=tree))
    setattr(tree, "lookup_fbs_type", lookup_fbs_type)
    setattr(tree, "parse_types", parse_types)
    setattr(tree, "get_bases", partial(get_bases, module=tree))
    # Strings
    # Strings
    setattr(tree, "camel_case", camel_case)
    setattr(tree, "kotlin_reserved", KT_KWLIST)
    if not separate:
        _, filename = os.path.split(path)
        kt_filename = os.path.splitext(filename)[0] + ".kt"
        return [FileToGenerate(os.path.join(prefix, kt_filename), tree, TEMPLATE)]

    files_to_generate = []

    for table in tree.__fbs_meta__["tables"]:
        setattr(tree, "table", table)
        files_to_generate.append(
            FileToGenerate(os.path.join(prefix, table.__name__ + ".kt"), tree, TEMPLATE)
        )

    for fbs_union in tree.__fbs_meta__["unions"]:
        setattr(tree, "fbs_union", fbs_union)
        files_to_generate.append(
            FileToGenerate(os.path.join(prefix, fbs_union.__name__ + ".kt"), tree, None)
        )

    for fbs_enum in tree.__fbs_meta__["enums"]:
        setattr(tree, "fbs_enum", fbs_enum)
        files_to_generate.append(
            FileToGenerate(os.path.join(prefix, fbs_enum.__name__ + ".kt"), tree, None)
        )

    return files_to_generate
