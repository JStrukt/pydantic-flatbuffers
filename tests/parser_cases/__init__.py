from pathlib import Path

HERE: Path = Path(__file__).parent.resolve()

COLOR: Path = HERE / "color.fbs"
COMMENTS: Path = HERE / "comments.fbs"
CONSTANTS: Path = HERE / "constants.fbs"
INCLUDE: Path = HERE / "include.fbs"
INCLUDE_TEST1: Path = HERE / "include_test1.fbs"
MONSTER_TEST: Path = HERE / "monster_test.fbs"
THRIFT2FBS: Path = HERE / "thrift2fbs.fbs"
