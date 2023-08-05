#!/bin/bash

DIR=$(dirname "$PWD/$0")
VERSION=$(python -c "import sys; sys.path.insert(0, '$DIR/..'); from PyGTKShell.Core import *; print '.'.join(map(str, pygtkshell_version))")
find "$DIR" -name "[^.]*.txt" -print -exec asciidoc -a version=$VERSION {} \;

