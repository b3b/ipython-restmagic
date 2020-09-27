#!/bin/bash
set -e

cd tests/notebooks/
papermill basic.ipynb basic_out.ipynb

result=$(nbdiff -M basic.ipynb basic_out.ipynb)
if [[ ${result} ]]; then
    echo "${result}"
    exit 1
fi

