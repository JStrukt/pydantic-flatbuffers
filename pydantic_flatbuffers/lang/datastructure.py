from dataclasses import dataclass
from pathlib import Path
from types import ModuleType


@dataclass
class FileToGenerate:
    filename: str
    tree: ModuleType
    template: Path
