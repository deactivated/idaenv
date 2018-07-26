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

ida_bin=("$IDAHOME"/$ida_pat)
if [[ ! -e "$ida_bin" ]]; then
    echo "IDA binary not found: $ida_bin"
    exit 1
fi

# Activate the virtualenv
source "$IDAENV/bin/activate"

# Configure environment
export IDAUSR="$HOME/.idapro:$( idaenv prefix )"

# Start the target binary
"$ida_bin" "$@"
