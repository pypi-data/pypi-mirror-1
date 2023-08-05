import unittest

import aglyph.context
import aglyph.definition

import tests


class XmlContextTest(tests.ValueTest):

    def setUp(self):
        self.context = aglyph.context.XmlContext()
        self.context.load(tests.CONTEXT_XML)

    def test_bools(self):
        init_args = \
            [arg.get_value() for arg in self.context["bools"].iter_init_args()]
        self.assertEqual(len(init_args), 3,
            "bools received %d arguments" % len(init_args))
        (arg0, arg1, arg2) = init_args
        self._verify_bools(arg0, arg1, arg2)

    def test_complexes(self):
        init_args = \
            [arg.get_value()
                for arg in self.context["complexes"].iter_init_args()]
        self.assertEqual(len(init_args), 13,
            "complexes received %d arguments" % len(init_args))
        (arg0, arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, arg9, arg10,
            arg11, arg12) = init_args
        self._verify_complexes(arg0, arg1, arg2, arg3, arg4, arg5, arg6, arg7,
            arg8, arg9, arg10, arg11, arg12)

    def test_dicts(self):
        init_args = \
            [arg.get_value() for arg in self.context["dicts"].iter_init_args()]
        self.assertEqual(len(init_args), 4,
            "dicts received %d arguments" % len(init_args))
        for (i, arg) in enumerate(init_args[:3]):
            self.assert_(isinstance(arg, aglyph.definition.Evaluator),
                "dicts arg%d is not an aglyph.definition.Evaluator" % i)
        arg0 = init_args[0].evaluate()
        arg1 = init_args[1].evaluate()
        arg2 = init_args[2].evaluate()
        arg3 = init_args[3]
        self._verify_dicts(arg0, arg1, arg2, arg3)

    def test_enumerates(self):
        init_args = \
            [arg.get_value()
                for arg in self.context["enumerates"].iter_init_args()]
        self.assertEqual(len(init_args), 4,
            "enumerates received %d arguments" % len(init_args))
        for (i, arg) in enumerate(init_args[:3]):
            self.assert_(isinstance(arg, aglyph.definition.Evaluator),
                "enumerates arg%d is not an aglyph.definition.Evaluator" % i)
        arg0 = init_args[0].evaluate()
        arg1 = init_args[1].evaluate()
        arg2 = init_args[2].evaluate()
        arg3 = init_args[3]
        self._verify_enumerates(arg0, arg1, arg2, arg3)

    def test_files(self):
        init_args = \
            [arg.get_value() for arg in self.context["files"].iter_init_args()]
        self.assertEqual(len(init_args), 2,
            "files received %d arguments" % len(init_args))
        self.assert_(isinstance(init_args[1], aglyph.definition.Evaluator),
            "files arg1 is not an aglyph.definition.Evaluator")
        arg0 = init_args[0]
        arg1 = init_args[1].evaluate()
        self._verify_files(arg0, arg1)

    def test_floats(self):
        init_args = \
            [arg.get_value()
                for arg in self.context["floats"].iter_init_args()]
        self.assertEqual(len(init_args), 5,
            "floats received %d arguments" % len(init_args))
        (arg0, arg1, arg2, arg3, arg4) = init_args
        self._verify_floats(arg0, arg1, arg2, arg3, arg4)

    def test_frozensets(self):
        init_args = \
            [arg.get_value()
                for arg in self.context["frozensets"].iter_init_args()]
        self.assertEqual(len(init_args), 4,
            "frozensets received %d arguments" % len(init_args))
        for (i, arg) in enumerate(init_args[:3]):
            self.assert_(isinstance(arg, aglyph.definition.Evaluator),
                "frozensets arg%d is not an aglyph.definition.Evaluator" % i)
        arg0 = init_args[0].evaluate()
        arg1 = init_args[1].evaluate()
        arg2 = init_args[2].evaluate()
        arg3 = init_args[3]
        self._verify_frozensets(arg0, arg1, arg2, arg3)

    def test_ints(self):
        init_args = \
            [arg.get_value() for arg in self.context["ints"].iter_init_args()]
        self.assertEqual(len(init_args), 8,
            "ints received %d arguments" % len(init_args))
        (arg0, arg1, arg2, arg3, arg4, arg5, arg6, arg7) = init_args
        self._verify_ints(arg0, arg1, arg2, arg3, arg4, arg5, arg6, arg7)

    def test_iters(self):
        init_args = \
            [arg.get_value() for arg in self.context["iters"].iter_init_args()]
        self.assertEqual(len(init_args), 4,
            "iters received %d arguments" % len(init_args))
        for (i, arg) in enumerate(init_args[:3]):
            self.assert_(isinstance(arg, aglyph.definition.Evaluator),
                "iters arg%d is not an aglyph.definition.Evaluator" % i)
        arg0 = init_args[0].evaluate()
        arg1 = init_args[1].evaluate()
        arg2 = init_args[2].evaluate()
        arg3 = init_args[3]
        self._verify_iters(arg0, arg1, arg2, arg3)

    def test_lists(self):
        init_args = \
            [arg.get_value() for arg in self.context["lists"].iter_init_args()]
        self.assertEqual(len(init_args), 4,
            "lists received %d arguments" % len(init_args))
        for (i, arg) in enumerate(init_args[:3]):
            self.assert_(isinstance(arg, aglyph.definition.Evaluator),
                "lists arg%d is not an aglyph.definition.Evaluator" % i)
        arg0 = init_args[0].evaluate()
        arg1 = init_args[1].evaluate()
        arg2 = init_args[2].evaluate()
        arg3 = init_args[3]
        self._verify_lists(arg0, arg1, arg2, arg3)

    def test_longs(self):
        init_args = \
            [arg.get_value() for arg in self.context["longs"].iter_init_args()]
        self.assertEqual(len(init_args), 8,
            "longs received %d arguments" % len(init_args))
        (arg0, arg1, arg2, arg3, arg4, arg5, arg6, arg7) = init_args
        self._verify_longs(arg0, arg1, arg2, arg3, arg4, arg5, arg6, arg7)

    def test_sets(self):
        init_args = \
            [arg.get_value() for arg in self.context["sets"].iter_init_args()]
        self.assertEqual(len(init_args), 4,
            "sets received %d arguments" % len(init_args))
        for (i, arg) in enumerate(init_args[:3]):
            self.assert_(isinstance(arg, aglyph.definition.Evaluator),
                "sets arg%d is not an aglyph.definition.Evaluator" % i)
        arg0 = init_args[0].evaluate()
        arg1 = init_args[1].evaluate()
        arg2 = init_args[2].evaluate()
        arg3 = init_args[3]
        self._verify_sets(arg0, arg1, arg2, arg3)

    def test_slices(self):
        init_args = \
            [arg.get_value()
                for arg in self.context["slices"].iter_init_args()]
        self.assertEqual(len(init_args), 3,
            "slices received %d arguments" % len(init_args))
        (arg0, arg1, arg2) = init_args
        self._verify_slices(arg0, arg1, arg2)

    def test_strs(self):
        init_args = \
            [arg.get_value() for arg in self.context["strs"].iter_init_args()]
        self.assertEqual(len(init_args), 3,
            "strs received %d arguments" % len(init_args))
        (arg0, arg1, arg2) = init_args
        self._verify_strs(arg0, arg1, arg2)

    def test_tuples(self):
        init_args = \
            [arg.get_value()
                for arg in self.context["tuples"].iter_init_args()]
        self.assertEqual(len(init_args), 4,
            "tuples received %d arguments" % len(init_args))
        for (i, arg) in enumerate(init_args[:3]):
            self.assert_(isinstance(arg, aglyph.definition.Evaluator),
                "tuples arg%d is not an aglyph.definition.Evaluator" % i)
        arg0 = init_args[0].evaluate()
        arg1 = init_args[1].evaluate()
        arg2 = init_args[2].evaluate()
        arg3 = init_args[3]
        self._verify_tuples(arg0, arg1, arg2, arg3)

    def test_unicodes(self):
        init_args = \
            [arg.get_value()
                for arg in self.context["unicodes"].iter_init_args()]
        self.assertEqual(len(init_args), 3,
            "unicodes received %d arguments" % len(init_args))
        (arg0, arg1, arg2) = init_args
        self._verify_unicodes(arg0, arg1, arg2)

    def test_xranges(self):
        init_args = \
            [arg.get_value()
                for arg in self.context["xranges"].iter_init_args()]
        self.assertEqual(len(init_args), 3,
            "xranges received %d arguments" % len(init_args))
        (arg0, arg1, arg2) = init_args
        self._verify_xranges(arg0, arg1, arg2)

    def test_builtin_constants(self):
        init_args = \
            [arg.get_value()
                for arg in self.context["builtin_constants"].iter_init_args()]
        self.assertEqual(len(init_args), 5,
            "builtin_constants received %d arguments" % len(init_args))
        (arg0, arg1, arg2, arg3, arg4) = init_args
        self._verify_builtin_constants(arg0, arg1, arg2, arg3, arg4)

    def test_references(self):
        init_args = \
            [arg.get_value()
                for arg in self.context["references"].iter_init_args()]
        self.assertEqual(len(init_args), 18,
            "references received %d arguments" % len(init_args))
        for (i, arg) in enumerate(init_args):
            self.assert_(isinstance(arg, aglyph.definition.Reference),
                "references arg%d is not an aglyph.definition.Reference" % i)

    def test_foof(self):
        self.assert_("foofThing" in self.context,
            "context does not define 'foofThing'")
        definition = self.context["foofThing"]
        init_args = [arg.get_value() for arg in definition.iter_init_args()]
        self.assertEqual(len(init_args), 1,
            "foofThing received %d arguments" % len(init_args))
        arg0 = init_args[0]
        self.assert_(isinstance(arg0, aglyph.definition.Reference),
            "foofThing arg0 is not an aglyph.definition.Reference")
        self.assertEqual(str(arg0), "references",
            "str(arg0) != 'references'")
        init_kwargs = [(kwarg.get_name(), kwarg.get_value())
                        for kwarg in definition.iter_init_kwargs()]
        self.assertEqual(len(init_kwargs), 1,
            "foofThing received %d keyword arguments" % len(init_kwargs))
        kwarg0 = init_kwargs[0]
        self.assertEqual(kwarg0[0], "constants", "kwarg0[0] != 'constants'")
        self.assert_(isinstance(kwarg0[1], aglyph.definition.Reference),
            "foofThing kwarg0[1] is not an aglyph.definition.Reference")
        self.assertEqual(str(kwarg0[1]), "builtin_constants",
            "str(kwarg0[1]) != 'builtin_constants'")
        setters = [(setter.get_name(), setter.get_value())
                    for setter in definition.iter_setters()]
        self.assertEqual(len(setters), 3,
            "foofThing received %d setters" % len(setters))
        (setter0, setter1, setter2) = setters
        self.assertEqual(setter0[0], "spam", "setter0[0] != 'spam'")
        self.assert_(isinstance(setter0[1], aglyph.definition.Reference),
            "foofThing setter0[1] is not an aglyph.definition.Reference")
        self.assertEqual(str(setter0[1]), "spamThing",
            "str(setter0[1]) != 'spamThing'")
        self.assertEqual(setter1[0], "set_eggs", "setter1[0] != 'set_eggs'")
        self.assert_(isinstance(setter1[1], aglyph.definition.Reference),
            "foofThing setter1[1] is not an aglyph.definition.Reference")
        self.assertEqual(str(setter1[1]), "eggsThing",
            "str(setter1[1]) != 'eggsThing'")
        self.assertEqual(setter2[0], "crap", "setter2[0] != 'crap'")
        self.assert_(isinstance(setter2[1], aglyph.definition.Reference),
            "foofThing setter2[1] is not an aglyph.definition.Reference")
        self.assertEqual(str(setter2[1]), "tests.CrapThing",
            "str(setter2[1]) != 'tests.CrapThing'")

    def test_spam(self):
        self.assert_("spamThing" in self.context,
            "context does not define 'spamThing'")
        definition = self.context["spamThing"]
        init_args = [arg.get_value() for arg in definition.iter_init_args()]
        self.assertEqual(len(init_args), 1,
            "spamThing received %d arguments" % len(init_args))
        arg0 = init_args[0]
        self.assert_(isinstance(arg0, aglyph.definition.Evaluator),
            "spamThing arg0 is not an aglyph.definition.Evaluator")
        arg0 = arg0.evaluate()
        self.assert_(isinstance(arg0, tuple), "spamThing arg0 is not a tuple")
        init_kwargs = [(kwarg.get_name(), kwarg.get_value())
                        for kwarg in definition.iter_init_kwargs()]
        self.assertEqual(len(init_kwargs), 0,
            "spamThing received %d keyword arguments" % len(init_kwargs))
        setters = [(setter.get_name(), setter.get_value())
                    for setter in definition.iter_setters()]
        self.assertEqual(len(setters), 0,
            "spamThing received %d setters" % len(setters))

    def test_eggs(self):
        self.assert_("eggsThing" in self.context,
            "context does not define 'eggsThing'")
        definition = self.context["eggsThing"]
        init_args = [arg.get_value() for arg in definition.iter_init_args()]
        self.assertEqual(len(init_args), 0,
            "eggsThing received %d arguments" % len(init_args))
        init_kwargs = [(kwarg.get_name(), kwarg.get_value())
                        for kwarg in definition.iter_init_kwargs()]
        self.assertEqual(len(init_kwargs), 0,
            "eggsThing received %d keyword arguments" % len(init_kwargs))
        setters = [(setter.get_name(), setter.get_value())
                    for setter in definition.iter_setters()]
        self.assertEqual(len(setters), 1,
            "eggsThing received %d setters" % len(setters))
        setter0 = setters[0]
        self.assertEqual(setter0[0], "numeric",
            "eggsThing setter0[0] != 'numeric'")
        self.assert_(isinstance(setter0[1], frozenset),
            "eggsThing setter0[1] is not a frozenset")

    def test_crap(self):
        self.assert_("tests.CrapThing" in self.context,
            "context does not define 'tests.CrapThing'")
        definition = self.context["tests.CrapThing"]
        init_args = [arg.get_value() for arg in definition.iter_init_args()]
        self.assertEqual(len(init_args), 0,
            "tests.CrapThing received %d arguments"
                % len(init_args))
        init_kwargs = [(kwarg.get_name(), kwarg.get_value())
                        for kwarg in definition.iter_init_kwargs()]
        self.assertEqual(len(init_kwargs), 0,
            "tests.CrapThing received %d keyword arguments"
                % len(init_kwargs))
        setters = [(setter.get_name(), setter.get_value())
                    for setter in definition.iter_setters()]
        self.assertEqual(len(setters), 0,
            "tests.CrapThing received %d setters" % len(setters))

    def test_what(self):
        self.assert_("tests.WhatThing" in self.context,
            "context does not define 'tests.WhatThing'")
        definition = self.context["tests.WhatThing"]
        init_args = [arg.get_value() for arg in definition.iter_init_args()]
        self.assertEqual(len(init_args), 1,
            "tests.WhatThing received %d arguments"
                % len(init_args))
        arg0 = init_args[0]
        self.assert_(isinstance(arg0, aglyph.definition.Reference),
            "tests.WhatThing arg0 is not an aglyph.definition.Reference")
        init_kwargs = [(kwarg.get_name(), kwarg.get_value())
                        for kwarg in definition.iter_init_kwargs()]
        self.assertEqual(len(init_kwargs), 0,
            "tests.WhatThing received %d keyword arguments"
                % len(init_kwargs))
        setters = [(setter.get_name(), setter.get_value())
                    for setter in definition.iter_setters()]
        self.assertEqual(len(setters), 0,
            "tests.WhatThing received %d setters" % len(setters))

    def test_prototypes(self):
        prototypes = ["dicts", "enumerates", "files", "frozensets", "iters",
            "lists", "sets", "tuples", "references", "foofThing", "spamThing",
            "eggsThing", "tests.CrapThing"]
        singletons = ["bools", "complexes", "floats", "ints", "longs",
            "slices", "strs", "unicodes", "xranges", "builtin_constants",
            "tests.WhatThing", "config1", "config2"]
        for component_id in prototypes:
            self.assertEqual(
                self.context[component_id].get_creation_strategy(),
                "prototype",
                "%r is not a prototype" % component_id)
        for component_id in singletons:
            self.assertEqual(
                self.context[component_id].get_creation_strategy(),
                "singleton",
                "%r is not a singleton" % component_id)

    def test_common_setters(self):
        common_setters = list(self.context.iter_common_setters())
        self.assertEqual(len(common_setters), 2, "len(common_setters) != 2")
        (setter0, setter1) = common_setters
        self.assert_(isinstance(setter0, aglyph.definition.Setter),
            "setter0 is not an aglyph.definition.Setter")
        self.assertEqual(setter0.get_name(), "config",
            "setter0.get_name() != 'config'")
        self.assert_(
            isinstance(setter0.get_value(), aglyph.definition.Reference),
            "setter0.get_value() is not an aglyph.definition.Reference")
        self.assert_(isinstance(setter1, aglyph.definition.Setter),
            "setter1 is not an aglyph.definition.Setter")
        self.assertEqual(setter1.get_name(), "version",
            "setter1.get_name() != 'version'")
        self.assert_(isinstance(setter1.get_value(), tuple),
            "setter1.get_value() is not a tuple")


if (__name__ == "__main__"):
    unittest.main()

