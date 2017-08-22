#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset

## Script used to initialize the board we perform our tests on.
## Usage: ./initialize_board.sh <host> <config_file> 
host=$1
config_file=$2

# Initialize directory structure
ssh $host "rm -rf ~/automatic_tests"
ssh $host "mkdir -p ~/automatic_tests/testing"

# Transfer the testing framework
scp $(dirname $0)/transferable/test.py $config_file  $host:~/automatic_tests/testing/
