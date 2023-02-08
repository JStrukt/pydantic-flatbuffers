from functools import partial
from pathlib import Path
from types import ModuleType
from typing import List

from pydantic_flatbuffers.fbs.fbs import FBSType
from pydantic_flatbuffers.lang.datastructure import FileToGenerate
from pydantic_flatbuffers.lang.get_type import get_type

HERE: Path = Path(__file__).parent.resolve()
TEMPLATE: Path = HERE / "template.yaml.j2"


def decorate_tree(tree: ModuleType) -> ModuleType:
    setattr(tree, "FBSType", FBSType)
    setattr(tree, "yaml_types", FBSType._VALUES_TO_NAMES_LOWER)
    setattr(tree, "get_type", partial(get_type, primitive=tree.yaml_types, module=tree))
    return tree


def generate(path: Path, tree: ModuleType) -> List[FileToGenerate]:
    return [FileToGenerate(f"{path.stem}.yaml", decorate_tree(tree), TEMPLATE)]
