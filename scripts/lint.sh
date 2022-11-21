#!/usr/bin/env bash

set -e
set -x

mypy msaCore
flake8 msaCore docs_src
black msaCore docs_src --check
isort msaCore docs_src scripts --check-only

