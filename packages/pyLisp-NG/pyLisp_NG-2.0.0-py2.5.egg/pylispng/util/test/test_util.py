import unittest

from pylispng import util

class UtilTestCase(unittest.TestCase):
    """

    """
    def test_arity(self):
        """

        """
        funcs = ['abs', '+', 'a']
        arities = [1, 2, 0]
        for func, expected in zip(funcs, arities):
            arity = util.getArity(func)
            self.assertEquals(arity, expected)

    def test_dynamicList(self):
        """

        """
        dl = util.DynamicList()
        self.assertEquals(len(dl), 0)
        dl[0] = 'apple'
        self.assertEquals(len(dl), 1)
        self.assertEquals(dl[0], 'apple')
        dl[11] = 'orange'
        self.assertEquals(len(dl), 12)
        self.assertEquals(dl[11], 'orange')
        self.assertEquals(dl[1], None)
        self.assertEquals(dl[10], None)
