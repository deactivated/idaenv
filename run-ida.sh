#!/bin/bash

set -e -o pipefail
shopt -s extglob

if [[ -z "$IDAENV" || -z "$IDAHOME" ]]; then
    echo "IDA environment vars not set."
    exit 1;
fi

name=$( basename "$0" )

case $name in
    ida|ida32)
        ida_pat="ida?(q)"
        ;;
    ida64)
        ida_pat="ida?(q)64"
        ;;
    *)
        echo "Unknown target executable"
        exit 1;
esac

# Look for the appropriate ida binary in $IDAHOME
ida_bin=("$IDAHOME"/$ida_pat)
if [[ ! -e "$ida_bin" ]]; then
    echo "IDA binary not found: $ida_bin"
    exit 1
fi

# Check if this is actually an idaenv install
if [[ ! -e "$IDAENV/bin/idaenv" ]]; then
    echo "idaenv not found in virtual environment"
    # Start IDA without further effort
    "$ida_bin" "$@"
    exit
fi

# Activate the virtualenv
source "$IDAENV/bin/activate"

# Configure IDAUSR
export IDAUSR="$HOME/.idapro:$( "$IDAENV/bin/idaenv" prefix )"

# Try to find libpython for preload
LIBPYTHON="$(python -c 'import sysconfig; print("%s/%s" % (
       sysconfig.get_config_var("LIBPL"),
       sysconfig.get_config_var("LDLIBRARY")))' 2>&1)"

# Start the target IDA binary
if [[ -f "$LIBPYTHON" && -f "/lib64/ld-linux-x86-64.so.2" ]]; then
    # Preload correct libpython
    LD_PRELOAD="$LIBPYTHON" "$ida_bin" "$@"
else
    # Hope for the best
    "$ida_bin" "$@"
fi
