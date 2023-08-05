import unittest

import aglyph
import aglyph.assembler
import aglyph.classloader
import tests

class AssemblerTest(tests.ValueTest):

    def setUp(self):
        # Force reload of assembler for each test.  This is necessary because
        # test_assemble_values() and test_assemble_references() both verify the
        # same 'enumerates' and 'iters' instances, which respectively contain
        # both lazy and eager evaluated versions.  If the assembler is NOT
        # reloaded, then the eagerly-evaluated versions would always raise
        # StopIteration the second time they were verified.
        self.assembler = aglyph.get_assembler(tests.ASSEMBLER_INI, True)

    def test_get_assembler(self):
        self.assertEqual(
            self.assembler,
            aglyph.get_assembler(tests.ASSEMBLER_INI),
            "aglyph.get_assembler(...) did not return a cached instance")
        self.assertNotEqual(
            self.assembler,
            aglyph.get_assembler(tests.ASSEMBLER_INI, True),
            "aglyph.get_assembler(..., True) did not return a fresh instance")

    def test_assemble_values(self):
        component_ids = ["bools", "complexes", "dicts", "enumerates", "files",
            "floats", "frozensets", "ints", "iters", "lists", "longs", "sets",
            "slices", "strs", "tuples", "unicodes", "xranges",
            "builtin_constants"]
        for component_id in component_ids:
            values = self.assembler.assemble(component_id)
            verify_method = getattr(self, "_verify_%s" % component_id)
            apply(verify_method, values.args)

    def test_assemble_references(self):
        component_ids = ["bools", "complexes", "dicts", "enumerates", "files",
            "floats", "frozensets", "ints", "iters", "lists", "longs", "sets",
            "slices", "strs", "tuples", "unicodes", "xranges",
            "builtin_constants"]
        references = self.assembler.assemble("references")
        for (component_id, component) \
                in zip(component_ids, references.args):
            verify_method = getattr(self, "_verify_%s" % component_id)
            apply(verify_method, component.args)

    def test_prototypes(self):
        component_ids = ["dicts", "enumerates", "files", "frozensets", "iters",
            "lists", "sets", "tuples", "references", "foofThing", "spamThing",
            "eggsThing", "tests.CrapThing"]
        for component_id in component_ids:
            self.assertNotEqual(
                self.assembler.assemble(component_id),
                self.assembler.assemble(component_id),
                "assembler.assemble(%r) returned same instance" % component_id)

    def test_singletons(self):
        component_ids = ["bools", "complexes", "floats", "ints", "longs",
            "slices", "strs", "unicodes", "xranges", "builtin_constants",
            "tests.WhatThing", "config1", "config2"]
        for component_id in component_ids:
            self.assertEqual(
                self.assembler.assemble(component_id),
                self.assembler.assemble(component_id),
                "assembler.assemble(%r) did not return same instance"
                    % component_id)

    def test_create(self):
        component_ids = ["bools", "complexes", "dicts", "enumerates", "files",
            "floats", "frozensets", "ints", "iters", "lists", "longs", "sets",
            "slices", "strs", "tuples", "unicodes", "xranges",
            "builtin_constants", "references", "foofThing", "spamThing",
            "eggsThing", "tests.CrapThing",
            "tests.WhatThing", "config1", "config2"]
        for component_id in component_ids:
            instance1 = self.assembler.create(component_id)
            instance2 = self.assembler.create(component_id)
            self.assertNotEqual(id(instance1), id(instance2),
                "assembler.create(%r) returned same instance" % component_id)

    def test_iter_by_strategy(self):
        expected_prototypes = sorted(["dicts", "enumerates", "files",
            "frozensets", "iters", "lists", "sets", "tuples", "foofThing",
            "spamThing", "eggsThing", "tests.CrapThing"])
        assembler_prototypes = \
            sorted(self.assembler.iter_by_strategy("prototype"))
        expected_singletons = sorted(["bools", "complexes", "floats", "ints",
            "longs", "slices", "strs", "unicodes", "xranges",
            "builtin_constants", "tests.WhatThing", "config1",
            "config2"])
        assembler_singletons = \
            sorted(self.assembler.iter_by_strategy("singleton"))
        non_prototypes = set(expected_prototypes) - set(assembler_prototypes)
        non_singletons = set(expected_singletons) - set(assembler_singletons)
        self.assertEqual(non_prototypes, set(),
            "expected prototypes %s" % ", ".join(list(non_prototypes)))
        self.assertEqual(non_singletons, set(),
            "expected singletons %s" % ", ".join(list(non_singletons)))

    def test___contains__(self):
        component_ids = ["bools", "complexes", "dicts", "enumerates", "files",
            "floats", "frozensets", "ints", "iters", "lists", "longs", "sets",
            "slices", "strs", "tuples", "unicodes", "xranges",
            "builtin_constants", "references", "foofThing", "spamThing",
            "eggsThing", "tests.CrapThing",
            "tests.WhatThing", "config1", "config2"]
        for component_id in component_ids:
            self.assert_(component_id in self.assembler,
                "assembler does not contain component ID %r" % component_id)

    def test___iter__(self):
        component_ids = sorted(["bools", "complexes", "dicts", "enumerates",
            "files", "floats", "frozensets", "ints", "iters", "lists", "longs",
            "sets", "slices", "strs", "tuples", "unicodes", "xranges",
            "builtin_constants", "references", "foofThing", "spamThing",
            "eggsThing", "tests.CrapThing",
            "tests.WhatThing", "config1", "config2"])
        # Guarantee the order of the assembler iterator for accurate testing.
        cid_iter = iter(sorted(self.assembler))
        for component_id in component_ids:
            self.assertEqual(component_id, cid_iter.next(),
                "iter(assembler).next() != %r" % component_id)
        self.failUnlessRaises(StopIteration, cid_iter.next)


if (__name__ == "__main__"):
    unittest.main()

