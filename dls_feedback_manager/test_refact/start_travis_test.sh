#!/home/travis/bin/python

# Running in travis

PYIOC_VERSION=2-11
PYIOC=$TRAVIS_BUILD_DIR/pythonSoftIoc-2.11/pythonIoc
export EPICS_CA_SERVER_PORT=6164
export EPICS_CA_REPEATER_PORT=6165
export EPICS_CA_ADDR_LIST=127.0.0.1
#export EPICS_CA_AUTO_ADDR_LIST=NO

cd "$(dirname "$0")"
exec $PYIOC test_manager.py "$@"
