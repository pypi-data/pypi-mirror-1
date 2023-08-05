import datetime
try:
    import fixedpoint
except ImportError:
    fixedpoint = None

import sys
if sys.version_info >= (2, 5):
    # Python 2.5 stopped putting arguments in co_names,
    # and stopped prepending None to co_consts (except when CO_NESTED?).
    idx = 0
else:
    idx = 1


import unittest

from dejavu import codewalk
nums = codewalk.numeric_opcodes

amount = 5
a = [1,2,3,4,5]
f = [lambda x: x in a,
     lambda x: x + datetime.date(2004, 1, 1),
     lambda x, **kw: (x.Date == datetime.date(2004, 1, 1)
                      and x.Qty < kw['Size']),
     # Mix names from globals, locals, attrs
     lambda x, amount: (4 != x.amount) or (amount * 3 > 20),
     lambda x: 3 * 4 * 5 * x,
     lambda x: a[2:4] == -x['offset'],
     lambda x: amount == 5 or amount == x.Qty,
     lambda x: not (x.a == 3 and (x.b > 1 or x.b < -10)),
     # Unicode const
     lambda x: x.Name == u'Dimsdale',
     # getattr
     lambda x: getattr(x, 'Name') == u'Dimsdale',
     # multiple args
     lambda x, y, z, **kw: x.Qty > 1 and y.Qty > 20 and z.Type == 'A',
     ]

# Closure example = f[11]
def foo():
    a = 5
    def bar():
        return a + 5
    return bar
f.append(foo())

if fixedpoint:
     f.append(lambda x: x.Amount > fixedpoint.FixedPoint(3, 2))

fcode = [func.func_code.co_code for func in f]


class VisitorTests(unittest.TestCase):
    
    def test_safe_tuple(self):
        l = ['logic', 'icontains', 'getattr', 'x', 'field', 'criteria', u'GroupName']
        self.assertEqual(codewalk.safe_tuple(l), ('logic', 'icontains', 'getattr',
                                                  'x', 'field', 'criteria', 'GroupName'))
    
    def test_Localizer(self):
        r = codewalk.Localizer(f[0]).bytecode()
        self.assertEqual(r, nums(['LOAD_FAST', 0, 0,
                                  'LOAD_CONST', idx, 0,
                                  'COMPARE_OP', 6, 0,
                                  'RETURN_VALUE']))
        r = codewalk.Localizer(f[1]).bytecode()
        self.assertEqual(r, nums(['LOAD_FAST', 0, 0,
                                  'LOAD_CONST', idx + 2, 0,
                                  'LOAD_ATTR', idx + 1, 0,
                                  'LOAD_CONST', idx, 0,
                                  'LOAD_CONST', idx + 1, 0,
                                  'LOAD_CONST', idx + 1, 0,
                                  'CALL_FUNCTION', 3, 0,
                                  'BINARY_ADD',
                                  'RETURN_VALUE']))
        r = codewalk.Localizer(f[2]).bytecode()
        self.assertEqual(r, nums(['LOAD_FAST', 0, 0,
                                  'LOAD_ATTR', idx, 0,
                                  'LOAD_CONST', idx + 3, 0,
                                  'LOAD_ATTR', idx + 2, 0,
                                  'LOAD_CONST', idx, 0,
                                  'LOAD_CONST', idx + 1, 0,
                                  'LOAD_CONST', idx + 1, 0,
                                  'CALL_FUNCTION', 3, 0,
                                  'COMPARE_OP', 2, 0,
                                  'JUMP_IF_FALSE', 17, 0,
                                  'POP_TOP',
                                  'LOAD_FAST', 0, 0,
                                  'LOAD_ATTR', idx + 3, 0,
                                  'LOAD_FAST', 1, 0,
                                  'LOAD_CONST', idx + 2, 0,
                                  'BINARY_SUBSCR',
                                  'COMPARE_OP', 0, 0,
                                  'RETURN_VALUE']))
        
        r = codewalk.Localizer(f[3]).bytecode()
        self.assertEqual(r, nums(['LOAD_CONST', idx, 0,
                                  'LOAD_FAST', 0, 0,
                                  'LOAD_ATTR', idx, 0,
                                  'COMPARE_OP', 3, 0,
                                  'JUMP_IF_TRUE', 14, 0,
                                  'POP_TOP',
                                  'LOAD_FAST', 1, 0,
                                  'LOAD_CONST', idx + 1, 0,
                                  'BINARY_MULTIPLY',
                                  'LOAD_CONST', idx + 2, 0,
                                  'COMPARE_OP', 4, 0,
                                  'RETURN_VALUE']))
    
    def test_EarlyBinder(self):
        r = codewalk.EarlyBinder(f[1]).bytecode()
        self.assertEqual(r, nums(['LOAD_FAST', 0, 0,
                                  'LOAD_CONST', idx + 4, 0,
                                  'BINARY_ADD',
                                  'RETURN_VALUE']))
        r = codewalk.EarlyBinder(f[2]).bytecode()
        self.assertEqual(r, nums(['LOAD_FAST', 0, 0,
                                  'LOAD_ATTR', idx, 0,
                                  'LOAD_CONST', idx + 5, 0,
                                  'COMPARE_OP', 2, 0,
                                  'JUMP_IF_FALSE', 17, 0,
                                  'POP_TOP',
                                  'LOAD_FAST', 0, 0,
                                  'LOAD_ATTR', idx + 3, 0,
                                  'LOAD_FAST', 1, 0,
                                  'LOAD_CONST', idx + 2, 0,
                                  'BINARY_SUBSCR',
                                  'COMPARE_OP', 0, 0,
                                  'RETURN_VALUE']))
        r = codewalk.EarlyBinder(f[4]).bytecode()
        self.assertEqual(r, nums(['LOAD_CONST', idx + 4, 0,
                                  'LOAD_FAST', 0, 0,
                                  'BINARY_MULTIPLY',
                                  'RETURN_VALUE']))
        r = codewalk.EarlyBinder(f[5]).bytecode()
        self.assertEqual(r, nums(['LOAD_CONST', idx + 4, 0,
                                  'LOAD_FAST', 0, 0,
                                  'LOAD_CONST', idx + 2, 0,
                                  'BINARY_SUBSCR',
                                  'UNARY_NEGATIVE',
                                  'COMPARE_OP', 2, 0,
                                  'RETURN_VALUE']))
        r = codewalk.EarlyBinder(f[6]).bytecode()
        self.assertEqual(r, nums(['LOAD_CONST', idx + 1, 0,
                                  'JUMP_IF_TRUE', 13, 0,
                                  'POP_TOP',
                                  'LOAD_CONST', idx, 0,
                                  'LOAD_FAST', 0, 0,
                                  'LOAD_ATTR', idx + 1, 0,
                                  'COMPARE_OP', 2, 0,
                                  'RETURN_VALUE']))
        r = codewalk.EarlyBinder(f[9]).bytecode()
        self.assertEqual(r, nums(['LOAD_FAST', 0, 0,
                                  # 2, since co_names was ('getattr', 'x').
                                  'LOAD_ATTR', idx + 1, 0,
                                  'LOAD_CONST', idx + 1, 0,
                                  'COMPARE_OP', 2, 0,
                                  'RETURN_VALUE']))
        # Test a tainted (late-bound) function
        e = lambda x: x.FirstDate >= datetime.date.today()
        r = codewalk.EarlyBinder(e, bind_late=[datetime.date.today]).bytecode()
        self.assertEqual(r, nums(['LOAD_FAST', 0, 0,
                                  'LOAD_ATTR', idx, 0,
                                  'LOAD_CONST', idx + 2, 0,
                                  'CALL_FUNCTION', 0, 0,
                                  'COMPARE_OP', 5, 0,
                                  'RETURN_VALUE']))
        
        # Closures (dereferencing of func_closure)
        r = codewalk.EarlyBinder(f[11]).bytecode()
        if sys.version_info >= (2, 4):
            # This bytecode changed for Python 2.4.
            # Oddly enough, it didn't change from 2.4 to 2.5
            # like other LOAD_CONST (because of CO_NESTED?).
            self.assertEqual(r, nums(['LOAD_CONST', 2, 0,
                                      'RETURN_VALUE']))
        else:
            self.assertEqual(r, nums(['LOAD_CONST', idx + 1, 0,
                                      'RETURN_VALUE',
                                      'LOAD_CONST', 0, 0,
                                      'RETURN_VALUE']))
    
    def test_LambdaDecompiler(self):
        s = ['lambda x: x in a',
             'lambda x: x + datetime.date(2004, 1, 1)',
             "lambda x, **kw: (x.Date == datetime.date(2004, 1, 1)) and (x.Qty < kw['Size'])",
             "lambda x, amount: (4 != x.amount) or (amount * 3 > 20)",
             ]
        if sys.version_info >= (2, 5):
            # Python 2.5 collapses constants where possible.
            s.append("lambda x: 60 * x")
        else:
            s.append("lambda x: 3 * 4 * 5 * x")
        s.extend([
             "lambda x: a[2:4] == -(x['offset'])",
             "lambda x: (amount == 5) or (amount == x.Qty)",
             "lambda x: not ((x.a == 3) and ((x.b > 1) or (x.b < -10)))",
             "lambda x: x.Name == u'Dimsdale'",
             "lambda x: getattr(x, 'Name') == u'Dimsdale'",
             "lambda x, y, z, **kw: (x.Qty > 1) and ((y.Qty > 20) and (z.Type == 'A'))",
             "",
             ])
        if fixedpoint:
            s.append("lambda x: x.Amount > fixedpoint.FixedPoint(3, 2)")
        for funcitem, stritem in zip(f, s):
            if stritem: # Skip the closure one until I can write a lambda equivalent
                r = codewalk.LambdaDecompiler(funcitem).code()
                self.assertEqual(r, stritem)
    
    def test_BranchTracker(self):
        r = codewalk.BranchTracker(f[6]).branches()
        self.assertEqual(r, [9, 22])
    
    def test_KeywordInspector(self):
        e = lambda x, **kw: x.Size > kw['Size']
        self.assertEqual(codewalk.KeywordInspector(e).kwargs(), ["Size"])
        e = lambda x: x.Size > kw['Size']
        self.assertRaises(ValueError, codewalk.KeywordInspector, e)
        e = lambda x, **kw: x.Date > x.newdate(kw['Year'], 1, 1)
        self.assertEqual(codewalk.KeywordInspector(e).kwargs(), ["Year"])


if __name__ == "__main__":
    unittest.main(__name__)

