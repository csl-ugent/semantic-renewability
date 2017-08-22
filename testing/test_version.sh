#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset

## Script used to test a version (including the copying of files to and from the board).
## Usage: ./test_version.sh <host> <version_a_src> <version_b_src> <version_name> <results_dir>
host=$1
version_a_src=$2
version_b_src=$3
version_name=$4
results_dir=$5

# Copy over files
dst_dir="~/automatic_tests/$version_name"
ssh $host "mkdir -p $dst_dir"
scp $version_a_src/BC05/d.out $host:$dst_dir

# Redeploy code mobility to switch blocks (the -i and -p options do not actually matter)
/opt/code_mobility/deploy_application.sh -a $(cat $version_a_src/AID.txt) -p 20 -i localhost $version_b_src/BC05/mobile_blocks

# Execute testing framework
ssh $host "~/automatic_tests/testing/test.py ~/automatic_tests/testing/config.ini $dst_dir"

# Copy back files
scp $host:$dst_dir/results.json $results_dir/$version_name.json
scp $host:$dst_dir/debug.log $results_dir/debug_$version_name.log
