import os
from shutil import rmtree
import unittest

from pydantic_flatbuffers.fbs.parser import load
from pydantic_flatbuffers.lang.py.generate import generate as generate_py
from pydantic_flatbuffers.lang import generate_files
from pathlib import Path
from .parser_cases import COLOR


class CodeGeneratorTests(unittest.TestCase):
    TEST_CASE = COLOR
    TESTS_DIR = Path(__file__).parent.absolute()
    COLOR_DIR = TESTS_DIR / "color"

    def setUp(self):
        self.maxDiff = None
        os.chdir(self.TESTS_DIR)

    def tearDown(self):
        rmtree(self.COLOR_DIR)

    def test_py(self):
        generate_files(*generate_py(self.TEST_CASE, load(self.TEST_CASE)))
        py_if: Path = self.COLOR_DIR / "color.py"
        py_ref: Path = self.TESTS_DIR / "expected" / "golden-color.py"
        self.assertEqual(py_if.read_text(), py_ref.read_text())


if __name__ == "__main__":
    unittest.main()
