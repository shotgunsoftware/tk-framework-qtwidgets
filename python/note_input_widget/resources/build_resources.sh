#!/usr/bin/env bash
#
# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

# The path to output all built .py files to:
UI_PYTHON_PATH=../ui

# Helper functions to build UI files
function build_qt {
    echo "$1 $2 > $UI_PYTHON_PATH/$3.py"
    # compile ui to python
    $1 $2 > $UI_PYTHON_PATH/$3.py
    # replace PySide2 imports with sgtk.platform.qt and then added code to set
    # global variables for each new import.
    sed -i"" -E \
        -e "/^from PySide2.QtWidgets(\s.*)?$/d; /^\s*$/d" \
        -e "s/^(from PySide.\.)(\w*)(.*)$/from tank.platform.qt import \2\nfor name, cls in \2.__dict__.items():\n    if isinstance(cls, type): globals()[name] = cls\n/g" \
        -e "s/from PySide2 import/from tank.platform.qt import/g" \
        $UI_PYTHON_PATH/$3.py
}

function build_ui {
    build_qt "$1 -g python --from-imports" "$2.ui" "$2"
}

function build_res {
    build_qt "$1 -g python" "$2.qrc" "$2_rc"
}

while getopts u:r: flag
do
    case "${flag}" in
        u) uic=${OPTARG};;
        r) rcc=${OPTARG};;
    esac
done

if [ -z "$uic" ]; then
    echo "the PySide uic compiler must be specified with the -u parameter"
    exit 1
fi

if [ -z "$rcc" ]; then
    echo "the PySide rcc compiler must be specified with the -r parameter"
    exit 1
fi

uicversion=$(${uic} --version)
rccversion=$(${rcc} --version)


if [ -z "$uicversion" ]; then
    echo "the PySide uic compiler version cannot be determined"
    exit 1
fi

if [ -z "$rccversion" ]; then
    echo "the PySide rcc compiler version cannot be determined"
    exit 1
fi

# build UI's:
echo "building user interfaces..."
build_ui $uic note_input_widget

# build resources
echo "building resources..."
build_res $rcc resources
