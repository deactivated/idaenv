#!/bin/bash

set -ef -o pipefail

if [[ -z "$IDAENV" || -z "$IDAHOME" ]]; then
    echo "IDA environment vars not set."
    exit 1;
fi

name=$( basename "$0" )

case $name in
    ida|ida32)
        ida_bin=ida
        ;;
    ida64)
        ida_bin=ida64
        ;;
    *)
        echo "Unknown target executable"
        exit 1;
esac

# Activate the virtualenv
source "$IDAENV/bin/activate"

# Configure environment
export IDAUSR="$HOME/.idapro:$( idaenv prefix )"

# Start the target binary
"$IDAHOME"/$ida_bin "$@"
