#!/usr/bin/env bash

## Script used to transfer the relevant files to arndale_external.
## Usage: ./transfer_arndale.sh <python_file> <config_file> <host>
python_file=$1
config_file=$2
host=$3

# Make sure all required directories exist.
ssh dvernemm@$host "rm -rf /home/dvernemm/automatic_tests/testing;
                    mkdir -p /home/dvernemm/automatic_tests;
                    mkdir -p /home/dvernemm/automatic_tests/testing"

# Transfer all necessary files (1 SSH connection).
sftp dvernemm@$host << EOF
  # Original
  put $python_file /home/dvernemm/automatic_tests/testing
  put $config_file /home/dvernemm/automatic_tests/testing
EOF