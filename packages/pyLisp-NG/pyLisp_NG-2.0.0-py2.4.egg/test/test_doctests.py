from utils import buildDoctestSuite

# to add a new module to the test runner, simply include is in the list below:
modules = [
    'pylispng.lisp',
]

suite = buildDoctestSuite(modules)

if __name__ == '__main__':
    import unittest
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)


