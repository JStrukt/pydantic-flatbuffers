import os
from shutil import rmtree
import unittest

from pydantic_flatbuffers.fbs.parser import load
from pydantic_flatbuffers.lang.kt.generate import generate as generate_kt
from pydantic_flatbuffers.lang.py.generate import generate as generate_py
from pydantic_flatbuffers.lang.rust.generate import generate as generate_rust
from pydantic_flatbuffers.lang.swift.generate import generate as generate_swift
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

    def test_rust(self):
        generate_files(*generate_rust(self.TEST_CASE, load(self.TEST_CASE)))
        rust_if: Path = self.COLOR_DIR / "color.rs"
        rust_ref: Path = self.TESTS_DIR / "expected" / "golden-color.rs"
        self.assertEqual(rust_ref.read_text(), rust_if.read_text())

    def test_kotlin(self):
        generate_files(*generate_kt(self.TEST_CASE, load(self.TEST_CASE)))
        kt_if: Path = self.COLOR_DIR / "color.kt"
        kt_ref: Path = self.TESTS_DIR / "expected" / "golden-color.kt"
        self.assertEqual(kt_if.read_text(), kt_ref.read_text())

    def test_swift(self):
        generate_files(*generate_swift(self.TEST_CASE, load(self.TEST_CASE)))
        swift_if: Path = self.COLOR_DIR / "color.swift"
        swift_ref: Path = self.TESTS_DIR / "expected" / "golden-color.swift"
        self.assertEqual(swift_if.read_text(), swift_ref.read_text())

    def test_py(self):
        generate_files(*generate_py(self.TEST_CASE, load(self.TEST_CASE)))
        py_if: Path = self.COLOR_DIR / "color.py"
        py_ref: Path = self.TESTS_DIR / "expected" / "golden-color.py"
        self.assertEqual(py_if.read_text(), py_ref.read_text())


if __name__ == "__main__":
    unittest.main()
