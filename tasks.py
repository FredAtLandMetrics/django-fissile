import os
from invoke import task


SCRIPT_DIRPATH = os.path.dirname(os.path.realpath(__file__))

@task
def test_all(c):
    os.chdir(os.path.join(SCRIPT_DIRPATH, 'tests', 'resources', 'minimal'))
    c.run('python ./manage.py test', env={'PYTHONPATH': SCRIPT_DIRPATH})