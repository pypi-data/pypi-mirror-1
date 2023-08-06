#!/bin/bash
BUILDOUT_PATH=""
POUND_RUNNER="$poundbin"
POUND_CFG="$poundcfg"
POUND_PID="$poundpid"

\$POUND_RUNNER -f \$POUND_CFG -p \$POUND_PID
