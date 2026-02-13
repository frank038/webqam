#!/bin/bash

thisdir=$(dirname "$0")
cd $thisdir

if [[ $# -eq 0 ]]; then
    python3 ./webqam.py >/dev/null 2>&1
elif [[ $# -eq 2 ]]; then
    python3 ./webqam.py "$1" "$2"
else
    python3 ./webqam.py --help
fi