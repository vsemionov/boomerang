#!/bin/bash

BASE_DIR=$(dirname $(dirname $0))

echo "clearing expired sessions"
python $BASE_DIR/manage.py clearsessions

echo "clearing expired deleted objects"
python $BASE_DIR/manage.py cleardeleted
