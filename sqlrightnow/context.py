from contextlib import contextmanager

from sqlrightnow.manager import DBManager


@contextmanager
def db_context(storage, engine, commit_message='Default commit message'):
    manager = DBManager(storage, engine)
    try:
        yield manager
    finally:
        manager.commit(commit_message)
