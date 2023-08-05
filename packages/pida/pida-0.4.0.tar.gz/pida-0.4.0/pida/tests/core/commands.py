

import pida.core.command as command

import unittest

class MockCommand(object):

    def __init__(self):
        self.count = 0
        self.args = []
        self.kw = []

    def __call__(self, *args, **kw):
        self.count = self.count + 1
        self.args = args
        self.kw = kw
        return True
        
def c():
    mc = MockCommand()
    arg1 = command.argument('banana', True)
    arg2 = command.argument('melon', False)
    c1 = command.command('peel', mc, [])
    c2 = command.command('fruitbowl', mc, [arg1, arg2])
    return c1, c2, mc

class CommandTest(unittest.TestCase):

    def test_call_good(self):
        c1, c2, mc = c()
        self.assertEqual(mc.count, 0)
        self.assertEqual(True, c1())
        self.assertEqual(mc.count, 1)

    def test_call_good_argument(self):
        c1, c2, mc = c()
        self.assertEqual(mc.count, 0)
        self.assertEqual(True, c2(banana='yellow'))
        self.assertEqual(mc.count, 1)
        self.assertEqual(mc.kw, {'banana': 'yellow'})

    def test_d_call_opt_argument(self):
        c1, c2, mc = c()
        self.assertEqual(mc.count, 0)
        self.assertEqual(True, c2(banana='yellow', melon='green'))
        self.assertEqual(mc.count, 1)
        self.assertEqual(mc.kw, {'banana': 'yellow', 
                             'melon': 'green'})
