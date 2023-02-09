from collections import OrderedDict
from pydantic_flatbuffers.fbs.fbs import FBSType
from typing import List, NewType, Optional, Tuple

from pydantic_flatbuffers.lang.get_type import _NAMESPACE_TO_TYPE


Table = NewType("Table", OrderedDict)


def get_module_name(name, module):
    for namespace in _NAMESPACE_TO_TYPE.keys():
        for mod in [module] + module.__fbs_meta__["includes"]:
            for t in mod.__fbs_meta__[namespace]:
                if t.__name__ == name:
                    return t.__module__
    return None


def parse_types(fbs_type, py_type) -> Tuple[bool, int, bool, Optional[FBSType], bool]:
    number_type = fbs_type in FBSType._NUMBER_TYPES
    bits = FBSType._BITS[fbs_type] if number_type else 0
    if (py_type[0], py_type[-1]) == ("[", "]"):
        primitive_type = False
        element_type = py_type[1:-1]
        element_type_primitive = element_type in FBSType._PRIMITIVE_TYPES_NAMES
    else:
        element_type = None
        element_type_primitive = False
        primitive_type = fbs_type in FBSType._PRIMITIVE_TYPES
    return (number_type, bits, primitive_type, element_type, element_type_primitive)


def lookup_fbs_type(module, fbs_type) -> Optional[FBSType]:
    """For complex types, check if something is a struct,
    table, union or an enum"""
    for namespace in _NAMESPACE_TO_TYPE.keys():
        for mod in [module] + module.__fbs_meta__["includes"]:
            for t in mod.__fbs_meta__[namespace]:
                if t.__name__ == fbs_type:
                    return _NAMESPACE_TO_TYPE[namespace]
    return None


def lookup_table(table, module):
    for t in module.__fbs_meta__["tables"]:
        if t.__name__ == table:
            return t
    return None


def get_all_bases(table: Table, module) -> List[str]:
    table_attrs_length = len(table.attributes)
    if not table_attrs_length:
        return []
    if table_attrs_length == 1 and table.attributes[0][0] == "protocol":
        return []
    return [t[0] for t in table.attributes]


def get_bases(table: Table, module) -> List[str]:
    def is_view(module, table_name):
        t = lookup_table(table_name, module)
        return t.view if hasattr(t, "view") else False

    return [t for t in get_all_bases(table, module) if not is_view(module, t)]


def pre_process_module(module, reserved=None):
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
            if v != None:
                table.default_dict[k] = v
        for member, value in table.default_spec:
            if value != None:
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
