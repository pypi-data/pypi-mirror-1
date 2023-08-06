import unittest

from pylispng import lisp
from pylispng.util import sprint

ans1 = """
   [*]
    |--[2]
    +--[*]
        +--[*]
            |--[3]
            |--[4]
        +--[*]
            |--[2]
            |--[3]
"""

ans2 = """
   [*]
    |--[5]
    +--[+]
        |--[3]
        |--[4]
        |--[6]
    |--[22]
    +--[*]
        |--[2.3999999999999999]
        |--[5]
        |--[0.001]
    +--[-]
        |--[5]
        +--[+]
            |--[2]
            +--[-]
                |--[2]
                |--[4]
"""
class SExpressionPrintTestCase(unittest.TestCase):
    """

    """
    def test_tree(self):
        """

        """
        exprs = [
            '(* 2 (* (* 3 4) (* 2 3)))',
            '(* 5 (+ 3 4 6) 22 (* 2.4 5 0.001) (- 5 (+ 2 (- 2 4))))',
            ]
        answers = [x.lstrip('\n') for x in [ans1, ans2]]
        r = lisp.Reader()
        for expr, expected in zip(exprs, answers):
            sexpr = r.get_sexpr(expr)
            self.assertEquals(sprint.getTree(sexpr, initial=True), expected)

