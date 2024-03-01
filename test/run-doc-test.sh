#! /usr/bin/env bash

SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_PATH="${SCRIPT_PATH%test*}test"

python -m doctest docs/*.md -o NORMALIZE_WHITESPACE
