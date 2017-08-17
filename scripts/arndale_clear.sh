#!/usr/bin/env bash

## Script used to clear automatic_tests directory externally.
## Usage: ./transfer_arndale.sh <host>
host=$1

ssh dvernemm@$host "rm -rf /home/dvernemm/automatic_tests"