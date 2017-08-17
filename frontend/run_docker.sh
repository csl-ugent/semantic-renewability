#!/usr/bin/env bash
# WARNING: will stop any running instances.
sudo docker rm -f $(sudo docker ps -a -q)

# DEV MODE:
sudo docker run -d -p 8001:8001 -p 28015:28015 -v /data/semantic_renewability/rethinkdb:/var/lib/rethinkdb/instance1 -t semantic_renewability:latest
