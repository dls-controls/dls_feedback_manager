#!/home/travis/bin/python

# Running in travis

PYIOC_VERSION=2-11
PYIOC=pythonSoftIoc-2.11/pythonIoc
EPICS_CA_SERVER_PORT="6164"
EPICS_CA_REPEATER_PORT="6165"
EPICS_CA_ADDR_LIST="127.0.0.1"
#export EPICS_CA_AUTO_ADDR_LIST=NO

cd $(dirname $0)
exec $PYIOC test_manager.py "$@"
