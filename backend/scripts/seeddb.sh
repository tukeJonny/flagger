#!/usr/bin/env bash

set -euo pipefail

CWD=`pwd`
MANAGE_SCRIPT="$CWD/manage.py"

if [ -e ./backend/db.sqlite3 ]; then
    rm ./backend/db.sqlite3
fi
if [ -e ./scoreserver/migrations/0*.py ]; then
    rm ./scoreserver/migrations/0*.py
fi

python $MANAGE_SCRIPT makemigrations
python $MANAGE_SCRIPT migrate
python $MANAGE_SCRIPT manufacture
