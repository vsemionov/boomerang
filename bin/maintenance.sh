#!/bin/bash

BASE_DIR=$(dirname $(dirname $0))

python $BASE_DIR/manage.py clearsessions
python $BASE_DIR/manage.py cleardeleted
