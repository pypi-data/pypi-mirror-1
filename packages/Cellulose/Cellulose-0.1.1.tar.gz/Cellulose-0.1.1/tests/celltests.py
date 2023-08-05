import sys
sys.path.insert(0, '../')
import cellulose
from cellulose import InputCell, ComputedCell, CellList, CellDict, ComputedDict
import unittest


class ChangeCountingCell(cellulose.DependantCell):
    def __init__(self):
        cellulose.DependantCell.__init__(self)
        self.dep_changed_count = 0
        self.dep_possibly_changed_count = 0

    def dependency_changed(self):
        self.dep_changed_count += 1

    def dependency_possibly_changed(self, dependency):
        self.dep_possibly_changed_count += 1


class InputCellTest(unittest.TestCase):
    def setUp(self):
        self.cell = InputCell()
        self.cell.value = 0

    def test_dependency_alert(self):
        c = ChangeCountingCell()
        c.push()
        self.cell.get()
        c.pop()
        self.cell.value = 1
        self.assertEqual(c.dep_changed_count, 1)

    def test_dependency_weakref_release(self):
        c = ComputedCell(self.cell.get)
        self.assertEqual(c.value, 0)
        self.assertEqual(len(self.cell.dependants), 1)
        del c
        self.assertEqual(len(self.cell.dependants), 0)


class ComputedCellTest(unittest.TestCase):
    def setUp(self):
        self.cell = ComputedCell()
        self.depended_cell_a = InputCell()
        self.depended_cell_b = InputCell()
        self.depended_cell_a.value = 1
        self.depended_cell_b.value = 2

        def check():
            if self.depended_cell_a.value == 1:
                return "a == 1"
            else:
                return "b == %d" % self.depended_cell_b.value
        self.cell.set_function(check)

    def test_correct_response(self):
        self.assertEqual(self.cell.value, "a == 1")

    def test_dependency_registered(self):
        self.assertEqual(self.cell.value, "a == 1")
        self.assertEqual(len(self.depended_cell_a.dependants), 1)
        self.assert_(id(self.cell) in self.depended_cell_a.dependants)
        self.assert_(id(self.depended_cell_a) in self.cell.dependencies)

    def test_dependency_kept(self):
        self.assertEqual(self.cell.value, "a == 1")
        self.depended_cell_a.value = 2
        self.assertEqual(self.cell.value, "b == 2")
        self.assert_(id(self.cell) in self.depended_cell_a.dependants)
        self.assert_(id(self.depended_cell_a) in self.cell.dependencies)
        self.assert_(id(self.cell) in self.depended_cell_b.dependants)
        self.assert_(id(self.depended_cell_b) in self.cell.dependencies)


    def test_dependency_alert(self):
        c = ChangeCountingCell()
        c.push()
        self.cell.get()
        c.pop()
        # b should not yet be depended upon.
        self.depended_cell_b.value = 5
        self.assertEqual(c.dep_possibly_changed_count, 0)
        self.assertEqual(c.dep_changed_count, 0)
        self.depended_cell_a.value = 2
        self.assertEqual(c.dep_possibly_changed_count, 1)
        self.assertEqual(c.dep_changed_count, 0)
        self.assertEqual(self.cell.value, 'b == 5')
        self.assertEqual(c.dep_possibly_changed_count, 1)
        self.assertEqual(c.dep_changed_count, 1)

    def test_lazy_calculation(self):
        c = ComputedCell(lambda: self.cell.value)
        self.assertEqual(c.value, 'a == 1')
        self.depended_cell_a.value = 2
        self.assert_(self.cell._dirty)
        self.assertFalse(c._dirty)
        self.assert_(id(self.cell) in c._possibly_changed_dependencies)
        self.assertEqual(c.value, 'b == 2')

    def test_dependency_weakref_release(self):
        self.cell.value
        del self.cell
        self.assertEqual(len(self.depended_cell_a.dependants), 0)


class DeepDependencyTest(unittest.TestCase):
    def setUp(self):
        class TestInputCell(InputCell):
            deep_dependencies = None # Overide property
        self.cell_a = TestInputCell(1)
        self.cell_a.deep_dependencies = set(('dep',))
        self.cell_b = ComputedCell(lambda: self.cell_a.value)
        self.cell_c = ComputedCell(lambda: self.cell_b.value)

    def test_deep(self):
        self.assertEqual(self.cell_a.deep_dependencies, set(('dep',)))
        self.assertEqual(self.cell_c.deep_dependencies, set(('dep',)))

    def test_deep_dep_change(self):
        self.cell_a.deep_dependencies = set(('dep2',))
        self.assertEqual(self.cell_c.deep_dependencies, set(('dep2',)))

    def test_dep_change(self):
        self.cell_b.function = lambda: 1
        self.assertEqual(self.cell_c.deep_dependencies, set())
        self.assertEqual(self.cell_b.deep_dependencies, set())


class PentagramTest(unittest.TestCase):
    def runTest(self):
        """
        Tests agains this:
        http://pyworks.org/pipermail/pycells/2006-June/000157.html
        """
        X = InputCell()
        X.value = '(X is input)'
        A = ComputedCell(lambda: '(A is '+C.value+X.value+')')
        B = ComputedCell(lambda: '(B is '+X.value+')')
        C = ComputedCell(lambda: '(C is '+B.value+')')
        H = ComputedCell(lambda: '(H is '+A.value+C.value+X.value+')')

        c = ChangeCountingCell()
        c.push()
        self.assertEqual(H.value, '(H is (A is (C is (B is (X is input)))'+
            '(X is input))(C is (B is (X is input)))(X is input))')
        c.pop()
        self.assertEqual(len(c.dependencies), 1)
        X.value = '(X is changed)'
        self.assertEqual(H.value, '(H is (A is (C is (B is (X is changed)))'+
            '(X is changed))(C is (B is (X is changed)))(X is changed))')

class AnotherTest(unittest.TestCase):
    def runTest(self):
        c1 = InputCell()
        c1.value = 1
        c2 = ComputedCell(c1.get)
        c3 = ChangeCountingCell()
        c3.push()
        c2.get()
        c3.pop()
        self.assertEqual(c3.dep_possibly_changed_count, 0)
        c1.value = 2
        self.assertEqual(len(c1.dependants), 1)
        self.assertEqual(c3.dep_possibly_changed_count, 1)
        c2.get()
        self.assertEqual(len(c1.dependants), 1)
        c1.value = 3
        self.assertEqual(c2.get(), 3)
        self.assertEqual(c3.dep_possibly_changed_count, 2)


class CellListTest(unittest.TestCase):
    def test_regression(self):
        # This is more of a regression test.
        l = CellList(['a','b','c'])
        self.assertEqual(l, ['a','b','c'])
        c = ComputedCell(lambda: ' '.join(l))
        self.assertEqual(c.value, 'a b c')
        l.append('d')
        self.assertEqual(c.value, 'a b c d')

    def test_len(self):
        l = CellList(['a','b','c'])
        c = ChangeCountingCell()
        c.push()
        len(l)
        c.pop()
        self.assertEqual(len(l), 3)
        self.assertEqual(c.dep_changed_count, 0)
        self.assertEqual(c.dep_possibly_changed_count, 0)

        l[0] = 'z'
        self.assertEqual(len(l), 3)
        self.assertEqual(c.dep_changed_count, 0)
        self.assertEqual(c.dep_possibly_changed_count, 1)

        l.append('a')
        self.assertEqual(len(l), 4)
        self.assertEqual(c.dep_changed_count, 1)
        self.assertEqual(c.dep_possibly_changed_count, 2)


class CellDictTest(unittest.TestCase):

    def test_getitem(self):
        c = CellDict(one=1, two=2)
        counter = ChangeCountingCell()
        cellulose.dependant_cell_stack.push(counter)
        self.assertEqual(c['one'], 1)
        cellulose.dependant_cell_stack.pop(counter)
        self.assertEqual(len(counter.dependencies), 1)
        c['one'] = 1
        self.assertEqual(counter.dep_changed_count, 0)
        c['one'] = 2
        self.assertEqual(counter.dep_changed_count, 1)
        c['two'] = 3 # Should not depend on key 'two'
        self.assertEqual(counter.dep_changed_count, 1)

    def test_contains(self):
        # Note that this does not check for the condition of a value changing,
        # without changing if the dict contains the key.
        c = CellDict(one=1, two=2)
        counter = ChangeCountingCell()
        cellulose.dependant_cell_stack.push(counter)
        self.assertTrue('one' in c)
        self.assertFalse('three' in c)
        cellulose.dependant_cell_stack.pop(counter)
        self.assertEqual(len(counter.dependencies), 2)
        del c['one']
        self.assertEqual(counter.dep_changed_count, 1)
        c['two'] = 3 # Should not depend on key 'two'
        self.assertEqual(counter.dep_changed_count, 1)
        c['three'] = 3
        self.assertEqual(counter.dep_changed_count, 2)

    def test_items(self):
        c = CellDict(one=1, two=2)
        counter = ChangeCountingCell()
        cellulose.dependant_cell_stack.push(counter)
        self.assertEqual(set(c.items()), set((('one', 1), ('two', 2))))
        cellulose.dependant_cell_stack.pop(counter)
        c['three'] = 3
        self.assertEqual(counter.dep_changed_count, 1)
        c['one'] = 1
        self.assertEqual(counter.dep_changed_count, 1)
        c['one'] = 2
        self.assertEqual(counter.dep_changed_count, 2)

    def test_update(self):
        c = CellDict(one=1, two=2)
        counter = ChangeCountingCell()
        cellulose.dependant_cell_stack.push(counter)
        'one' in c, 'three' in c
        cellulose.dependant_cell_stack.pop(counter)
        c.update(three=3)
        self.assertEqual(counter.dep_changed_count, 1)
        c.update(two=3, three=3)
        self.assertEqual(counter.dep_changed_count, 1)
        c.update(one=2, four=4)
        self.assertEqual(counter.dep_changed_count, 2)


class TestComputedDict(unittest.TestCase):
    # TODO this doesn't actually test for full cellulose integration.
    keys = None
    def setUp(self):
        self.factor_cell = InputCell()
        self.factor_cell.value = 2

        self.cd = ComputedDict((lambda k: k*self.factor_cell.value), self.keys)

    def test_common(self):
        # These are some tests for both with and without valid_keys
        # TODO test for proper behavior with dependency discovery, change
        # TODO notification, etc.  Also test for the cache_values feature.
        self.assertEqual(self.cd[1], 2)
        self.assertEqual(self.cd["string"], "stringstring")

        self.factor_cell.value = 3

        self.assertEqual(self.cd[1], 3)

    def test_discard_cache(self):
        self.assertTrue(self.cd.discard_cache)  # Default value
        cc = ComputedCell(lambda: self.cd['string'])

        self.assertEqual(cc.value, "stringstring")
        self.assertTrue("string" in self.cd._key_subcells)
        del cc
        self.assertFalse("string" in self.cd._key_subcells)

    def test_keep_cache(self):
        self.cd.discard_cache = False
        cc = ComputedCell(lambda: self.cd['string'])

        self.assertEqual(cc.value, "stringstring")
        self.assertTrue("string" in self.cd._key_subcells)
        del cc
        self.assertTrue("string" in self.cd._key_subcells)

class TestComputedDictWithoutKeys(TestComputedDict):
    keys = None
    def test_without_keys(self):
        self.assertEqual(self.cd.valid_keys, None)

        self.assertRaises(AttributeError, lambda: self.cd.get('key','default'))
        self.assertRaises(AttributeError, lambda: 'key' in self.cd)
        for n in ('items', 'keys', 'values', '__len__', '__iter__'):
            self.assertRaises(AttributeError, getattr(self.cd, n))


class TestComputedDictWithKeys(TestComputedDict):
    keys = [1,2,3,4,5, "string", ("a", "tuple")]

    def test_KeyError(self):
        self.assertRaises(KeyError, (lambda:self.cd['invalidkey']))

    def test_keys(self):
        self.assertEqual(self.keys, self.cd.keys())

    def test_items(self):
        self.assertEqual(self.cd.items(), [(k, k*2) for k in self.keys])

    def test_values(self):
        self.assertEqual(self.cd.values(), [k*2 for k in self.keys])

    def test_len(self):
        self.assertEqual(len(self.cd), len(self.keys))

    def test_get(self):
        self.assertEqual(self.cd.get("string","default"), "stringstring")
        self.assertEqual(self.cd.get("invalidkey","default"), "default")

    def test_contains(self):
        self.assertTrue("string" in self.cd)
        self.assertFalse("invalidkey" in self.cd)

    def test_has_key(self):
        self.assertTrue(self.cd.has_key("string"))
        self.assertFalse(self.cd.has_key("invalidkey"))

    def test_iter(self):
        self.assertTrue(hasattr(iter(self.cd), 'next'))
        self.assertEqual(list(iter(self.cd)), self.keys)



class TestAutoCells(unittest.TestCase):
    def runTest(self):
        class TestClass(cellulose.AutoCells):
            def _get_result(self):
                return self.a + self.b
        c = TestClass()
        counter = ChangeCountingCell()
        c.a = 1
        c.b = 2
        cellulose.dependant_cell_stack.push(counter)
        self.assertEqual(c.result, 3)
        cellulose.dependant_cell_stack.pop(counter)

        c.a = 2
        self.assertEqual(counter.dep_possibly_changed_count, 1)
        self.assertEqual(counter.dep_changed_count, 0)

        self.assertEqual(c.result, 4)
        self.assertEqual(counter.dep_changed_count, 1)



if __name__ == "__main__":
    unittest.main()
