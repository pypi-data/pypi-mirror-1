import sys

from nose.tools import *

from atomisator.main.tests.base import set_conf, tear_conf
from atomisator.main.tests.base import test_conf 
from atomisator.main.commands import atomisator 
from atomisator.main.config import AtomisatorConfig

sys_argv = None

def set_more_conf():
    set_conf()
    parser = AtomisatorConfig(test_conf)
    parser.store_entries = False
    parser.write()
    global sys_argv 
    sys_argv = sys.argv 
    sys.argv = ['atomisator', test_conf]

def more_tear_conf():
    sys.argv = sys_argv 
    tear_conf()
 
@with_setup(set_more_conf, more_tear_conf)
def test_atomisator_no_storage():
    atomisator()

