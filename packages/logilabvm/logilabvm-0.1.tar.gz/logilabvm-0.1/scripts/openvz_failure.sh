#!/bin/bash

# fail on first error or on unset variables
set -e -u

NAME=$1
STAGE="openvz failure"

echo "[$STAGE] Destroy the VM"
vzctl stop $NAME
vzctl destroy $NAME
