#!/usr/bin/env bash
BUILDOUT_PATH=""
POUND_RUNNER="$poundbin"
POUND_CFG="$poundcfg"
POUND_PID="$poundpid"

exec \$POUND_RUNNER -f \$POUND_CFG -p \$POUND_PID
