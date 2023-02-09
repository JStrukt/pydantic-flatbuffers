#!/usr/bin/env python3

# -*- coding: utf-8 -*-

import argparse

from pydantic_flatbuffers.fbs.parser import load
from pydantic_flatbuffers.lang.py.generate import generate_py


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--includes", action="store", nargs="+", help="Directories to search"
    )
    parser.add_argument(
        "--templates", action="store", nargs="+", help="Filename to template"
    )
    parser.add_argument(
        "--python", type=bool, default=False, help="Generate Python code"
    )
    # TODO: pass args.sort to parser
    parser.add_argument(
        "--sort", type=bool, default=False, help="Sort everything alphabetically"
    )
    args, rest = parser.parse_known_args()
    for filename in rest:
        if args.python:
            if args.templates:
                generate_py(filename, load(filename), args.templates)
            else:
                generate_py(filename, load(filename))


if __name__ == "__main__":
    main()
