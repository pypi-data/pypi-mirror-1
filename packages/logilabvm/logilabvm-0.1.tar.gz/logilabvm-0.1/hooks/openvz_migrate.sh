#!/bin/bash

# fail on first error or on unset variables 
set -e -u

NAME=$1
DESTINATION=$2
LIVE=false

# TODO: basic hook, maybe try to get it smarter

# live or not
for arg in ${*:3}; do
    if [ "$arg" == "--live" ] || [ "$arg" == "-l" ]; then
        LIVE=true
        break
    fi
done

if [ "$LIVE" == "true" ]; then
    vzmigrate --remove-area yes --online -v $DESTINATION $NAME
else
    vzmigrate --remove-area yes -v $DESTINATION $NAME
fi
