#!/usr/bin/env bash

## Script used to transfer the relevant files to arndale_external.
## Usage: ./transfer_arndale.sh <exec_base> <mobile_base> <output_directory> <host>
exec_base=$1
mobile_base=$2
output_directory=$3
host=$4

# Make sure all required directories exist.
ssh dvernemm@$host "mkdir -p /home/dvernemm/automatic_tests;
                    mkdir -p /home/dvernemm/automatic_tests/$output_directory"

# Transfer all necessary files (1 SSH connection).
sftp dvernemm@$host << EOF
  # Original
  put $exec_base/BC05/d.out /home/dvernemm/automatic_tests/$output_directory
  put $mobile_base/BC05/mobile_blocks/* /home/dvernemm/automatic_tests/$output_directory
EOF
