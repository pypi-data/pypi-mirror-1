# Copyright (c) 2008 Thomas Lotze
# See also LICENSE.txt

import os
import os.path
import shutil
import tempfile


original_cwd = None
sandboxes = []


def new_sandbox(specification):
    root = tempfile.mkdtemp()
    sandboxes.append(root)
    root = os.path.join(root, '')
    for line in specification.splitlines():
        type_, raw_path, comment = (line.split(None, 2) + [''])[:3]
        path = os.path.normpath(os.path.join(root, raw_path))
        if not path.startswith(root):
            raise ValueError('"%s" points outside the sandbox.' % raw_path)
        if type_ == 'f':
            f = open(path, 'w')
            f.write(comment)
            f.close()
        elif type_ == 'd':
            os.mkdir(path)
        elif type_ == 'l':
            assert comment.startswith('-> ')
            os.symlink(comment[3:], path)
    os.chdir(root)


def ls():
    root = os.path.join(os.getcwd(), '')
    items = []

    def handle_symlink(path):
        if os.path.islink(path):
            items.append((path, 'l', '-> ' + os.readlink(path)))
            return True
        return False

    for dirpath, dirnames, filenames in os.walk(root):
        for name in dirnames:
            path = os.path.join(dirpath, name)
            if not handle_symlink(path):
                items.append((path, 'd', ''))
        for name in filenames:
            path = os.path.join(dirpath, name)
            if not handle_symlink(path):
                items.append((path, 'f', open(path).read()))

    for path, type_, comment in sorted(items):
        assert path.startswith(root)
        print type_, path[len(root):], comment


def setup_sandboxes(test=None):
    global original_cwd
    original_cwd = os.getcwd()


def teardown_sandboxes(test=None):
    for path in sandboxes:
        shutil.rmtree(path, ignore_errors=True)
    del sandboxes[:]
    os.chdir(original_cwd)
