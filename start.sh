#!/bin/bash

if [ ! -d "venv" ]
then
    python3 -m venv --upgrade-deps venv \
    && venv/bin/pip3 install --no-cache-dir wheel \
    && venv/bin/pip3 install --no-cache-dir -Ur requirements.txt \
    && reset
fi

source venv/bin/activate

python3 -Bc "import pathlib; import shutil; [shutil.rmtree(p) for p in pathlib.Path('.').rglob('__pycache__')]"

if [ ! -v "SESSION_STRING" ]
then
    python3 app/generate_session_string.py \
    & exit
fi

python3 -m app
