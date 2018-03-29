#!/bin/sh

export EPICS_CA_SERVER_PORT=6164
export EPICS_CA_REPEATER_PORT=6165
export EPICS_CA_ADDR_LIST=127.0.0.1
#export EPICS_CA_AUTO_ADDR_LIST=NO

cd "$(dirname "$0")"
exec $PYIOC manager_tests.py "$@"
