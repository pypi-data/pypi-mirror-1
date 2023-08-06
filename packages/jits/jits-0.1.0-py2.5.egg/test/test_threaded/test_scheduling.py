import urllib2, sys
from time import sleep

import jits

from test_project.test_app import views as view

class TestTaskString(object):
    def __init__(self, string):
        self.string = string
    def __call__(self):
        view.test_list.append(self.string)
        
def get_slash():
    return urllib2.urlopen('http://localhost:7887').read()        
        
def test_initial_schedule():
    jits.add_task(callback=TestTaskString('initial_schedule'), minutes=1)
    assert len(view.test_list) is 0
    get_slash()
    assert len(view.test_list) is 1 and 'initial_schedule' in view.test_list

def test_not_now():
    jits.add_task(callback=TestTaskString('not now'), minutes=1, now=False)
    get_slash()
    sleep(.5)
    assert 'not now' not in view.test_list
    
def test_10_seconds():
    jits.add_task(callback=TestTaskString('10 seconds'), seconds=10)
    assert '10 seconds' in view.test_list
    sleep(11)
    get_slash()
    assert len([t for t in view.test_list if t == '10 seconds']) is 2
    sleep(11)
    get_slash()
    assert len([t for t in view.test_list if t == '10 seconds']) is 3
    
    
    