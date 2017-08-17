#!/usr/bin/env bash

## Script used to test a given version.
## Usage: ./transfer_arndale.sh <output_directory> <results_location> <host>
output_directory=$1
results_location=$2
host=$3

# Make sure all required directories exist.
ssh dvernemm@$host "cd /home/dvernemm/automatic_tests/$output_directory;
                    python3.4 ../testing/test.py ../testing/config.ini"

# Transfer all necessary files (1 SSH connection).
sftp dvernemm@$host << EOF
  # Original
  get /home/dvernemm/automatic_tests/$output_directory/results.json $results_location/$output_directory.json
  get /home/dvernemm/automatic_tests/$output_directory/debug.log $results_location/debug_$output_directory.log
EOF