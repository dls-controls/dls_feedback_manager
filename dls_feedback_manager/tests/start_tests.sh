#!/bin/sh

PYIOC_VERSION=2.11
PYIOC=/dls_sw/prod/R3.14.12.3/support/pythonSoftIoc/2-11/pythonIoc
export EPICS_CA_SERVER_PORT=6164
export EPICS_CA_REPEATER_PORT=6165
export EPICS_CA_ADDR_LIST=127.0.0.1
export PYTHONPATH+=:/home/sfx44126/Desktop/gitolite_testing/dls_feedback_manager/dls_feedback_manager/
#export EPICS_CA_AUTO_ADDR_LIST=NO

cd "$(dirname "$0")"
exec $PYIOC test_test.py "$@"

