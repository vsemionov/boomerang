#! /usr/bin/env python

import sys
import os
import uuid
import threading

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "notes.settings")
import django
django.setup()

from django.db import transaction
from django.contrib.auth.models import User
from api.models import Notebook, Note, Task


DEFAULT_THREADS = 4
DEFAULT_USERS_PER_THREAD = 2500
DEFAULT_NOTEBOOKS_PER_USER = 1
DEFAULT_NOTES_PER_NOTEBOOK = 10
DEFAULT_TASKS_PER_USER = 10


def create_user():
    user = User(username=uuid.uuid4())
    user.save()
    return user


def create_notebook(user):
    notebook = Notebook(user=user, name=uuid.uuid4())
    notebook.save()
    return notebook


def create_note(notebook):
    note = Note(notebook=notebook, title=uuid.uuid4(),
                text="%s %s %s %s" % (uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), uuid.uuid4()))
    note.save()
    return note


def create_task(user):
    task = Task(user=user, done=False, title=uuid.uuid4(), description="%s %s" % (uuid.uuid4(), uuid.uuid4()))
    task.save()
    return task


class Populator(threading.Thread):
    added_users = 0
    added_users_lock = threading.Lock()

    def __init__(self, users, notebooks_per_user, notes_per_notebook, tasks_per_user, *args, **kwargs):
        super(Populator, self).__init__(*args, **kwargs)

        self.users = users
        self.notebooks_per_user = notebooks_per_user
        self.notes_per_notebook = notes_per_notebook
        self.tasks_per_user = tasks_per_user

    def run(self):
        with transaction.atomic():
            for _ in range(self.users):
                user = create_user()
                for _ in range(self.notebooks_per_user):
                    notebook = create_notebook(user)
                    for _ in range(self.notes_per_notebook):
                        create_note(notebook)
                for _ in range(self.tasks_per_user):
                    create_task(user)
                with self.added_users_lock:
                    self.__class__.added_users += 1
                    added_users = self.__class__.added_users
                    print "Added %d users, %d notebooks, %d notes, %d tasks" % \
                          (added_users, added_users * self.notebooks_per_user,
                           added_users * self.notebooks_per_user * self.notes_per_notebook,
                           added_users * self.tasks_per_user)


def main():
    nthreads = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_THREADS
    users_per_thread = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_USERS_PER_THREAD
    notebooks_per_user = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_NOTEBOOKS_PER_USER
    notes_per_notebook = int(sys.argv[4]) if len(sys.argv) > 4 else DEFAULT_NOTES_PER_NOTEBOOK
    tasks_per_user = int(sys.argv[5]) if len(sys.argv) > 5 else DEFAULT_TASKS_PER_USER

    threads = [Populator(users_per_thread, notebooks_per_user, notes_per_notebook, tasks_per_user) for _ in range(nthreads)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
