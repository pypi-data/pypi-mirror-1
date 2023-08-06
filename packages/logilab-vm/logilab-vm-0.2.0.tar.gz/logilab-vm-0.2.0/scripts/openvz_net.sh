#!/bin/bash

# fail on first error or on unset variables 
set -e -u

NAME=$1
ITER=$2
NUM=$((ITER-1))
STAGE="openvz net $ITER"

# TODO: set modulr variables
if [ "${METHOD}" == "user" ]; then
    echo "[$STAGE] Create an interface"
    vzctl set $NAME --netif_add eth${NUM},${MAC_INT},veth${NAME}.${NUM},${MAC} --save
    #vzctl set $NAME --ipadd $IP --save
else
    echo "[$STAGE] Nothing to do"
fi
