from pydantic_flatbuffers.lang.enums import Namespaces


def get_type(name, module, primitive, optional=False, optionalize=None, listify=None):
    try:
        base = primitive[name]
        if optional and optionalize:
            return optionalize(base)
        return base
    except KeyError:
        for namespace in list(Namespaces):
            for t in module.__fbs_meta__[namespace.title]:
                if t.__name__ == name:
                    return t.__name__
        if (name[0], name[-1]) == ("[", "]"):
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
