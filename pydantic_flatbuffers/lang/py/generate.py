import os
from pathlib import Path
from functools import partial
from keyword import kwlist
from types import ModuleType
from typing import List, Tuple

from typeguard import typechecked

from pydantic_flatbuffers.fbs.fbs import FBSType
from pydantic_flatbuffers.lang.datastructure import FileToGenerate
from pydantic_flatbuffers.lang.enums import FBSTypes
from pydantic_flatbuffers.lang.get_type import get_type
from pydantic_flatbuffers.lang.common import (
    get_bases,
    get_module_name,
    lookup_fbs_type,
    parse_types,
    pre_process_module,
)
from pydantic_flatbuffers.lang.py.types import FBSPyType

HERE: Path = Path(__file__).parent.resolve()
TEMPLATE: Path = HERE / "template.py.j2"


@typechecked
def c_int_types(module: ModuleType) -> List:  # noqa: C901
    """Figure out what int types need to be imported from ctypes"""
    c_types = []
    for fbs_type in list(FBSTypes):
        namespace = fbs_type.namespace
        title = fbs_type.title
        if namespace:
            print(f"Namespace: {namespace}, Title: {title}")
            for t in module.__fbs_meta__[namespace]:
                if namespace == "unions":
                    continue
                if namespace == "enums":
                    fbs_type = t._FBSType
                    print(f"Namespace: enums, FBS Type: {fbs_type}")
                    try:
                        real_type: FBSTypes = FBSTypes(fbs_type)
                    except ValueError:
                        continue
                    py_type = real_type.get_c_int_type()
                    if py_type:
                        c_types.append(py_type)
                    continue
                for _, mtype in t._fspec.items():
                    fbs_type = mtype[1]
                    print(f"FBS Type: {fbs_type}")
                    try:
                        real_type: FBSTypes = FBSTypes(fbs_type)
                    except ValueError:
                        continue
                    py_type = real_type.get_c_int_type()
                    if py_type:
                        c_types.append(py_type)
    return c_types


# Should be compatible with GenTypeBasic() upstream
@typechecked
def py_gen_type(fbs_type: FBSTypes) -> str:
    return fbs_type.pyctype


# Should be compatible with GenMethod() upstream
@typechecked
def py_gen_method(fbs_type: FBSTypes) -> str:
    primitive = fbs_type.primitive
    pyctype = fbs_type.pyctype
    index = fbs_type.index
    struct_index = FBSTypes.STRUCT.index

    if primitive:
        return camel_case(pyctype)
    elif index == struct_index:
        return "Struct"
    else:
        return "UOffsetTRelative"


# Similar to, but not compatible with GenGetter() upstream
@typechecked
def py_gen_getter(fbs_type: FBSTypes) -> Tuple[str, Tuple]:
    index = fbs_type.index
    str_index = FBSType.STRING.index
    union_index = FBSType.UNION.index
    enum_index = FBSType.ENUM.index
    vector_index = FBSType.VECTOR.index
    if index == str_index:
        return ("String", ())
    elif index in (union_index, enum_index):
        return ("Get", ("flatbuffers.number_types.{}Flags".format("Int8"),))
    elif index == vector_index:
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


@typechecked
def camel_case(text: str) -> str:
    return "".join([x.title() for x in text.split("_")])


@typechecked
def generate(
    path: Path,
    tree: ModuleType,
    separate: bool = False,
) -> List[FileToGenerate]:
    prefix = path.stem
    print(f"This is the prefix: {prefix}")
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
            optionalize=True,
            listify=True,
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
