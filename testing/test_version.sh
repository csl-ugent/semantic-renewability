#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset

## Script used to test a version (including the copying of files to and from the board).
## Usage: ./test_version.sh <host> <binary> <version_name> <results_dir>
host=$1
binary=$2
version_name=$3
results_dir=$4

# Copy over files
dst_dir="~/automatic_tests/$version_name"
ssh $host "mkdir -p $dst_dir"
scp $binary $host:$dst_dir/binary

# Execute testing framework, capture the return code
ssh $host "~/automatic_tests/testing/test.py ~/automatic_tests/testing/config.ini $dst_dir" && rc=$? || rc=$?

# Copy back files
scp $host:$dst_dir/results.json $results_dir/$version_name.json
scp $host:$dst_dir/debug.log $results_dir/debug_$version_name.log

# Exit with the return code of the testing framework
exit $rc
