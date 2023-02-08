import os
from pathlib import Path
import re
from functools import partial
from keyword import kwlist
from types import ModuleType
from typing import List, Optional, Tuple

from pydantic_flatbuffers.fbs.fbs import FBSType
from pydantic_flatbuffers.lang.datastructure import FileToGenerate
from pydantic_flatbuffers.lang.get_type import get_type, _NAMESPACE_TO_TYPE
from pydantic_flatbuffers.lang.common import (
    get_bases,
    get_module_name,
    lookup_fbs_type,
    parse_types,
    pre_process_module,
)
from pydantic_flatbuffers.lang.py.types import FBSPyType, listify, optionalize

HERE: Path = Path(__file__).parent.resolve()
TEMPLATE: Path = HERE / "template.py.j2"


def c_int_from_fbs_type(fbs_type: FBSType) -> Optional[str]:
    if fbs_type in FBSType._PRIMITIVE_TYPES:
        py_type = FBSPyType._VALUES_TO_PY_TYPES[fbs_type]
        if re.search(r"int\d", py_type):
            return py_type
    return None


def c_int_types(module) -> List:
    """Figure out what int types need to be imported from ctypes"""
    c_types = []
    for namespace in _NAMESPACE_TO_TYPE.keys():
        for t in module.__fbs_meta__[namespace]:
            if namespace == "unions":
                continue
            if namespace == "enums":
                py_type = c_int_from_fbs_type(t._FBSType)
                if py_type:
                    c_types.append(py_type)
                continue
            for _, mtype in t._fspec.items():
                fbs_type = mtype[1]
                py_type = c_int_from_fbs_type(fbs_type)
                if py_type:
                    c_types.append(py_type)
    return c_types


# Should be compatible with GenTypeBasic() upstream
def py_gen_type(fbs_type) -> str:
    return FBSType._VALUES_TO_PY_C_TYPES[fbs_type]


# Should be compatible with GenMethod() upstream
def py_gen_method(fbs_type) -> str:
    is_primitive = fbs_type in FBSType._PRIMITIVE_TYPES
    if is_primitive:
        return camel_case(py_gen_type(fbs_type))
    elif fbs_type == FBSType.STRUCT:
        return "Struct"
    else:
        return "UOffsetTRelative"


# Similar to, but not compatible with GenGetter() upstream
def py_gen_getter(fbs_type) -> Tuple[str, Tuple]:
    if fbs_type == FBSType.STRING:
        return ("String", ())
    elif fbs_type == FBSType.UNION or fbs_type == FBSType.ENUM:
        return ("Get", ("flatbuffers.number_types.{}Flags".format("Int8"),))
    elif fbs_type == FBSType.VECTOR:
        _, _, _, element_type, _ = parse_types(fbs_type, get_type(fbs_type))
        return (
            "Get",
            (
                "flatbuffers.number_types.{}Flags".format(
                    camel_case(py_gen_type(element_type))
                ),
            ),
        )
    else:
        return (
            "Get",
            (
                "flatbuffers.number_types.{}Flags".format(
                    camel_case(py_gen_type(fbs_type))
                ),
            ),
        )


def camel_case(text: str) -> str:
    return "".join([x.title() for x in text.split("_")])


def generate(
    path: Path,
    tree: ModuleType,
    separate=False,
) -> List[FileToGenerate]:
    prefix = path.stem
    if not os.path.exists(prefix):
        os.mkdir(prefix)
        open(os.path.join(prefix, "__init__.py"), "a").close()
    setattr(tree, "module", tree)
    pre_process_module(tree, kwlist)
    # Type related methods
    setattr(tree, "FBSType", FBSType)
    setattr(tree, "python_types", FBSPyType._VALUES_TO_PY_TYPES)
    setattr(
        tree,
        "get_type",
        partial(
            get_type,
            primitive=tree.python_types,
            optionalize=optionalize,
            listify=listify,
            module=tree,
        ),
    )
    setattr(tree, "get_module_name", partial(get_module_name, module=tree))
    setattr(tree, "get_bases", partial(get_bases, module=tree))
    setattr(tree, "lookup_fbs_type", lookup_fbs_type)
    setattr(tree, "parse_types", parse_types)
    setattr(tree, "c_int_types", partial(c_int_types, module=tree))
    # Strings
    setattr(tree, "camel_case", camel_case)
    setattr(tree, "python_reserved", kwlist)
    # Python specific
    setattr(tree, "py_gen_type", py_gen_type)
    setattr(tree, "py_gen_method", py_gen_method)
    setattr(tree, "py_gen_getter", py_gen_getter)
    if not separate:
        _, filename = os.path.split(path)
        py_filename = os.path.splitext(filename)[0] + ".py"
        return [FileToGenerate(os.path.join(prefix, py_filename), tree, TEMPLATE)]

    files_to_generate = []

    for table in tree.__fbs_meta__["tables"]:
        setattr(tree, "table", table)
        files_to_generate.append(
            FileToGenerate(os.path.join(prefix, table.__name__ + ".py"), tree, TEMPLATE)
        )

    for fbs_union in tree.__fbs_meta__["unions"]:
        setattr(tree, "fbs_union", fbs_union)
        files_to_generate.append(
            FileToGenerate(os.path.join(prefix, fbs_union.__name__ + ".py"), tree, None)
        )

    for fbs_enum in tree.__fbs_meta__["enums"]:
        setattr(tree, "fbs_enum", fbs_enum)
        files_to_generate.append(
            FileToGenerate(os.path.join(prefix, fbs_enum.__name__ + ".py"), tree, None)
        )
    return files_to_generate
