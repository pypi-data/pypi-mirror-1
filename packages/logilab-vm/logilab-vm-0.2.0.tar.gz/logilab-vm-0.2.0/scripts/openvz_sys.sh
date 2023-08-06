#!/bin/bash

# fail on first error or on unset variables
set -e -u

STAGE="openvz sys"

# TODO: set gateway / modulr variables
echo "[$STAGE] Create VM"
if [ -n "${OSTEMPLATE}" ]; then
    vzctl create $NAME --ostemplate $OSTEMPLATE --hostname $HOST
else
    vzctl create $NAME --hostname $HOST
fi
if [ -n "${DOMAIN}" ]; then
    # try to retrieve nameservers
    NS=""
    for opt in $*; do
        if [ "${opt%=*}" == "NS" ]; then
            NS="$NS --nameserver ${opt#*=}"
        fi
    done
    echo "[$STAGE] Set search domain [and nameservers]"
    vzctl set $NAME $NS --searchdomain $DOMAIN --save
fi
