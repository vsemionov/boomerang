import os
from pathlib import Path

import psycogreen.gevent


def when_ready(server):
    Path('/tmp/app-initialized').touch()


def post_fork(server, worker):
    psycogreen.gevent.patch_psycopg()


bind = os.environ['PORT']
if bind.startswith('/'):
    bind = 'unix:' + bind

workers = os.getenv('NUM_WORKERS', 4)

worker_class = 'gevent'

errorlog = '-'
