#!/usr/bin/env bash

set -e  # exit immediately with a non-zero status if any command fails

tmprootdir="$(dirname $0)"
echo ${tmprootdir} | grep '^/' >/dev/null 2>&1
if [ X"$?" == X"0" ]; then
    export ROOTDIR="${tmprootdir}"
else
    export ROOTDIR="$(pwd)"
fi

modules="
    test-mlmmj.py
    test-cleanup.py
"

# py.test command line arguments
#  -s                    shortcut for --capture=no.
#  -x, --exitfirst       exit instantly on first error or failed test.
#  -v, --verbose         increase verbosity.
py.test -s -x $@ ${modules}

echo "* Clean up temporary files."
find . -name '*pyc' | xargs rm -f {}
rm -rf .cache __pycache__
