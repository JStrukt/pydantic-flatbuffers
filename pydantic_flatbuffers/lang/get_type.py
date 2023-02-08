from pydantic_flatbuffers.fbs.fbs import FBSType

_NAMESPACE_TO_TYPE = {
    "tables": FBSType.TABLE,
    "structs": FBSType.STRUCT,
    "enums": FBSType.ENUM,
    "unions": FBSType.UNION,
}


def get_type(name, module, primitive, optional=False, optionalize=None, listify=None):
    try:
        base = primitive[name]
        if optional and optionalize:
            return optionalize(base)
        return base
    except KeyError:
        for namespace in _NAMESPACE_TO_TYPE.keys():
            for t in module.__fbs_meta__[namespace]:
                if t.__name__ == name:
                    return t.__name__
        if name.startswith("["):
            element_type = get_type(
                name[1:-1], module, module.FBSType._LOWER_NAMES_TO_VALUES
            )
            target_type = get_type(element_type, module, primitive)
            if listify:
                target_type = listify(target_type)
            else:
                target_type = f"[{target_type}]"
            return target_type
        return name
