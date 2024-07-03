#!/bin/bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -r requirements-test.txt
pip install -r requirements-pypi.txt
pip install -e .

playwright install

# maybe these are better; BUT the above fixes the version of the unbounded dependencies
# pip install  .[dev]
# pip install  .[test]
