#!/usr/bin/env python

"""Integration tests of `sqlrightnow`."""

import sqlite3
import uuid

from sqlrightnow.context import db_context
from sqlrightnow.engine import SQLiteEngine
from sqlrightnow.manager import DBManager
from sqlrightnow.persistence import GitStorage


def test_integration():
    """An end-to-end test of `sqlrightnow`."""
    # With a helpful context manager
    # We want to support other storage engines as well, e.g., 
    # S3Storage(bucket='xyz', key='/test/test.sqlite')
    storage = GitStorage(
        bucket='https://github.com/marcua/sqlrightnow-test',
        path=f'test/test-{uuid.uuid4()}.sqlite')  # UUID to avoid collisions on parallel test runs
    engine = SQLiteEngine()
    with db_context(storage=storage, engine=engine, commit_message='New table and some data') as manager:
        connection = sqlite3.connect(manager.local_path())
        cursor = connection.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS test_table ('
                       'id integer PRIMARY KEY, '
                       'name text NOT NULL);')
        cursor.execute('INSERT INTO TABLE test_table '
                       '(text)'
                       'VALUES ("Test #1");')
        connection.commit()
        connection.close()
        manager.commit('Created a table and added some data')

    # Without the context manager, and a bit more control over the flow (e.g., you can commit more than once)
    manager = DBManager(storage=storage, engine=engine)

    connection = sqlite3.connect(manager.local_path())
    cursor = connection.cursor()
    cursor.execute('INSERT INTO TABLE test_table '
                   '(text)'
                   'VALUES ("Test #2");')
    cursor.execute('INSERT INTO TABLE test_table '
                   '(text)'
                   'VALUES ("Test #3");')
    connection.commit()
    connection.close()
    manager.commit('Added two more rows')

    connection = sqlite3.connect(manager.local_path())
    cursor = connection.cursor()
    cursor.execute('INSERT INTO TABLE test_table '
                   '(text)'
                   'VALUES ("Test #4");')
    connection.commit()
    manager.commit('Another row')

    # We should be able to continue using the cursor even after a
    # manager/Git commit.
    cursor.execute('SELECT text FROM test_table;')
    results = {row[0] for row in cursor.fetchall()}
    assert results == {'Test #1', 'Test #2', 'Test #3', 'Test #4'}

    # TODO(marcua): assert something about git history getting
    # updated.

    # You probably never want to do this, but it's good for integration tests
    storage.delete(commit_message='Got rid of the DB')
