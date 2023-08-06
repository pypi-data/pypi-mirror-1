# Copyright (c) 2008 Thomas Lotze
# See also LICENSE.txt

import os
import os.path
import shutil
import sys
import tempfile


HEAD = """\
#!%(executable)s

import sys
sys.path[:] = %(pythonpath)r

"""


original_environ = {}
tmp_paths = []


def install(text, path=None, name=None, on_path=False, env=None):
    if path is not None:
        tmp_paths.append(path)
        file_ = open(path, 'w')
    elif name is not None:
        directory = tempfile.mkdtemp()
        tmp_paths.append(directory)
        path = os.path.join(directory, name)
        file_ = open(path, 'w')
    else:
        handle, path = tempfile.mkstemp()
        tmp_paths.append(path)
        file_ = os.fdopen(handle, 'w')

    file_.write(HEAD % dict(
        executable=sys.executable,
        pythonpath=sys.path,
        ))

    file_.write(text)

    file_.close()
    os.chmod(path, 0754)

    if on_path:
        original_environ.setdefault('PATH', os.environ['PATH'])
        os.environ['PATH'] = ':'.join((directory, os.environ['PATH']))

    if env is not None:
        original_environ.setdefault(env, os.environ.get(env))
        os.environ[env] = path

    return path


def teardown_scripts(test=None):
    for key, value in original_environ.iteritems():
        if value is None:
            del os.environ[key]
        else:
            os.environ[key] = value
    original_environ.clear()

    for path in tmp_paths:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    del tmp_paths[:]
