#!/bin/sh

# Running in travis
: ' if [ PATH=]
    then
        do something
# Running in terminal
    else
        do this instead
    fi '

PYIOC_VERSION=2-11
PYIOC=$TRAVIS_BUILD_DIR/pythonIoc
export EPICS_CA_SERVER_PORT=6164
export EPICS_CA_REPEATER_PORT=6165
export EPICS_CA_ADDR_LIST=127.0.0.1
#export EPICS_CA_AUTO_ADDR_LIST=NO

cd "$(dirname "$0")"
exec $PYIOC manager_test.py "$@"
