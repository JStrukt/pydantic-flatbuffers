import os
import unittest

from pydantic_flatbuffers.fbs.parser import load
from pydantic_flatbuffers.lang.py.generate import generate as generate_py
from pydantic_flatbuffers.lang import generate_files
from pathlib import Path
from .parser_cases import COLOR, CONSTANTS, INCLUDE


class CodeGeneratorTests(unittest.TestCase):
    TESTS_DIR = Path(__file__).parent.absolute()

    def setUp(self):
        os.chdir(self.TESTS_DIR)

    def test_generate_color(self):
        generate_files(*generate_py(COLOR, load(COLOR)))
        py_if: Path = self.TESTS_DIR / "color" / "color.py"
        py_ref: Path = self.TESTS_DIR / "expected" / "golden-color.py"
        self.assertEqual(py_if.read_text(), py_ref.read_text())

    def test_generate_constants(self):
        generate_files(*generate_py(CONSTANTS, load(CONSTANTS)))

    def test_generate_include(self):
        generate_files(*generate_py(INCLUDE, load(INCLUDE)))


if __name__ == "__main__":
    unittest.main()
