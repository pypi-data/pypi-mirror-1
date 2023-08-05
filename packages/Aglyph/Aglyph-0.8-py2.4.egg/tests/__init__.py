import os
import unittest

import aglyph.classloader
import aglyph.context
import aglyph.definition

# Determine file paths to test artifacts.
_TEST_PACKAGE = aglyph.classloader.ClassLoader().find_resource("tests")
ASSEMBLER_INI = os.path.join(_TEST_PACKAGE, "assembler.ini")
CONFIG_INI = os.path.join(_TEST_PACKAGE, "config.ini")
CONTEXT_XML = os.path.join(_TEST_PACKAGE, "context.xml")
TEST_TXT = os.path.join(_TEST_PACKAGE, "test.txt")
# The "context.xml" file needs to be recreated so that the paths referenced
# within it are always correct.
_CONTEXT_XML_fp = file(CONTEXT_XML, 'w')
_CONTEXT_XML_fp.write(
"""<?xml version="1.0"?>
<!DOCTYPE context
    PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.sourceforge.net/projects/aglyph/dtd/context-0.8.dtd">
<context id="aglyph-unittest" version="0.8">
    <description>
        This context defines components that are used by Aglyph unit tests.
    </description>
    <common>
        <setter attribute="config"><reference component="config1"/></setter>
        <setter attribute="version">
            <tuple evaluate="eager">
                <int>0</int>
                <int>0</int>
                <int>0</int>
            </tuple>
        </setter>
    </common>
    <component id="bools" classpath="tests.Elements" create="singleton">
        <init>
            <arg><bool/></arg>
            <arg><bool></bool></arg>
            <arg><bool>false</bool></arg> <!-- True! -->
        </init>
    </component>
    <component id="complexes" classpath="tests.Elements"
            create="singleton">
        <init>
            <arg><complex/></arg>
            <arg><complex></complex></arg>
            <arg><complex real="0"/></arg>
            <arg><complex real="0" imag="0"/></arg>
            <arg><complex>0j</complex></arg>
            <arg><complex real="7" imag="9"/></arg>
            <arg><complex>7+9j</complex></arg>
            <arg><complex real="-7" imag="9"/></arg>
            <arg><complex>-7+9j</complex></arg>
            <arg><complex real="7" imag="-9"/></arg>
            <arg><complex>7-9j</complex></arg>
            <arg><complex real="-7" imag="-9"/></arg>
            <arg><complex>-7-9j</complex></arg>
        </init>
    </component>
    <component id="dicts" classpath="tests.Elements">
        <init>
            <arg><dict/></arg>
            <arg><dict></dict></arg>
            <arg>
                <dict>
                    <item>
                        <key><str>foof</str></key>
                        <value><str>spam</str></value>
                    </item>
                    <item>
                        <key><str>eggs</str></key>
                        <value><str>crap</str></value>
                    </item>
                    <item>
                        <key><str>what</str></key>
                        <value><str>what</str></value>
                    </item>
                </dict>
            </arg>
            <arg>
                <dict evaluate="eager">
                    <item>
                        <key><str>foof</str></key>
                        <value><str>spam</str></value>
                    </item>
                    <item>
                        <key><str>eggs</str></key>
                        <value><str>crap</str></value>
                    </item>
                    <item>
                        <key><str>what</str></key>
                        <value><str>what</str></value>
                    </item>
                </dict>
            </arg>
        </init>
    </component>
    <component id="enumerates" classpath="tests.Elements">
        <init>
            <arg><enumerate/></arg>
            <arg><enumerate></enumerate></arg>
            <arg>
                <enumerate>
                    <str>foof</str>
                    <str>spam</str>
                    <str>eggs</str>
                    <str>crap</str>
                    <str>what</str>
                </enumerate>
            </arg>
            <arg>
                <enumerate evaluate="eager">
                    <str>foof</str>
                    <str>spam</str>
                    <str>eggs</str>
                    <str>crap</str>
                    <str>what</str>
                </enumerate>
            </arg>
        </init>
    </component>
    <component id="files" classpath="tests.Elements">
        <init>
            <arg>
                <file filename="%(TEST_TXT)s" mode="w" evaluate="eager"/>
            </arg>
            <arg><file filename="%(TEST_TXT)s" mode="r" bufsize="32"/></arg>
        </init>
    </component>
    <component id="floats" classpath="tests.Elements"
            create="singleton">
        <init>
            <arg><float/></arg>
            <arg><float></float></arg>
            <arg><float>0</float></arg>
            <arg><float>7.9</float></arg>
            <arg><float>-7.9</float></arg>
        </init>
    </component>
    <component id="frozensets" classpath="tests.Elements">
        <init>
            <arg><frozenset/></arg>
            <arg><frozenset></frozenset></arg>
            <arg>
                <frozenset>
                    <str>foof</str>
                    <str>foof</str>
                    <str>spam</str>
                    <str>spam</str>
                    <str>eggs</str>
                    <str>eggs</str>
                    <str>crap</str>
                    <str>crap</str>
                    <str>what</str>
                    <str>what</str>
                </frozenset>
            </arg>
            <arg>
                <frozenset evaluate="eager">
                    <str>foof</str>
                    <str>foof</str>
                    <str>spam</str>
                    <str>spam</str>
                    <str>eggs</str>
                    <str>eggs</str>
                    <str>crap</str>
                    <str>crap</str>
                    <str>what</str>
                    <str>what</str>
                </frozenset>
            </arg>
        </init>
    </component>
    <component id="ints" classpath="tests.Elements" create="singleton">
        <init>
            <arg><int/></arg>
            <arg><int></int></arg>
            <arg><int>0</int></arg>
            <arg><int>79</int></arg>
            <arg><int>-79</int></arg>
            <arg><int radix="2">01001111</int></arg>
            <arg><int radix="8">0117</int></arg>
            <arg><int radix="16">4F</int></arg>
        </init>
    </component>
    <component id="iters" classpath="tests.Elements">
        <init>
            <arg><iter/></arg>
            <arg><iter></iter></arg>
            <arg>
                <iter>
                    <str>foof</str>
                    <str>spam</str>
                    <str>eggs</str>
                    <str>crap</str>
                    <str>what</str>
                </iter>
            </arg>
            <arg>
                <iter evaluate="eager">
                    <str>foof</str>
                    <str>spam</str>
                    <str>eggs</str>
                    <str>crap</str>
                    <str>what</str>
                </iter>
            </arg>
        </init>
    </component>
    <component id="lists" classpath="tests.Elements">
        <init>
            <arg><list/></arg>
            <arg><list></list></arg>
            <arg>
                <list>
                    <str>foof</str>
                    <str>spam</str>
                    <str>eggs</str>
                    <str>crap</str>
                    <str>what</str>
                </list>
            </arg>
            <arg>
                <list evaluate="eager">
                    <str>foof</str>
                    <str>spam</str>
                    <str>eggs</str>
                    <str>crap</str>
                    <str>what</str>
                </list>
            </arg>
        </init>
    </component>
    <component id="longs" classpath="tests.Elements" create="singleton">
        <init>
            <arg><long/></arg>
            <arg><long></long></arg>
            <arg><long>0</long></arg>
            <arg><long>79</long></arg>
            <arg><long>-79</long></arg>
            <arg><long radix="2">01001111</long></arg>
            <arg><long radix="8">0117</long></arg>
            <arg><long radix="16">4F</long></arg>
        </init>
    </component>
    <component id="sets" classpath="tests.Elements">
        <init>
            <arg><set/></arg>
            <arg><set></set></arg>
            <arg>
                <set>
                    <str>foof</str>
                    <str>foof</str>
                    <str>spam</str>
                    <str>spam</str>
                    <str>eggs</str>
                    <str>eggs</str>
                    <str>crap</str>
                    <str>crap</str>
                    <str>what</str>
                    <str>what</str>
                </set>
            </arg>
            <arg>
                <set evaluate="eager">
                    <str>foof</str>
                    <str>foof</str>
                    <str>spam</str>
                    <str>spam</str>
                    <str>eggs</str>
                    <str>eggs</str>
                    <str>crap</str>
                    <str>crap</str>
                    <str>what</str>
                    <str>what</str>
                </set>
            </arg>
        </init>
    </component>
    <component id="slices" classpath="tests.Elements"
            create="singleton">
        <init>
            <arg><slice stop="0"/></arg>
            <arg><slice start="1" stop="10"/></arg>
            <arg><slice start="9" stop="0" step="-2"/></arg>
        </init>
    </component>
    <component id="strs" classpath="tests.Elements" create="singleton">
        <init>
            <arg><str/></arg>
            <arg><str></str></arg>
            <arg><str>The quick brown fox jumps over the lazy dog.</str></arg>
        </init>
    </component>
    <component id="tuples" classpath="tests.Elements">
        <init>
            <arg><tuple/></arg>
            <arg><tuple></tuple></arg>
            <arg>
                <tuple>
                    <str>foof</str>
                    <str>spam</str>
                    <str>eggs</str>
                    <str>crap</str>
                    <str>what</str>
                </tuple>
            </arg>
            <arg>
                <tuple evaluate="eager">
                    <str>foof</str>
                    <str>spam</str>
                    <str>eggs</str>
                    <str>crap</str>
                    <str>what</str>
                </tuple>
            </arg>
        </init>
    </component>
    <component id="unicodes" classpath="tests.Elements"
            create="singleton">
        <init>
            <arg><unicode/></arg>
            <arg><unicode></unicode></arg>
            <arg>
                <unicode>The quick brown fox jumps over the lazy dog.</unicode>
            </arg>
        </init>
    </component>
    <component id="xranges" classpath="tests.Elements"
            create="singleton">
        <init>
            <arg><xrange stop="0"/></arg>
            <arg><xrange start="1" stop="10"/></arg>
            <arg><xrange start="9" stop="0" step="-2"/></arg>
        </init>
    </component>
    <component id="builtin_constants" classpath="tests.Elements"
            create="singleton">
        <init>
            <arg><ellipsis/></arg>
            <arg><false/></arg>
            <arg><none/></arg>
            <arg><notimplemented/></arg>
            <arg><true/></arg>
        </init>
    </component>
    <component id="references" classpath="tests.Elements">
        <init>
            <arg><reference component="bools"/></arg>
            <arg><reference component="complexes"/></arg>
            <arg><reference component="dicts"/></arg>
            <arg><reference component="enumerates"/></arg>
            <arg><reference component="files"/></arg>
            <arg><reference component="floats"/></arg>
            <arg><reference component="frozensets"/></arg>
            <arg><reference component="ints"/></arg>
            <arg><reference component="iters"/></arg>
            <arg><reference component="lists"/></arg>
            <arg><reference component="longs"/></arg>
            <arg><reference component="sets"/></arg>
            <arg><reference component="slices"/></arg>
            <arg><reference component="strs"/></arg>
            <arg><reference component="tuples"/></arg>
            <arg><reference component="unicodes"/></arg>
            <arg><reference component="xranges"/></arg>
            <arg><reference component="builtin_constants"/></arg>
        </init>
    </component>
    <component id="foofThing" classpath="tests.FoofThing">
        <init>
            <arg><reference component="references"/></arg>
            <arg name="constants">
                <reference component="builtin_constants"/>
            </arg>
        </init>
        <setters>
            <setter attribute="spam">
                <reference component="spamThing"/>
            </setter>
            <setter attribute="set_eggs">
                <reference component="eggsThing"/>
            </setter>
            <setter attribute="crap">
                <reference component="tests.CrapThing"/>
            </setter>
        </setters>
    </component>
    <component id="spamThing" classpath="tests.SpamThing">
        <init>
            <arg>
                <tuple>
                    <enumerate>
                        <str>zero</str><str>one</str><str>two</str>
                    </enumerate>
                    <dict>
                        <item>
                            <key>
                                <tuple>
                                    <reference component="config1"/>
                                    <reference component="config2"/>
                                </tuple>
                            </key>
                            <value>
                                <dict>
                                    <item>
                                        <key><str>foof</str></key>
                                        <value><str>spam</str></value>
                                    </item>
                                </dict>
                            </value>
                        </item>
                    </dict>
                    <set evaluate="eager">
                        <false/><true/>
                    </set>
                </tuple>
            </arg>
        </init>
    </component>
    <component id="eggsThing" classpath="tests.EggsThing">
        <setters>
            <setter attribute="numeric">
                <frozenset evaluate="eager">
                    <reference component="ints"/>
                    <reference component="longs"/>
                    <reference component="floats"/>
                    <reference component="complexes"/>
                </frozenset>
            </setter>
        </setters>
    </component>
    <component classpath="tests.CrapThing"/>
    <component classpath="tests.WhatThing" create="singleton">
        <init>
            <arg><reference component="foofThing"/></arg>
        </init>
    </component>
    <component id="config1" classpath="ConfigParser.SafeConfigParser"
            create="singleton">
        <setters>
            <setter attribute="readfp">
                <file filename="%(CONFIG_INI)s"/>
            </setter>
        </setters>
    </component>
    <component id="config2" classpath="__builtin__.dict" create="singleton">
        <init>
            <arg name="foof"><str>spam</str></arg>
            <arg name="eggs"><str>crap</str></arg>
            <arg name="what"><str>what</str></arg>
        </init>
    </component>
</context>
""" % {"CONFIG_INI": CONFIG_INI, "TEST_TXT": TEST_TXT}
    )
_CONTEXT_XML_fp.close()
del _CONTEXT_XML_fp
del _TEST_PACKAGE


class Elements:

    def __init__(self, *args):
        self.args = args


class Thing(object):

    def __init__(self):
        self.__version = None
        self.__config = None

    def set_version(self, value):
        self.__version = value
    version = property(None, set_version)

    def get_config(self):
        return self.__config
    def set_config(self, value):
        self.__config = value
    config = property(get_config, set_config)

    def __str__(self):
        version_string = "%d.%d.%d" % self.__version
        return "%s v%s" % (self.__class__.__name__, version_string)


class FoofThing(Thing):

    def __init__(self, references, constants=None):
        Thing.__init__(self)
        self.references = references
        self.constants = constants
        self.spam = None
        self.__eggs = None
        self.__crap = None

    def get_eggs(self):
        return self.__eggs

    def set_eggs(self, value):
        self.__eggs = value

    def get_crap(self):
        return self.__crap
    def set_crap(self, value):
        self.__crap = value
    crap = property(get_crap, set_crap)


class SpamThing(Thing):

    def __init__(self, tuparg):
        Thing.__init__(self)
        self.tuparg = tuparg


class EggsThing(Thing):

    def __init__(self):
        Thing.__init__(self)
        self.__numeric = None

    def get_numeric(self):
        return self.__numeric
    def set_numeric(self, value):
        self.__numeric = value
    numeric = property(get_numeric, set_numeric)


class CrapThing(EggsThing):

    def __init__(self):
        EggsThing.__init__(self)


class WhatThing(CrapThing):

    def __init__(self, foof):
        CrapThing.__init__(self)
        self.__foof = foof

    def get_foof(self):
        return self.__foof
    foof = property(get_foof)


class ValueTest(unittest.TestCase):

    def __assert_isinstance(self, label, type_, *args):
        for (i, obj) in enumerate(args):
            self.assert_(isinstance(obj, type_),
                "%s arg%d is not a %s" % (label, i, type_.__name__))

    def _verify_bools(self, arg0, arg1, arg2):
        self.__assert_isinstance("bools", bool, *(arg0, arg1, arg2))
        self.assert_(arg0 is False, "bools arg0 is not False")
        self.assert_(arg1 is False, "bools arg1 is not False")
        self.assert_(arg2 is True, "bools arg2 is not True")

    def _verify_complexes(self, arg0, arg1, arg2, arg3, arg4, arg5, arg6, arg7,
            arg8, arg9, arg10, arg11, arg12):
        args = (arg0, arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, arg9,
            arg10, arg11, arg12)
        self.__assert_isinstance("complexes", complex, *args)
        self.assertEqual(arg0, 0j, "complexes arg0 != 0j")
        self.assertEqual(arg1, 0j, "complexes arg1 != 0j")
        self.assertEqual(arg2, 0j, "complexes arg2 != 0j")
        self.assertEqual(arg3, 0j, "complexes arg3 != 0j")
        self.assertEqual(arg4, 0j, "complexes arg4 != 0j")
        self.assertEqual(arg5, 7+9j, "complexes arg5 != 7+9j")
        self.assertEqual(arg6, 7+9j, "complexes arg6 != 7+9j")
        self.assertEqual(arg7, -7+9j, "complexes arg7 != -7+9j")
        self.assertEqual(arg8, -7+9j, "complexes arg8 != -7+9j")
        self.assertEqual(arg9, 7-9j, "complexes arg9 != 7-9j")
        self.assertEqual(arg10, 7-9j, "complexes arg10 != 7-9j")
        self.assertEqual(arg11, -7-9j, "complexes arg11 != -7-9j")
        self.assertEqual(arg12, -7-9j, "complexes arg12 != -7-9j")

    def _verify_dicts(self, arg0, arg1, arg2, arg3):
        self.__assert_isinstance("dicts", dict, *(arg0, arg1, arg2, arg3))
        self.assertEqual(len(arg0), 0,
            "%s arg0 is not empty" % self)
        self.assertEqual(len(arg1), 0, "dicts arg1 is not empty")
        self.assertEqual(len(arg2), 3, "dicts len(arg2) != 3")
        self.assertEqual(arg2.get("foof"), "spam",
            "dicts arg2['foof'] != 'spam'")
        self.assertEqual(arg2.get("eggs"), "crap",
            "dicts arg2['eggs'] != 'crap'")
        self.assertEqual(arg2.get("what"), "what",
            "dicts arg2['what'] != 'what'")
        self.assertEqual(arg2, arg3, "dicts arg2 != arg3")

    def _verify_enumerates(self, arg0, arg1, arg2, arg3):
        self.__assert_isinstance(
            "enumerates", enumerate, *(arg0, arg1, arg2, arg3))
        self.failUnlessRaises(StopIteration, arg0.next)
        self.failUnlessRaises(StopIteration, arg1.next)
        self.assertEqual(arg2.next(), (0, "foof"),
            "enumerates arg2.next() != (0, 'foof')")
        self.assertEqual(arg2.next(), (1, "spam"),
            "enumerates arg2.next() != (1, 'spam')")
        self.assertEqual(arg2.next(), (2, "eggs"),
            "enumerates arg2.next() != (2, 'eggs')")
        self.assertEqual(arg2.next(), (3, "crap"),
            "enumerates arg2.next() != (3, 'crap')")
        self.assertEqual(arg2.next(), (4, "what"),
            "enumerates arg2.next() != (4, 'what')")
        self.failUnlessRaises(StopIteration, arg2.next)
        self.assertEqual(arg3.next(), (0, "foof"),
            "enumerates arg3.next() != (0, 'foof')")
        self.assertEqual(arg3.next(), (1, "spam"),
            "enumerates arg3.next() != (1, 'spam')")
        self.assertEqual(arg3.next(), (2, "eggs"),
            "enumerates arg3.next() != (2, 'eggs')")
        self.assertEqual(arg3.next(), (3, "crap"),
            "enumerates arg3.next() != (3, 'crap')")
        self.assertEqual(arg3.next(), (4, "what"),
            "enumerates arg3.next() != (4, 'what')")
        self.failUnlessRaises(StopIteration, arg3.next)

    def _verify_files(self, arg0, arg1):
        self.__assert_isinstance("files", file, *(arg0, arg1))
        self.assertEqual(
            arg0.name, TEST_TXT, "files arg0.name != %r" % TEST_TXT)
        self.assertEqual(arg0.mode, 'w', "files arg0.mode != 'w'")
        arg0.write("foof,spam,eggs,crap,what")
        arg0.close()
        arg0 = None; del arg0
        self.assertEqual(
            arg1.name, TEST_TXT, "files arg1.name != %r" % TEST_TXT)
        self.assertEqual(arg1.mode, 'r', "files arg1.mode != 'r'")
        self.assertEqual(arg1.read(), "foof,spam,eggs,crap,what",
            "files arg1.read() != 'foof,spam,eggs,crap,what'")

    def _verify_floats(self, arg0, arg1, arg2, arg3, arg4):
        self.__assert_isinstance(
            "floats", float, *(arg0, arg1, arg2, arg3, arg4))
        self.assertEqual(arg0, 0.0, "floats arg0 != 0.0")
        self.assertEqual(arg1, 0.0, "floats arg1 != 0.0")
        self.assertEqual(arg2, 0.0, "floats arg2 != 0.0")
        self.assertAlmostEqual(arg3, 7.9, 1, "floats arg3 != 7.9")
        self.assertAlmostEqual(arg4, -7.9, 1, "floats arg4 != -7.9")

    def _verify_frozensets(self, arg0, arg1, arg2, arg3):
        self.__assert_isinstance(
            "frozensets", frozenset, *(arg0, arg1, arg2, arg3))
        self.assertEqual(len(arg0), 0, "frozensets arg0 is not empty")
        self.assertEqual(len(arg1), 0, "frozensets arg1 is not empty")
        self.assertEqual(len(arg2), 5, "frozensets len(arg2) != 5")
        self.assert_("foof" in arg2, "'foof' not in arg2")
        self.assert_("spam" in arg2, "'spam' not in arg2")
        self.assert_("eggs" in arg2, "'eggs' not in arg2")
        self.assert_("crap" in arg2, "'crap' not in arg2")
        self.assert_("what" in arg2, "'what' not in arg2")
        self.assertEqual(arg2 - arg3, frozenset([]),
            "frozensets arg2 - arg3 is not an empty set")

    def _verify_ints(self, arg0, arg1, arg2, arg3, arg4, arg5, arg6, arg7):
        self.__assert_isinstance(
            "ints", int, *(arg0, arg1, arg2, arg3, arg4, arg5, arg6, arg7))
        self.assertEqual(arg0, 0, "ints arg0 != 0")
        self.assertEqual(arg1, 0, "ints arg1 != 0")
        self.assertEqual(arg2, 0, "ints arg2 != 0")
        self.assertEqual(arg3, 79, "ints arg3 != 79")
        self.assertEqual(arg4, -79, "ints arg4 != -79")
        self.assertEqual(arg5, 79, "ints arg5 != 79")
        self.assertEqual(arg6, 79, "ints arg6 != 79")
        self.assertEqual(arg7, 79, "ints arg7 != 79")

    def _verify_iters(self, arg0, arg1, arg2, arg3):
        for (i, arg) in enumerate([arg0, arg1, arg2, arg3]):
            self.assert_(type(arg) is type(iter([])),
                "iters arg%d is not an iterator" % i)
        self.failUnlessRaises(StopIteration, arg0.next)
        self.failUnlessRaises(StopIteration, arg1.next)
        self.assertEqual(arg2.next(), "foof", "iters arg2.next() != 'foof'")
        self.assertEqual(arg2.next(), "spam", "iters arg2.next() != 'spam'")
        self.assertEqual(arg2.next(), "eggs", "iters arg2.next() != 'eggs'")
        self.assertEqual(arg2.next(), "crap", "iters arg2.next() != 'crap'")
        self.assertEqual(arg2.next(), "what", "iters arg2.next() != 'what'")
        self.failUnlessRaises(StopIteration, arg2.next)
        self.assertEqual(arg3.next(), "foof", "iters arg3.next() != 'foof'")
        self.assertEqual(arg3.next(), "spam", "iters arg3.next() != 'spam'")
        self.assertEqual(arg3.next(), "eggs", "iters arg3.next() != 'eggs'")
        self.assertEqual(arg3.next(), "crap", "iters arg3.next() != 'crap'")
        self.assertEqual(arg3.next(), "what", "iters arg3.next() != 'what'")
        self.failUnlessRaises(StopIteration, arg3.next)

    def _verify_lists(self, arg0, arg1, arg2, arg3):
        self.__assert_isinstance("lists", list, *(arg0, arg1, arg2, arg3))
        self.assertEqual(len(arg0), 0, "lists arg0 is not empty")
        self.assertEqual(len(arg1), 0, "lists arg1 is not empty")
        self.assertEqual(len(arg2), 5, "lists len(arg2) != 5")
        self.assertEqual(arg2[0], "foof", "lists arg2[0] != 'foof'")
        self.assertEqual(arg2[1], "spam", "lists arg2[1] != 'spam'")
        self.assertEqual(arg2[2], "eggs", "lists arg2[2] != 'eggs'")
        self.assertEqual(arg2[3], "crap", "lists arg2[3] != 'crap'")
        self.assertEqual(arg2[4], "what", "lists arg2[4] != 'what'")
        self.assertEqual(arg2, arg3, "lists arg2 != arg3")

    def _verify_longs(self, arg0, arg1, arg2, arg3, arg4, arg5, arg6, arg7):
        self.__assert_isinstance(
            "longs", long, *(arg0, arg1, arg2, arg3, arg4, arg5, arg6, arg7))
        self.assertEqual(arg0, 0L, "longs arg0 != 0L")
        self.assertEqual(arg1, 0L, "longs arg1 != 0L")
        self.assertEqual(arg2, 0L, "longs arg2 != 0L")
        self.assertEqual(arg3, 79L, "longs arg3 != 79L")
        self.assertEqual(arg4, -79L, "longs arg4 != -79L")
        self.assertEqual(arg5, 79L, "longs arg5 != 79L")
        self.assertEqual(arg6, 79L, "longs arg6 != 79L")
        self.assertEqual(arg7, 79L, "longs arg7 != 79L")

    def _verify_sets(self, arg0, arg1, arg2, arg3):
        self.__assert_isinstance("sets", set, *(arg0, arg1, arg2, arg3))
        self.assertEqual(len(arg0), 0, "sets arg0 is not empty")
        self.assertEqual(len(arg1), 0, "sets arg1 is not empty")
        self.assertEqual(len(arg2), 5, "sets len(arg2) != 5")
        self.assert_("foof" in arg2, "'foof' not in arg2")
        self.assert_("spam" in arg2, "'spam' not in arg2")
        self.assert_("eggs" in arg2, "'eggs' not in arg2")
        self.assert_("crap" in arg2, "'crap' not in arg2")
        self.assert_("what" in arg2, "'what' not in arg2")
        self.assertEqual(arg2 - arg3, set([]),
            "sets arg2 - arg3 is not an empty set")

    def _verify_slices(self, arg0, arg1, arg2):
        self.__assert_isinstance("slices", slice, *(arg0, arg1, arg2))
        self.assert_(arg0.start is None, "slices arg0.start is not None")
        self.assertEqual(arg0.stop, 0, "slices arg0.stop != 0")
        self.assert_(arg0.step is None, "slices arg0.step is not None")
        self.assertEqual(arg1.start, 1, "slices arg1.start != 1")
        self.assertEqual(arg1.stop, 10, "slices arg1.stop != 10")
        self.assert_(arg1.step is None, "slices arg1.step is not None")
        self.assertEqual(arg2.start, 9, "slices arg2.start != 9")
        self.assertEqual(arg2.stop, 0, "slices arg2.stop != 0")
        self.assertEqual(arg2.step, -2, "slices arg2.step != -2")

    def _verify_strs(self, arg0, arg1, arg2):
        self.__assert_isinstance("strs", str, *(arg0, arg1, arg2))
        self.assertEqual(arg0, '', "strs arg0 != ''")
        self.assertEqual(arg1, '', "strs arg1 != ''")
        self.assertEqual(arg2, "The quick brown fox jumps over the lazy dog.",
            "strs arg2 != 'The quick brown fox jumps over the lazy dog.'")

    def _verify_tuples(self, arg0, arg1, arg2, arg3):
        self.__assert_isinstance("tuples", tuple, *(arg0, arg1, arg2, arg3))
        self.assertEqual(len(arg0), 0, "tuples arg0 is not empty")
        self.assertEqual(len(arg1), 0, "tuples arg1 is not empty")
        self.assertEqual(len(arg2), 5, "tuples len(arg2) != 5")
        self.assertEqual(arg2[0], "foof", "tuples arg2[0] != 'foof'")
        self.assertEqual(arg2[1], "spam", "tuples arg2[1] != 'spam'")
        self.assertEqual(arg2[2], "eggs", "tuples arg2[2] != 'eggs'")
        self.assertEqual(arg2[3], "crap", "tuples arg2[3] != 'crap'")
        self.assertEqual(arg2[4], "what", "tuples arg2[4] != 'what'")
        self.assertEqual(arg2, arg3, "tuples arg2 != arg3")

    def _verify_unicodes(self, arg0, arg1, arg2):
        self.__assert_isinstance("unicodes", unicode, *(arg0, arg1, arg2))
        self.assertEqual(arg0, u'', "strs arg0 != u''")
        self.assertEqual(arg1, u'', "strs arg1 != u''")
        self.assertEqual(arg2, u"The quick brown fox jumps over the lazy dog.",
            "unicodes arg2 != u'The quick brown fox jumps over the lazy dog.'")

    def _verify_xranges(self, arg0, arg1, arg2):
        self.__assert_isinstance("xranges", xrange, *(arg0, arg1, arg2))
        self.assertEqual(list(arg0), [], "xranges arg0 is not an empty xrange")
        self.assertEqual(list(arg1), list(xrange(1, 10)),
            "xranges arg1 != xrange(1, 10)")
        self.assertEqual(list(arg2), list(xrange(9, 0, -2)),
            "xranges arg2 != xrange(9, 0, -2)")

    def _verify_builtin_constants(self, arg0, arg1, arg2, arg3, arg4):
        self.assert_(arg0 is Ellipsis,
            "builtin_constants arg0 is not Ellipsis")
        self.assert_(arg1 is False, "builtin_constants arg1 is not False")
        self.assert_(arg2 is None, "builtin_constants arg2 is not None")
        self.assert_(arg3 is NotImplemented,
            "builtin_constants arg3 is not NotImplemented")
        self.assert_(arg4 is True, "builtin_constants arg4 is not True")

