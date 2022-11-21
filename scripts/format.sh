#!/bin/sh -e
set -x

autoflake --remove-all-unused-imports --recursive --in-place msaCore docs_src --exclude=__init__.py
black msaCore docs_src
isort msaCore docs_src
