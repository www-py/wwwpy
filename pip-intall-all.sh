#!/bin/bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -r requirements-test.txt
pip install -r requirements-pypi.txt
pip install -e .

# maybe these are better
# pip install  .[dev]
# pip install  .[test]
