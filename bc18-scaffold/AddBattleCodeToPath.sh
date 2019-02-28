# ASSUME we are in the same directory as run_nodocker.sh

#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH="$DIR/battlecode/python:$PYTHONPATH"
echo $PYTHONPATH


