import doctest
import unittest
import os
import time
from os import mkdir, listdir, makedirs, utime
from os.path import join, exists
from shutil import copytree, rmtree
from ooo2tools.daemon.ooo2tools_daemon import check_share, task_to_process, cmd_exe
from ooo2tools.daemon import ooo2tools_daemon
from stat import *

SHARED_DIR = ooo2tools_daemon.SHARED_DIR

files = [join(SHARED_DIR, 'todo-000'),
    join(SHARED_DIR, 'todo-004'),
    join(SHARED_DIR, 'todo-002.processed'),
    join(SHARED_DIR, 'todo-003.lock'),
    join(SHARED_DIR, 'todo-003'),
    join(SHARED_DIR, 'todo-001'),
    join(SHARED_DIR, 'todo-003.processed'),
    join(SHARED_DIR, 'todo-002')]

sleep_tree = [join(SHARED_DIR, 'todo-003'),
    join(SHARED_DIR, 'todo-001')]

def setUp_tree():
    print "setting up tree"
    files.sort()
    if exists(SHARED_DIR):
        rmtree(SHARED_DIR)
    mkdir(SHARED_DIR)
    for test_files in files:
        if '.processed' in test_files or '.lock' in test_files:
            f = open(join(SHARED_DIR, test_files), 'w')
            f.close()
        else:
            copytree('test_todo', join(SHARED_DIR, test_files))

def setUp_sleep_tree():
    mkdir(SHARED_DIR)
    mkdir(sleep_tree[1])
    time.sleep(1)
    mkdir(sleep_tree[0])

class Test_ooo2tools_daemon(unittest.TestCase):
    def setUp(self):
        print "pre"
        files.sort()
        if exists(SHARED_DIR):
            rmtree(SHARED_DIR)
        mkdir(SHARED_DIR)
        for test_files in files:
            if '.processed' in test_files or '.lock' in test_files:
                f = open(join(SHARED_DIR, test_files), 'w')
                f.close()
            else:
                copytree('test_todo', join(SHARED_DIR, test_files))

    def test_check_share(self):
        todo = check_share()
        todo_dirs = [join(SHARED_DIR, 'todo-000'),
            join(SHARED_DIR, 'todo-004'),
            join(SHARED_DIR, 'todo-003'),
            join(SHARED_DIR, 'todo-001'),
            join(SHARED_DIR, 'todo-002')]
        for item in todo:
            self.assert_(item in todo_dirs)

    def test_task_to_process(self):
        os.utime(files[0], (0,0))
        self.assertEqual(task_to_process(files), files[0])

    def test_cmd_exe(self):
        task = join(SHARED_DIR, 'todo')
        copytree('test_todo', task)
        status = cmd_exe(task)[0]
        self.assertEqual(status, 0)

    def tearDown(self):
        print "post"
        if exists(SHARED_DIR):
            rmtree(SHARED_DIR)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test_ooo2tools_daemon))
    return suite
