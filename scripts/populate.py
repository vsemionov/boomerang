#! /usr/bin/env python

import sys
import uuid
import threading

import requests


DEFAULT_BASE_URL = "http://127.0.0.1:8000/"
SIGNUP_PATH = "accounts/signup/"
API_PATH = "api/"

INFO_SUBPATH = "info/"
NOTEBOOK_SUBPATH = "users/{}/notebooks/"
NOTE_SUBPATH = "users/{}/notebooks/{}/notes/"

DEFAULT_THREADS = 4
DEFAULT_USERS_PER_THREAD = 2500
DEFAULT_NOTEBOOKS_PER_USER = 1
DEFAULT_NOTES_PER_NOTEBOOK = 10


def create_user(base_url):
    signup_url = base_url + SIGNUP_PATH
    username = uuid.uuid4()
    password = uuid.uuid4()
    sess = requests.Session()
    sess.get(signup_url)
    sess.post(signup_url, data=dict(csrfmiddlewaretoken=sess.cookies["csrftoken"], username=username, password1=password, password2=password))
    return username, password


def get_user_id(api_url, username, password):
    info_url = api_url + INFO_SUBPATH
    user_id = requests.get(info_url, auth=(username, password)).json()["user"]["id"]
    return user_id


def create_notebook(api_url, username, password, user_id):
    notebooks_url = api_url + NOTEBOOK_SUBPATH.format(user_id)
    notebook = dict(name=str(uuid.uuid4()))
    notebook_id = requests.post(notebooks_url, auth=(username, password), json=notebook).json()["id"]
    return notebook_id


def create_note(api_url, username, password, user_id, notebook_id):
    notes_url = api_url + NOTE_SUBPATH.format(user_id, notebook_id)
    note = dict(notebook=notebook_id, title=str(uuid.uuid4()), text=str(uuid.uuid4()))
    note_id = requests.post(notes_url, auth=(username, password), json=note).json()["id"]
    return notebook_id


class Populator(threading.Thread):
    added_users = 0
    added_users_lock = threading.Lock()

    def __init__(self, base_url, users, notebooks_per_user, notes_per_notebook, *args, **kwargs):
        self.base_url = base_url
        self.api_url = base_url + API_PATH
        self.users = users
        self.notebooks_per_user = notebooks_per_user
        self.notes_per_notebook = notes_per_notebook
        super(Populator, self).__init__(*args, **kwargs)

    def run(self):
        for _ in range(self.users):
            username, password = create_user(self.base_url)
            user_id = get_user_id(self.api_url, username, password)
            for _ in range(self.notebooks_per_user):
                notebook_id = create_notebook(self.api_url, username, password, user_id)
                for _ in range(self.notes_per_notebook):
                    create_note(self.api_url, username, password, user_id, notebook_id)
            with self.added_users_lock:
                self.__class__.added_users += 1
                added_users = self.__class__.added_users
            print "Added %d users, %d notebooks, %d notes" % \
                  (added_users, added_users * self.notebooks_per_user,
                   added_users * self.notebooks_per_user * self.notes_per_notebook)


def main():
    base_url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BASE_URL
    nthreads = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_THREADS
    users_per_thread = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_USERS_PER_THREAD
    notebooks_per_user = int(sys.argv[4]) if len(sys.argv) > 4 else DEFAULT_NOTEBOOKS_PER_USER
    notes_per_notebook = int(sys.argv[5]) if len(sys.argv) > 5 else DEFAULT_NOTES_PER_NOTEBOOK
    threads = [Populator(base_url, users_per_thread, notebooks_per_user, notes_per_notebook) for _ in range(nthreads)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
