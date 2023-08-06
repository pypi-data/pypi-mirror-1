import unittest

from pylispng import lisp

class LispTestCase(unittest.TestCase):
    """

    """
    def setUp(self):
        """

        """
        self.exprs = [
            '(+ 5 3)',
            '(- 5 3)',
            '(- 3 5)',
            '(+ 5 2.3 2.7)',
            '(+ 5 (* 2 6.55))',
            '(* 5 (+ 3 4 6) 22 (* 2.4 5 0.001) (- 5 (+ 2 (- 2 4))))',
            "'(+ 5 3)",
            "'a",
            """'(this is "cool")""",
            "(first '(a b c))",
            "(rest '(a b c))",
            "(cons 'a '(b c d))",
            "(append '(a b c) '(d e f) (list 1 2 3 4))",
            "(setq fred '(a b c))",
            "(rest fred)",
            "(put 'fred 'birthday 'june-12-1973)",
            "(get 'fred 'birthday)",
            "(logic 0.5)",
            "(logic 1.0)",
            "(not (logic 0.0))",
            "(not (logic 0.35))",
            "(and *true* (not *true*))",
            "(or *true* (not *true*))",
            "(setq *true* (logic .95))",
            "(and *true* (not *true*))",
            "(or *true* (not *true*))",
            "(setq *true* (logic 1.0))",
            "(> 5 2)", 
            "(> 2 5)",
            "(> 5 (* 3 (+ 2 1)))",
            "(> (* 3 (+ 2 1)) (+ 1 2 3))",
            '(== "wow" "fred")',
            '(!= "wow" "fred")',
            "(>= 5 5)",
            '(<= "andy" "bobbie")',
            "(if (> 5 2) 'true 'false)",
            "(if (< 5 2) 'true 'false)",
            "(if (< 5 2) 'true)",
            "(if (not (< 5 2)) 'true)",
            "(lambda (x y) (* x y))",
            "((lambda (x y) (* x y)) 5 2)",
            "(lambda (x y) (* x y) (+ x y))",
            "((lambda (x y) (* x y) (+ x y)) 5 2)",
            "(def mult (lambda (x y) (* x y)))",
            "(mult 5 7)",
            "(def dumb (lambda (x y) (if (> x y) (* x y) (/ x y))))",
            "(dumb 5.0 3.0)",
            "(dumb 3.0 5.0)",
            "(let ((x 5) (y 3)) (+ x y))",
            "(let ((x 5) (y 3) z) (+ x y))",
            "(def dumb (lambda (x) (let ((y 12)) (* x y))))",
            "(dumb 3)",
            "`a",
            "`(a b ,fred)",
            "`(a b ,@fred)",
            "`(a (b (c (d (e (f ,@fred))))))",
            "((macro (x) `(+ ,x 5)) 4)",
            "(def incf (macro (x) `(setq ,x (+ ,x 1))))",
            "(setq whee 33)",
            "(incf whee)",
            "(def foo (lambda (x y) (if (<= y 0) x (begin (foo (cons y x) (- y 1))))))",
            "(foo '() 12)",
            "(let ((x 5)) (def bar (lambda () x)))",
            "(bar)",
            "(env-set (get-environment bar) 'x 33)",
            "(bar)",
            "(setq wow (list (cons 'a 'b) (cons 'q 'fun)))",
            "(assoc 'a wow)",
            '(- 5 (* 2 4))',
            '(- (* 2 4) 5)',
            '(/ 17 350)',
            '(/ 350 17)',
            ]
        self.answers = [
            '8',
            '2',
            '-2',
            '10.0',
            '18.100000000000001',
            '85.799999999999997',
            '(+ 5 3)',
            'a',
            "(this is 'cool')",
            'a',
            '(b c)',
            '(a b c d)',
            '(a b c d e f 1 2 3 4)',
            '(a b c)',
            '(b c)',
            'june-12-1973',
            'june-12-1973',
            '(logic 0.5)',
            '*true*',
            '*true*',
            '(logic 0.65)',
            '*false*',
            '*true*',
            '(logic 0.95)',
            '(logic 0.05)',
            '(logic 0.95)',
            '*true*',
            '*true*',
            '*false*',
            '*false*',
            '*true*',
            '*false*',
            '*true*',
            '*true*',
            '*true*',
            'true',
            'false',
            '*false*',
            'true',
            '(lambda (x y) (* x y))',
            '10',
            '(lambda (x y) (begin (* x y) (+ x y)))',
            '7',
            '(lambda (x y) (* x y))',
            '35',
            '(lambda (x y) (if (> x y) (* x y) (/ x y)))',
            '15.0',
            '0.59999999999999998',
            '8',
            '8',
            '(lambda (x) (let ((y 12)) (* x y)))',
            '36',
            'a',
            '(a b (a b c))',
            '(a b a b c)',
            '(a (b (c (d (e (f a b c))))))',
            '9',
            '(macro (x) (i-quote (setq , x (+ , x 1))))',
            '33',
            '34',
            '(lambda (x y) (if (<= y 0) x (begin (foo (cons y x) (- y 1)))))',
            '(1 2 3 4 5 6 7 8 9 10 11 12)',
            '(lambda () x)',
            '5',
            '33',
            '33',
            '((a . b) (q . fun))',
            'b',
            '-3',
            '3',
            '0.048571428571428571',
            '20.588235294117649',
        ]
        self.reader = lisp.Reader()
        self.lisper = lisp.Lisper()

    def test_dataStructure(self):
        """

        """
        self.assertEquals(lisp.get_type('+'), lisp.FunctionObject)
        self.assertEquals(lisp.get_type('*'), lisp.FunctionObject)
        self.assertEquals(lisp.get_type('and'), lisp.FunctionObject)
        self.assertEquals(lisp.get_type('lambda'), lisp.SyntaxObject)
        self.assertEquals(lisp.get_type('if'), lisp.SyntaxObject)
        self.assertEquals(lisp.get_type('def'), lisp.SyntaxObject)
        self.assertEquals(lisp.get_type('x'), lisp.SymbolObject)
        self.assertEquals(lisp.get_type(5), lisp.SymbolObject)

    def test_reader(self):
        """
        As long as get_sexpr() runs without throwing an exception, we're good.
        """
        for expr in self.exprs:
            sexpr1 = self.reader.get_sexpr(expr)
            sexpr2 = lisp.Reader(expr).sexpr
            self.assertTrue(isinstance(sexpr1, lisp.ListObject))
            self.assertEquals(str(sexpr1), str(sexpr2))

    def test_lisper(self):
        """

        """
        count = 0
        for expr, expected in zip(self.exprs, self.answers):
            count += 1
            sexpr = self.reader.get_sexpr(expr)
            answer = self.lisper.eval(sexpr)
            self.assertEquals(str(answer), expected)

    def test_expressionLengths(self):
        """
        PyLisp determines expression length by the number of immediate
        children, not all children recursively.
        """
        answers = [3, 3, 3, 4, 3, 6]
        for expr, expected in zip(self.exprs[:6], answers):
            sexpr = self.reader.get_sexpr(expr)
            self.assertEquals(len(sexpr), expected)

    def test_sExpressions(self):
        """

        """
        l = lisp.SExpression()
        l.append('+')
        l.append('3')
        l.append('5')
        l.append('(* 3 3)')
        form = '(+ 3 5 (* 3 3))'
        value = 17
        depth = 2
        length = 4
        size = 2
        self.assertEquals(str(l), form)
        self.assertEquals(l.eval(), value)
        self.assertEquals(l.getDepth(), depth)
        self.assertEquals(len(l), length)
        self.assertEquals(l.getSize(), size)
        # more complicated expressions, chuck at a time
        l = lisp.SExpression('(+ 4 19)')
        l.append('(- 2 (* 45 3))')
        l.append('(* 7 (- 37 99))')
        form = '(+ 4 19 (- 2 (* 45 3)) (* 7 (- 37 99)))'
        value = -544
        depth = 3
        length = 5
        size = 5
        self.assertEquals(str(l), form)
        self.assertEquals(l.eval(), value)
        self.assertEquals(l.getDepth(), depth)
        self.assertEquals(len(l), length)
        self.assertEquals(l.getSize(), size)

    def test_sExpressionsWithInts(self):
        # now test with integers
        l = lisp.SExpression()
        l.append('+')
        l.append(3)
        l.append(5)
        l.append('(* 3 3)')
        form = '(+ 3 5 (* 3 3))'
        value = 17
        self.assertEquals(str(l), form)
        self.assertEquals(l.eval(), value)

class ExpressionTests(unittest.TestCase):
    """

    """
    def setUp(self):
        self.exp1 = ('(+ 2 2)')
        self.exp2 = ('(+ 2 (- 5 2))')
        self.exp3 = ('(+ (+ (+ 0 0) (- 0 2)) (+ (+ 0 2) (- 1 0)))')
        self.exp4 = ('''(+ (+ (+ 0 0) (- 0 2)) (+ (+ (+ (+ (+ 0 0)
            (- 0 2)) (+ (+ 0 2) (- 1 0))) 2) (- 1 0)))''')
        self.exp5 = '(- 5 (* 2 4))'
        self.exp6 = ('(/ 1 4)')
        self.exp7 = ('(+ 2 (- 5 (/ 1 4)))')
        self.exps = [self.exp1, self.exp2, self.exp3, self.exp4,
            self.exp5, self.exp6, self.exp7]

    def test_expressionSize(self):
        """

        """
        exp2 = lisp.SExpression(self.exp2)
        exp3 = lisp.SExpression(self.exp3)
        exp4 = lisp.SExpression(self.exp4)
        self.assertEquals(exp2.getSize(), 2)
        self.assertEquals(exp3.getSize(), 7)
        self.assertEquals(exp4.getSize(), 14)

    def test_expressionIndices(self):
        """

        """
        exp1 = lisp.SExpression(self.exp1)
        exp2 = lisp.SExpression(self.exp2)
        exp3 = lisp.SExpression(self.exp3)
        #self.assertEquals(exp1[0], '(+ 2 2)')
        #self.assertEquals(exp2[1], ['-', 5, 2])
        #for i in xrange(exp3.getSize()):
        #    self.assertEquals(exp3[i], exp3Answer[i])
        # XXX hrm... need to think of a better way of representing/storing
        # branches such that manipulating them at a lower level will be
        # immediately reflected in the whole.
        #exp3[2] = ['*', 4, 3]

    def test_expressionSlices(self):
        """

        """
        exp3 = lisp.SExpression(self.exp3)
        #self.assertEquals(
        #    exp3[1:3], 
        #    [['+', ['+', 0, 0], ['-', 0, 2]],
        #        ['+', ['+', 0, 2], ['-', 1, 0]]])
        #self.assertEquals(exp3[5:7], [['+', 0, 2], ['-', 1, 0]])
        #self.assertEquals(exp3[4:], [['-', 0, 2], ['+', 0, 2], ['-', 1, 0]])

    def test_getExpressionDepth(self):
        """

        """
        for expected, exp in zip([1, 2, 3, 6, 2, 1, 3], self.exps):
            sexpr = lisp.SExpression(exp)
            self.assertEquals(sexpr.getDepth(), expected)

    def test_getOperatorCount(self):
        """

        """
        answers = [1, 2, 7, 14, 2, 1, 3]
        initCount = 0
        for expected, exp in zip(answers, self.exps):
            sexpr = lisp.SExpression(exp)
            self.assertEquals(sexpr.getSize(), expected)

    def test_getSubExpression(self):
        """

        """
        exp4 = lisp.SExpression(self.exp4)
        #for index in xrange(14):
        #    self.assertEquals(exp4[index], answers[index])

    def test_evalExpressions(self):
        """

        """
        answers = [4, 5, 1, 2, -3, 0.25, 6.75]
        for expected, exp in zip(answers, self.exps):
            self.assertEquals(lisp.SExpression(exp).eval(), expected)

