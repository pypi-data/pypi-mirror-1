import datetime
import pickle
import sys
import unittest

import dejavu
from dejavu import logic

nums = logic.codewalk.numeric_opcodes

lx = "logic.Expression(lambda x: "


class ExpressionTests(unittest.TestCase):
    
    def test_Expression_creation(self):
        e = logic.Expression(lambda x: dejavu.icontains(x.Status, 'c'))
        self.assertEqual(repr(e), lx + "dejavu.icontains(x.Status, 'c'))")
        self.assertEqual(e.func.func_code.co_code,
                         'd\x03\x00|\x00\x00i\x03\x00d\x01\x00\x83\x02\x00S')
        
        # 4/28/04: This one failed in endue.html.nav,
        # because 'field' was a Unicode string, which crashed
        # the interpreter when fed as part of co_names.
        def build_expr(field, criteria):
            k = lambda x: dejavu.icontains(getattr(x, field), criteria)
            return logic.Expression(k)
        e = build_expr(u'GroupName', u'Westmin')
        self.assertEqual(repr(e), lx + "dejavu.icontains(x.GroupName, u'Westmin'))")
        
        # Test that tainted functions don't get bound early.
        e = logic.Expression(lambda x: x.FirstDate > dejavu.today())
        self.assertEqual(repr(e), lx + "x.FirstDate > dejavu.today())")
        
        # Test unary unit functions (as opposed to attributes)
        e = logic.Expression(lambda x: x.has('Job') and x.Field == 'BC')
        self.assertEqual(repr(e), lx + "(x.has('Job')) and (x.Field == 'BC'))")
        e = logic.Expression(lambda x: not x.has('Job') and x.Field == 'BC')
        self.assertEqual(repr(e), lx + "(not (x.has('Job'))) and (x.Field == 'BC'))")
        
        # Test multiple args.
        e = logic.Expression(lambda x, y, z: x.Field == 'BC' and
                                             y.Qty > 3 and z.Qty < 20)
        self.assertEqual(repr(e),
                         "logic.Expression(lambda x, y, z: (x.Field == 'BC')"
                         " and ((y.Qty > 3) and (z.Qty < 20)))")
        
        # Test the 'in' operator.
        e = logic.Expression(lambda x: x.Name in ['George', 'John'])
        self.assertEqual(repr(e), lx + "x.Name in ['George', 'John'])")
    
    def test_pickling(self):
        # Test __setstate__
        e = logic.Expression(lambda x: True)
        e.__setstate__(("lambda x: x.TripStatus != 'Inquiry' and x.Field "
                        "== 'BC' and x.StartDate >= 3", {}))
        self.assertEqual(e.code(),
                         "lambda x: (x.TripStatus != 'Inquiry') and ((x.Field "
                         "== 'BC') and (x.StartDate >= 3))")
        
        # Test Expression pickling
        e = logic.Expression(lambda x: x.LastDate > datetime.date(2004, 3, 1))
        p = pickle.dumps(e)
        f = pickle.loads(p)
        self.assertEqual(repr(e), repr(f))
        
        e = logic.Expression(lambda x: dejavu.icontains(x.Status, 'c'))
        p = pickle.dumps(e)
        f = pickle.loads(p)
        self.assertEqual(repr(e), repr(f))
    
    def test_Expression_addition(self):
        a = lambda x: x.Date == 3
        b = lambda x: x.Qty == 5
        e = logic.Expression(a)
        e += logic.Expression(b)
        self.assertEqual(e.code(), "lambda x: (x.Date == 3) and (x.Qty == 5)")
        
        # This failed in endue.price_filter on 11/14/2005,
        # due to bug #25 (Python 2.4 changed JUMP targets).
        f = logic.Expression(lambda x: ((x.DateFrom == None or x.DateFrom <= datetime.date(2005, 11, 17))
                                        and (x.DateTo == None or x.DateTo >= datetime.date(2005, 11, 17))))
        f += logic.Expression(lambda x: x.DirectoryID == None or x.DirectoryID == 0)
        self.assertEqual(f.code(),
            'lambda x: (((x.DateFrom == None) or (x.DateFrom <= datetime.date(2005, 11, 17))) '
            'and ((x.DateTo == None) or (x.DateTo >= datetime.date(2005, 11, 17)))) '
            'and ((x.DirectoryID == None) or (x.DirectoryID == 0))')
    
    def test_Aggregator(self):
        a = lambda x: x.Date == 3
        b = lambda x: x.Qty == 5
        merged_code = nums(['LOAD_FAST', 0, 0,
                            'LOAD_ATTR', 1, 0,
                            'LOAD_CONST', 1, 0,
                            'COMPARE_OP', 2, 0,
                            'JUMP_IF_FALSE', 13, 0,
                            'POP_TOP',
                            'LOAD_FAST', 0, 0,
                            'LOAD_ATTR', 2, 0,
                            'LOAD_CONST', 2, 0,
                            'COMPARE_OP', 2, 0,
                            'RETURN_VALUE'])
        # Test aggregation.
        ag = logic.Aggregator(a)
        ag.and_combine(b)
        self.assertEqual(ag.bytecode(), merged_code)
        
        # Combine another. Change the name of the first arg and add kwargs.
        ag.and_combine(lambda y, **kw: y.Size < kw['Size'])
        self.assertEqual(ag.bytecode(), nums(['LOAD_FAST', 0, 0,
                                              'LOAD_ATTR', 1, 0,
                                              'LOAD_CONST', 1, 0,
                                              'COMPARE_OP', 2, 0,
                                              'JUMP_IF_FALSE', 13, 0,
                                              'POP_TOP',
                                              'LOAD_FAST', 0, 0,
                                              'LOAD_ATTR', 2, 0,
                                              'LOAD_CONST', 2, 0,
                                              'COMPARE_OP', 2, 0,
                                              'JUMP_IF_FALSE', 17, 0,
                                              'POP_TOP',
                                              'LOAD_FAST', 0, 0,
                                              'LOAD_ATTR', 3, 0,
                                              'LOAD_FAST', 1, 0,
                                              'LOAD_CONST', 3, 0,
                                              'BINARY_SUBSCR',
                                              'COMPARE_OP', 0, 0,
                                              'RETURN_VALUE']))
        f = ag.function()
        if sys.hexversion >= (2 << 24 | 4 << 16):
            # Python 2.4+
            self.assertEqual(logic.Expression(f).code(),
                             "lambda x, **kw: ((x.Date == 3) and (x.Qty == 5)) "
                             "and (x.Size < kw['Size'])")
        else:
            # Python 2.3-
            f2 = lambda x, **kw: ((x.Date == 3) and x.Qty == 5) and x.Size < kw['Size']
            self.assertEqual(logic.Expression(f).code(), logic.Expression(f2).code())
            self.assertEqual(f.func_code.co_code, f2.func_code.co_code)
        
        # This one failed on junct.membership, because the co_name
        # mapping was screwed up (I assumed co_names[0] == arg[0]).
        ag = logic.Aggregator(lambda x, **kw: x.GroupID == u'4')
        newfunc = lambda x, **kw: x.UserID == u'rbre'
        ag.and_combine(newfunc)
        self.assertEqual(ag.instr_index, ([None] * 12 +
                                          [ag.instr_index[12]] * 17))
        # Assert the mixed code (before renumbering consts)
        self.assertEqual(ag._bytecode, nums(['LOAD_FAST', 0, 0,
                                             'LOAD_ATTR', 1, 0,
                                             'LOAD_CONST', 1, 0,
                                             'COMPARE_OP', 2, 0,
                                             'JUMP_IF_FALSE', 13, 0,
                                             'POP_TOP',
                                             'LOAD_FAST', 0, 0,
                                             'LOAD_ATTR', 1, 0,
                                             'LOAD_CONST', 1, 0,
                                             'COMPARE_OP', 2, 0,
                                             'RETURN_VALUE']))
        # Assert the final, mixed code
        self.assertEqual(ag.bytecode(), nums(['LOAD_FAST', 0, 0,
                                              'LOAD_ATTR', 1, 0,
                                              'LOAD_CONST', 1, 0,
                                              'COMPARE_OP', 2, 0,
                                              'JUMP_IF_FALSE', 13, 0,
                                              'POP_TOP',
                                              'LOAD_FAST', 0, 0,
                                              'LOAD_ATTR', 2, 0,
                                              'LOAD_CONST', 2, 0,
                                              'COMPARE_OP', 2, 0,
                                              'RETURN_VALUE']))
    
    def test_filter(self):
        f = logic.filter(Date=3)
        self.assertEqual(map(ord, f.func.func_code.co_code),
                         nums(['LOAD_FAST', 0, 0,
                               'LOAD_ATTR', 1, 0,
                               'LOAD_CONST', 1, 0,
                               'COMPARE_OP', 2, 0,
                               'RETURN_VALUE']))
        
        f = logic.filter(Name='Harry', Weight=300)
        self.assertEqual(map(ord, f.func.func_code.co_code),
                         nums(['LOAD_FAST', 0, 0,
                               'LOAD_ATTR', 1, 0,
                               'LOAD_CONST', 1, 0,
                               'COMPARE_OP', 2, 0,
                               'JUMP_IF_FALSE', 13, 0,
                               'POP_TOP',
                               'LOAD_FAST', 0, 0,
                               'LOAD_ATTR', 2, 0,
                               'LOAD_CONST', 2, 0,
                               'COMPARE_OP', 2, 0,
                               'RETURN_VALUE']))
    
    def test_comparison(self):
        f = logic.comparison('Name', 2, 'Harry')
        g = logic.Expression(lambda x: x.Name == 'Harry')
        self.assertEqual(f.func.func_code, g.func.func_code)
        
        f = logic.comparison('Size', 4, 300)
        g = logic.Expression(lambda x: x.Size > 300)
        self.assertEqual(f.func.func_code, g.func.func_code)
        
        f = logic.comparison(u'ID', 2, u'30003')
        g = logic.Expression(lambda x: x.ID == u'30003')
        self.assertEqual(f.func.func_code, g.func.func_code)


if __name__ == "__main__":
    unittest.main(__name__)

