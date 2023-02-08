from functools import partial
from pathlib import Path
from types import ModuleType
from typing import List

from pydantic_flatbuffers.fbs.fbs import FBSType
from pydantic_flatbuffers.lang.datastructure import FileToGenerate
from pydantic_flatbuffers.lang.get_type import get_type
from pydantic_flatbuffers.lang.java.types import FBSJavaType

HERE: Path = Path(__file__).parent.resolve()
TEMPLATE: Path = HERE / "template.java.j2"


def decorate_tree(tree: ModuleType) -> ModuleType:
    setattr(tree, "FBSType", FBSType)
    setattr(tree, "java_types", FBSJavaType._VALUES_TO_JAVA_TYPES)
    setattr(tree, "get_type", partial(get_type, primitive=tree.java_types, module=tree))
    return tree


def generate(path: Path, tree: ModuleType) -> List[FileToGenerate]:
    return [FileToGenerate(f"I{path.stem}.java", decorate_tree(tree), TEMPLATE)]
