#!/usr/bin/env bash

# Warning, will delete files
# run with

set -x

rm -rf code_tests/
rm -rf contract_samples_not_used/
rm -rf data/
rm -rf xls/
# rm -rf __pycache__/
rm -rfv .git .idea .vscode
rm -rfv .gitignore
rm -rfv common/*.pdf
rm -rvf environment.json

set +x
