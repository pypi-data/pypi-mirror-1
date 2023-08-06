import os

db_file = 'test.db'


def setup():
    pass

def teardown():
    os.remove(os.path.join(os.getcwd(), db_file))

