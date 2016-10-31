#!/bin/bash

BASE_DIR=$(dirname $(dirname $0))

source $BASE_DIR/env/bin/activate

$BASE_DIR/manage.py clearsessions
$BASE_DIR/manage.py cleardeleted
