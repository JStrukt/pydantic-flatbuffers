from pydantic_flatbuffers.lang.enums import FBSTypes


def get_type(
    name,
    module,
    optional=False,
    optionalize: bool = False,
    listify: bool = False,
):
    try:
        base = FBSTypes(name).pytype
        if optional and optionalize:
            return f"Option[{base}]"
        return base
    except ValueError:
        for fbs_type in list(FBSTypes):
            if fbs_type.namespace:
                for t in module.__fbs_meta__[fbs_type.namespace]:
                    if t.__name__ == name:
                        return t.__name__
        if (name[0], name[-1]) == ("[", "]"):
            element_type = get_type(name[1:-1], module)
            target_type = get_type(element_type, module)
            if listify:
                target_type = f"List[{target_type}]"
            else:
                target_type = f"[{target_type}]"
            return target_type
        return name
