import os
import tempfile
import unittest

import aglyph.definition


class EvaluatorTest(unittest.TestCase):

    def test_evaluate_dict(self):
        kvpairs = [
            ["key", "value"],
            [aglyph.definition.Evaluator(tuple, [2, 3, 5, 7]), "tuple"],
            ["list", aglyph.definition.Evaluator(list, [11, 13, 17, 19])],
            ]
        dict_eval1 = aglyph.definition.Evaluator(dict, kvpairs)
        dict1 = dict_eval1.evaluate()
        self.assert_(isinstance(dict1, dict),
            "dict_eval1.evaluate() is not a dictionary")
        self.assertNotEqual(id(dict1), id(dict_eval1.evaluate()),
            "dict_eval1.evaluate() did not create a new instance")
        self.assertEqual(dict1["key"], "value", "dict1['key'] != 'value'")
        self.assertEqual(dict1[(2, 3, 5, 7)],
            "tuple", "dict1[(2, 3, 5, 7)] != 'tuple'")
        self.assertEqual(dict1["list"], [11, 13, 17, 19],
            "dict1['list'] != [11, 13, 17, 19]")
        dict_eval2 = aglyph.definition.Evaluator(
            dict, foof="spam", eggs="crap", what="what")
        dict2 = dict_eval2.evaluate()
        self.assert_(isinstance(dict2, dict),
            "dict_eval2.evaluate() is not a dictionary")
        self.assertNotEqual(id(dict2), id(dict_eval2.evaluate()),
            "dict_eval2.evaluate() did not create a new instance")
        self.assertEqual(dict2["foof"], "spam", "dict2['foof'] != 'spam'")
        self.assertEqual(dict2["eggs"], "crap", "dict2['eggs'] != 'crap'")
        self.assertEqual(dict2["what"], "what", "dict2['what'] != 'what'")
        dict_eval3 = aglyph.definition.Evaluator(
            dict, {"foof": "spam", "eggs": "crap"})
        dict3 = dict_eval3.evaluate()
        self.assert_(isinstance(dict3, dict),
            "dict_eval3.evaluate() is not a dictionary")
        self.assertNotEqual(id(dict3), id(dict_eval3.evaluate()),
            "dict_eval3.evaluate() did not create a new instance")
        self.assertEqual(dict3, {"foof": "spam", "eggs": "crap"},
            "dict3 != {'foof': 'spam', 'eggs': 'crap'}")

    def test_evaluate_enumerate(self):
        l1 = ["zero", "one", "two", "three"]
        enum_eval1 = aglyph.definition.Evaluator(enumerate, l1)
        enum1 = enum_eval1.evaluate()
        self.assert_(isinstance(enum1, enumerate),
            "enum_eval1.evaluate() is not an enumerate")
        self.assertNotEqual(id(enum1), id(enum_eval1.evaluate()),
            "enum_eval1.evaluate() did not create a new instance")
        for i in range(len(l1)):
            expected = (i, l1[i])
            self.assertEqual(enum1.next(), expected,
                "enum1.next() != (%d, %r)" % expected)
        self.failUnlessRaises(StopIteration, enum1.next)
        l2 = [
            aglyph.definition.Evaluator(list, ["spam", "and", "eggs"]),
            aglyph.definition.Evaluator(tuple, [1, 2, 3]),
            aglyph.definition.Evaluator(dict, foof="crap", what="what"),
            ]
        enum_eval2 = aglyph.definition.Evaluator(enumerate, l2)
        enum2 = enum_eval2.evaluate()
        self.assert_(isinstance(enum2, enumerate),
            "enum_eval2.evaluate() is not an enumerate")
        self.assertNotEqual(id(enum2), id(enum_eval2.evaluate()),
            "enum_eval2.evaluate() did not create a new instance")
        for i in range(len(l2)):
            expected = (i, l2[i].evaluate())
            self.assertEqual(enum2.next(), expected,
                "enum2.next() != (%d, %r)" % expected)
        self.failUnlessRaises(StopIteration, enum2.next)

    def test_evaluate_file(self):
        (fd, fn) = tempfile.mkstemp()
        os.write(fd, "first line\n")
        os.close(fd)
        file_eval = aglyph.definition.Evaluator(file, fn, 'a')
        fp1 = file_eval.evaluate()
        self.assert_(isinstance(fp1, file),
            "file_eval.evaluate() #1 is not a file")
        fp1.close()
        fp2 = file_eval.evaluate()
        self.assert_(isinstance(fp2, file),
            "file_eval.evaluate() #2 is not a file")
        fp2.write("second line\n")
        fp2.close()
        self.assertNotEqual(id(fp1), id(fp2),
            "file_eval.evaluate() #1 and #2 are the same object")
        fp3 = file(fn)
        self.assertEqual(fp3.readline(), "first line\n",
            "file_eval.evaluate() - file contents not preserved")
        self.assertEqual(fp3.readline(), "second line\n",
            "file_eval.evaluate() - file contents not preserved")
        fp3.close()
        os.unlink(fn)

    def test_evaluate_frozenset(self):
        l1 = ["zero", "one", "two", "three"]
        fset_eval1 = aglyph.definition.Evaluator(frozenset, l1)
        fset1 = fset_eval1.evaluate()
        self.assert_(isinstance(fset1, frozenset),
            "fset_eval1.evaluate() is not a frozenset")
        self.assertNotEqual(id(fset1), id(fset_eval1.evaluate()),
            "fset_eval1.evaluate() did not create a new instance")
        for value in l1:
            self.assert_(value in fset1, "%r not in fset1" % value)
        (fd, fn) = tempfile.mkstemp()
        os.close(fd)
        fset_eval2 = aglyph.definition.Evaluator(
            frozenset, [fn, aglyph.definition.Evaluator(file, fn)])
        fset2 = fset_eval2.evaluate()
        self.assert_(isinstance(fset2, frozenset),
            "fset_eval2.evaluate() is not a frozenset")
        self.assertNotEqual(id(fset2), id(fset_eval2.evaluate()),
            "fset_eval2.evaluate() did not create a new instance")
        self.assertEqual(len(fset2), 2, "len(fset2) != 2")
        for value in fset2:
            if (isinstance(value, str)):
                self.assertEqual(value, fn, "fset2 value != %r" % fn)
            elif (isinstance(value, file)):
                self.assertEqual(value.name, fn, "fset2 value.name != %r" % fn)
            else:
                raise TypeError("unexpected value in fset2 (%r)" % value)
        os.unlink(fn)

    def test_evaluate_iter(self):
        l1 = ["zero", "one", "two", "three"]
        iter_eval1 = aglyph.definition.Evaluator(iter, l1)
        iter1 = iter_eval1.evaluate()
        self.assert_(type(iter1) is type(iter(l1)),
            "iter_eval1.evaluate() is not an iter")
        self.assertNotEqual(id(iter1), id(iter_eval1.evaluate()),
            "iter_eval1.evaluate() did not create a new instance")
        for value in l1:
            self.assertEqual(iter1.next(), value, "iter1.next() != %r" % value)
        self.failUnlessRaises(StopIteration, iter1.next)
        l2 = [
            aglyph.definition.Evaluator(list, ["spam", "and", "eggs"]),
            aglyph.definition.Evaluator(tuple, [1, 2, 3]),
            aglyph.definition.Evaluator(dict, foof="crap", what="what"),
            ]
        iter_eval2 = aglyph.definition.Evaluator(iter, l2)
        iter2 = iter_eval2.evaluate()
        self.assert_(type(iter2) is type(iter(l2)),
            "iter_eval2.evaluate() is not an iter")
        self.assertNotEqual(id(iter2), id(iter_eval2.evaluate()),
            "iter_eval2.evaluate() did not create a new instance")
        for value in l2:
            self.assertEqual(iter2.next(), value.evaluate(),
                "iter2.next() != %r" % value)
        self.failUnlessRaises(StopIteration, iter2.next)

    def test_evaluate_list(self):
        list_eval = aglyph.definition.Evaluator(list,
            ["zero", aglyph.definition.Evaluator(int, "1"), "two",
                aglyph.definition.Evaluator(int, "03", 8)])
        list1 = list_eval.evaluate()
        self.assertEqual(len(list1), 4, "len(list1) != 4")
        self.assertEqual(list1[0], "zero", "list1[0] != 'zero'")
        self.assertEqual(list1[1], 1, "list1[1] != 1")
        self.assertEqual(list1[2], "two", "list1[2] != 'two'")
        self.assertEqual(list1[3], 3, "list1[3] != 3")
        list2 = list_eval.evaluate()
        self.assertNotEqual(id(list1), id(list2),
            "list_eval.evaluate() #1 and #2 are the same object")
        self.assertEqual(len(list2), 4, "len(list2) != 4")
        self.assertEqual(list2, ["zero", 1, "two", 3],
            "list2 != ['zero', 1, 'two', 3]")

    def test_evaluate_set(self):
        l1 = ["zero", "one", "two", "three"]
        set_eval1 = aglyph.definition.Evaluator(set, l1)
        set1 = set_eval1.evaluate()
        self.assert_(isinstance(set1, set),
            "set_eval1.evaluate() is not a set")
        self.assertNotEqual(id(set1), id(set_eval1.evaluate()),
            "set_eval1.evaluate() did not create a new instance")
        for value in l1:
            self.assert_(value in set1, "%r not in set1" % value)
        (fd, fn) = tempfile.mkstemp()
        os.close(fd)
        set_eval2 = aglyph.definition.Evaluator(
            set, [fn, aglyph.definition.Evaluator(file, fn)])
        set2 = set_eval2.evaluate()
        self.assert_(isinstance(set2, set),
            "set_eval2.evaluate() is not a set")
        self.assertNotEqual(id(set2), id(set_eval2.evaluate()),
            "set_eval2.evaluate() did not create a new instance")
        self.assertEqual(len(set2), 2, "len(set2) != 2")
        for value in set2:
            if (isinstance(value, str)):
                self.assertEqual(value, fn, "set2 value != %r" % fn)
            elif (isinstance(value, file)):
                self.assertEqual(value.name, fn, "set2 value.name != %r" % fn)
            else:
                raise TypeError("unexpected value in set2 (%r)" % value)
        os.unlink(fn)

    def test_evaluate_tuple(self):
        tuple_eval = aglyph.definition.Evaluator(tuple,
            ["zero", aglyph.definition.Evaluator(int, "1"), "two",
                aglyph.definition.Evaluator(int, "03", 8)])
        tuple1 = tuple_eval.evaluate()
        self.assertEqual(len(tuple1), 4, "len(tuple1) != 4")
        self.assertEqual(tuple1[0], "zero", "tuple1[0] != 'zero'")
        self.assertEqual(tuple1[1], 1, "tuple1[1] != 1")
        self.assertEqual(tuple1[2], "two", "tuple1[2] != 'two'")
        self.assertEqual(tuple1[3], 3, "tuple1[3] != 3")
        tuple2 = tuple_eval.evaluate()
        self.assertNotEqual(id(tuple1), id(tuple2),
            "tuple_eval.evaluate() #1 and #2 are the same object")
        self.assertEqual(len(tuple2), 4, "len(tuple2) != 4")
        self.assertEqual(tuple2, ("zero", 1, "two", 3),
            "tuple2 != ('zero', 1, 'two', 3)")


class DefinitionTest(unittest.TestCase):

    def setUp(self):
        self.definition = aglyph.definition.Definition(
            "component_id", "package.module.ClassName", "prototype")

    def test_add(self):
        self.definition.add(
            aglyph.definition.Setter("setter_attr1", "setter_value1"))
        self.definition.add(
            aglyph.definition.NamedValue("kwarg_name1", "kwarg_value1"))
        self.definition.add(aglyph.definition.Value("arg_value1"))
        self.failUnlessRaises(TypeError, self.definition.add, object())

    def test_add_init_arg(self):
        self.definition.add_init_arg("arg_value2")

    def test_add_init_kwarg(self):
        self.definition.add_init_kwarg("kwarg_name2", "kwarg_value2")

    def test_add_setter(self):
        self.definition.add_setter("setter_attr2", "setter_value2")

    def test_get_component_id(self):
        self.assertEqual(self.definition.get_component_id(), "component_id",
            "definition.get_component_id() != 'component_id'")

    def test_get_classpath(self):
        self.assertEqual(
            self.definition.get_classpath(), "package.module.ClassName",
            "definition.get_classpath() != 'package.module.ClassName'")

    def test_get_creation_strategy(self):
        self.assertEqual(self.definition.get_creation_strategy(), "prototype",
            "definition.get_creation_strategy() != 'prototype'")

    def test_iter_init_args(self):
        self.definition.add(aglyph.definition.Value("arg_value1"))
        self.definition.add(aglyph.definition.Value("arg_value2"))
        init_args = self.definition.iter_init_args()
        next = init_args.next()
        self.assert_(isinstance(next, aglyph.definition.Value),
            "init_args.next() is not an aglyph.definition.Value")
        self.assertEqual(next.get_value(), "arg_value1",
            "next.get_value() != 'arg_value1'")
        next = init_args.next()
        self.assert_(isinstance(next, aglyph.definition.Value),
            "init_args.next() is not an aglyph.definition.Value")
        self.assertEqual(next.get_value(), "arg_value2",
            "next.get_value() != 'arg_value2'")
        self.failUnlessRaises(StopIteration, init_args.next)

    def test_iter_init_kwargs(self):
        self.definition.add(
            aglyph.definition.NamedValue("kwarg_name1", "kwarg_value1"))
        self.definition.add(
            aglyph.definition.NamedValue("kwarg_name2", "kwarg_value2"))
        init_kwargs = self.definition.iter_init_kwargs()
        next = init_kwargs.next()
        self.assert_(isinstance(next, aglyph.definition.NamedValue),
            "init_kwargs.next() is not an aglyph.definition.NamedValue")
        self.assertEqual(next.get_name(), "kwarg_name1",
            "next.get_value() != 'kwarg_name1'")
        self.assertEqual(next.get_value(), "kwarg_value1",
            "next.get_value() != 'kwarg_value1'")
        next = init_kwargs.next()
        self.assert_(isinstance(next, aglyph.definition.NamedValue),
            "init_kwargs.next() is not an aglyph.definition.NamedValue")
        self.assertEqual(next.get_name(), "kwarg_name2",
            "next.get_value() != 'kwarg_name2'")
        self.assertEqual(next.get_value(), "kwarg_value2",
            "next.get_value() != 'kwarg_value2'")
        self.failUnlessRaises(StopIteration, init_kwargs.next)

    def test_iter_setters(self):
        self.definition.add(
            aglyph.definition.Setter("setter_attr1", "setter_value1"))
        self.definition.add(
            aglyph.definition.Setter("setter_attr2", "setter_value2"))
        setters = self.definition.iter_setters()
        next = setters.next()
        self.assert_(isinstance(next, aglyph.definition.Setter),
            "setters.next() is not an aglyph.definition.Setter")
        self.assertEqual(next.get_name(), "setter_attr1",
            "next.get_value() != 'setter_attr1'")
        self.assertEqual(next.get_value(), "setter_value1",
            "next.get_value() != 'setter_value1'")
        next = setters.next()
        self.assert_(isinstance(next, aglyph.definition.Setter),
            "setters.next() is not an aglyph.definition.Setter")
        self.assertEqual(next.get_name(), "setter_attr2",
            "next.get_value() != 'setter_attr2'")
        self.assertEqual(next.get_value(), "setter_value2",
            "next.get_value() != 'setter_value2'")
        self.failUnlessRaises(StopIteration, setters.next)


if (__name__ == "__main__"):
    unittest.main()

