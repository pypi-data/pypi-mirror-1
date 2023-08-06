#! /bin/sh

PYTHON="/usr/bin/python"
ZOPE_HOME="/home/shashank/zope-2.9.1"
INSTANCE_HOME="/home/shashank/zope-2.9.1/invite_testing"
CONFIG_FILE="/home/shashank/zope-2.9.1/invite_testing/etc/zope.conf"
SOFTWARE_HOME="/home/shashank/zope-2.9.1/lib/python"
PYTHONPATH="$SOFTWARE_HOME"
export PYTHONPATH INSTANCE_HOME SOFTWARE_HOME

TEST_RUN="$INSTANCE_HOME/Products/PloneInvite/tests/runalltests.py"

exec "$PYTHON" "$TEST_RUN"  "$@"
