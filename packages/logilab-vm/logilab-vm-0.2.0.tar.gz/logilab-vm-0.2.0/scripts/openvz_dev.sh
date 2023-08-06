#!/bin/bash

# fail on first error or on unset variables 
set -e -u

NAME=$1
ITER=$2
STAGE="openvz dev $ITER"

# TODO: handle dev
echo "[$STAGE] Nothing to do"
