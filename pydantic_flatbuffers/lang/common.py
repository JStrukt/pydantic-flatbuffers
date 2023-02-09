from collections import OrderedDict
from types import ModuleType

from typeguard import typechecked
from pydantic_flatbuffers.fbs.fbs import FBSType
from typing import List, NewType, Optional, Tuple

from pydantic_flatbuffers.lang.enums import FBSTypes


Table = NewType("Table", OrderedDict)


@typechecked
def get_module_name(name: str, module: ModuleType):
    for fbs_type in list(FBSTypes):
        namespace = fbs_type.namespace
        if namespace:
            for mod in [module] + module.__fbs_meta__["includes"]:
                for t in mod.__fbs_meta__[namespace]:
                    if t.__name__ == name:
                        return t.__module__
    return None


@typechecked
def parse_types(
    fbs_type: FBSTypes, py_type: str
) -> Tuple[bool, int, bool, Optional[FBSType], bool]:
    is_number = fbs_type.number
    bits = fbs_type.bits
    if (py_type[0], py_type[-1]) == ("[", "]"):
        primitive_type = False
        element_type = py_type[1:-1]
        element_type_primitive = element_type in FBSType._PRIMITIVE_TYPES_NAMES
    else:
        element_type = None
        element_type_primitive = False
        primitive_type = fbs_type in FBSType._PRIMITIVE_TYPES
    return (is_number, bits, primitive_type, element_type, element_type_primitive)


@typechecked
def lookup_fbs_type(module: ModuleType, fbs_type: FBSTypes) -> Optional[int]:
    """For complex types, check if something is a struct,
    table, union or an enum"""
    for fbs_type in list(FBSTypes):
        if fbs_type.namespace:
            for mod in [module] + module.__fbs_meta__["includes"]:
                for t in mod.__fbs_meta__[fbs_type.namespace]:
                    if t.__name__ == fbs_type:
                        return fbs_type.index
    return None


@typechecked
def lookup_table(table: str, module: ModuleType):
    for t in module.__fbs_meta__["tables"]:
        if t.__name__ == table:
            return t
    return None


@typechecked
def get_all_bases(table, module: ModuleType) -> List[str]:
    table_attrs_length = len(table.attributes)
    if not table_attrs_length:
        return []
    if table_attrs_length == 1 and table.attributes[0][0] == "protocol":
        return []
    return [t[0] for t in table.attributes]


@typechecked
def get_bases(table, module: ModuleType) -> List[str]:
    def is_view(module, table_name):
        t = lookup_table(table_name, module)
        return t.view if hasattr(t, "view") else False

    return [t for t in get_all_bases(table, module) if not is_view(module, t)]


@typechecked
def pre_process_module(  # noqa: C901
    module: ModuleType, reserved: Optional[List[str]] = None
) -> None:
    for table in module.__fbs_meta__["tables"]:
        if len(table.attributes) and table.attributes[0][0] == "protocol":
            table.protocol = True
        if len(table.attributes) and table.attributes[0][0] == "view":
            table.view = True
    # Do this in a second pass, so all tables have protoco/view attributes computed
    for table in module.__fbs_meta__["tables"]:
        bases = [lookup_table(b, module) for b in get_all_bases(table, module)]
        for b in bases:
            if not b or not hasattr(b, "view") or not b.view:
                continue
            table._fspec.update(b._fspec)
            table.default_spec += b.default_spec

        # Handle default values
        table.has_default = False
        table.default_dict = {}
        for k, v in table.default_spec:
            if v is not None:
                table.default_dict[k] = v
        for _, value in table.default_spec:
            if value is not None:
                table.has_default = True
                break

    # Rename any reserved field names
    if reserved is None:
        return

    for table in module.__fbs_meta__["tables"]:
        for k in set(table._fspec.keys()) & set(reserved):
            table._fspec[f"_{k}"] = table._fspec.pop(k)
        for i, kv in enumerate(table.default_spec):
            k, v = kv
            if k in reserved:
                table.default_spec[i] = (f"_{k}", v)
