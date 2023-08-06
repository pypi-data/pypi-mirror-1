"""
Utility functions for Evolve.
"""

# operators and their ranks
arities = {
    0: [],
    1: ['abs', 'floor', 'ceil'],
    2: ['+', '-', '*', '/'],
}

def getArity(funcName):
    """
    Arity represents the rank of a function, or how many operands (arguments)
    it takes.
    """
    for arity, funcs in arities.items():
        if funcName in funcs:
            return arity
    # everything else, assume to be a constant
    return 0

class DynamicList(list):
    """
    A list that pre-populates as needed.
    """
    def __setitem__(self, index, value):
        start = len(self)
        end = index
        if end >= start:
            self.extend([None for x in xrange(end-start+1)])
        try:
            super(DynamicList, self).__setitem__(index, value)
        except:
            import pdb;pdb.set_trace()
