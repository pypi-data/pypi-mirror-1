"""Classes for building Aglyph component contexts."""

import ConfigParser
import logging
import UserDict
import xml.dom.minidom

import aglyph.definition


class Context(UserDict.DictMixin):

    """Base class for all Aglyph contexts.

    A Context is basically a dictionary that supports an additional method:
    get_creation_strategy(component_id) -- get the creation strategy for the
                                           named component

    """

    logger = logging.getLogger("aglyph")

    def __init__(self, id_=None, description=''):
        """Create a new, empty context.

        Arguments:
        id_ -- a value that uniquely identifies this context (default None)
        description -- a textual description of this context (default '')

        """
        self.__map = {}
        self._id = id_
        self._description = description
        self.__common_setters = []

    def get_id(self):
        """Return this context's unique identifier."""
        return self._id

    def get_description(self):
        """Return the textual description of this context."""
        return self._description

    def get_creation_strategy(self, component_id):
        """Return the creation strategy for the named component.

        Arguments:
        component_id -- a value that uniquely identifies a component in this
                        context

        """
        return self.__map[component_id].get_creation_strategy()

    def add_common_setter(self, value):
        """Add a value that can be injected into any component.

        Arguments:
        value -- an aglyph.definition.Setter instance

        """
        self.__common_setters.append(value)

    def iter_common_setters(self):
        """Return an iterator over this context's common setters."""
        return iter(self.__common_setters)

    def keys(self):
        """Return a list of the component IDs in this context."""
        return self.__map.keys()

    def __getitem__(self, component_id):
        """Return the definition of the named component."""
        return self.__map[component_id]

    def __setitem__(self, component_id, definition):
        """Assign the definition of the named component."""
        self.__map[component_id] = definition

    def __delitem__(self, component_id):
        """Remove the named component and its definition from this context."""
        del self.__map[component_id]

    def __str__(self):
        return self._description


class XmlContext(Context):

    """A Context that is configurable via an XML configuration file.

    To configure this context, call its load method with a filename or an
    object supporting read().

    """

    def __init__(self):
        """Create a new, empty XML context.

        The id and description will be (optionally) set from parsed values.

        """
        Context.__init__(self)
        self._version = None

    def get_version(self):
        return self._version

    def load(self, fp):
        """Configure this context from the passed-in source.

        Arguments:
        fp -- a filename or file-like object containing XML settings.

        The results of this operation are undefined if the document does
        not conform to the Aglyph Context DTD.

        """
        document = xml.dom.minidom.parse(fp)
        document.normalize()
        context = document.documentElement
        self._extract_context_info(context)
        common = context.getElementsByTagName("common")
        if (common):
            for value in self._parse_common_setters(common[0]):
                self.add_common_setter(value)
        for component in context.getElementsByTagName("component"):
            classpath = component.getAttribute("classpath").encode("us-ascii")
            component_id = component.getAttribute("id").encode("us-ascii") \
                or classpath
            if (component_id in self):
                mesg = "duplicate component %r" % component_id
                self.logger.error(mesg)
                raise ValueError(mesg)
            creation = component.getAttribute("create").encode("us-ascii") \
                or "prototype"
            definition = aglyph.definition.Definition(
                component_id, classpath, creation)
            for value in self._iter_component_values(component):
                definition.add(value)
            self[component_id] = definition

    def _evaluate(self, element):
        """Convert an element type description to a useable value.

        This method will return one of the following types:
        * a Python builtin instance (e.g. an int, a str)
        * a Python bultin constant (e.g. True, False, None)
        * an aglyph.definition.Reference instance
        * an aglyph.definition.Evaluator instance

        The following types support lazy/eager evaluation (default lazy):
        * list
        * tuple
        * set
        * frozenset
        * dict

        Lazy evaluation can be overridden by setting the 'evaluate="eager"'
        attribute on the appropriate element.

        """
        methodname = "_evaluate_%s" % element.nodeName
        if (hasattr(self, methodname)):
            method = getattr(self, methodname)
            return method(element)
        else:
            self.logger.error("don't know how to evaluate <%s>",
                element.nodeName.encode("us-ascii"))
            raise AttributeError(methodname)

    def _evaluate_bool(self, element):
        """Convert a <bool> element to a Python boolean value.

        This method is provided for consistency; using the <true/> or 
        <false/> tags is usually preferred.

        """
        if ((element.firstChild is not None)
                and (element.firstChild.nodeType == xml.dom.Node.TEXT_NODE)):
            return bool(element.firstChild.nodeValue)
        else:
            return bool()

    def _evaluate_complex(self, element):
        """Convert a <complex> element to a Python complex value."""
        if ((element.firstChild is not None)
                and (element.firstChild.nodeType == xml.dom.Node.TEXT_NODE)
                and (element.firstChild.nodeValue)):
            if (element.hasAttribute("real") or element.hasAttribute("imag")):
                mesg = "<complex> element's text value and real/imag" \
                    " attributes are mutually exclusive"
                self.logger.error(mesg)
                raise ValueError(mesg)
            return complex(element.firstChild.nodeValue)
        elif (element.hasAttribute("real") and element.hasAttribute("imag")):
            real = float(element.getAttribute("real"))
            imag = float(element.getAttribute("imag"))
            return complex(real, imag)
        elif (element.hasAttribute("real")):
            real = element.getAttribute("real")
            return complex(real)
        elif (not element.hasAttribute("imag")):
            return complex()
        else:
            mesg = "<complex> cannot have 'imag' attribute alone"
            self.logger.error(mesg)
            raise ValueError(mesg)

    def _evaluate_dict(self, element):
        """Convert a <dict> element to a Python dictionary."""
        kvpairs = []
        for item in element.getElementsByTagName("item"):
            # First, find the key and value elements
            key = item.firstChild
            while (not ((key.nodeType == xml.dom.Node.ELEMENT_NODE)
                    and (key.nodeName == "key"))):
                key = key.nextSibling
            value = key.nextSibling
            while (not ((value.nodeType == xml.dom.Node.ELEMENT_NODE)
                    and (value.nodeName == "value"))):
                value = value.nextSibling
            # Next, find the elements that define the actual values for the key
            # and value
            key = key.firstChild
            while (key.nodeType != xml.dom.Node.ELEMENT_NODE):
                key = key.nextSibling
            value = value.firstChild
            while (value.nodeType != xml.dom.Node.ELEMENT_NODE):
                value = value.nextSibling
            # Finally, evaluate the key and value ...
            key = self._evaluate(key)
            value = self._evaluate(value)
            # ... and add them to the list of key->value pairings
            kvpairs.append([key, value])
        dict_eval = aglyph.definition.Evaluator(dict, kvpairs)
        if (element.getAttribute("evaluate") != "eager"):
            return dict_eval
        else:
            return dict_eval.evaluate()

    def _evaluate_ellipsis(self, element):
        """Convert an <ellipsis> element to the builtin constant Ellipsis."""
        return Ellipsis

    def _evaluate_enumerate(self, element):
        """Convert an <enumerate> element to a Python enumeration."""
        items = [self._evaluate(node) for node in element.childNodes
                if (node.nodeType == xml.dom.Node.ELEMENT_NODE)]
        enum_eval = aglyph.definition.Evaluator(enumerate, items)
        if (element.getAttribute("evaluate") != "eager"):
            return enum_eval
        else:
            return enum_eval.evaluate()

    def _evaluate_false(self, element):
        """Convert a <false> element to the Python builtin constant False."""
        return False

    def _evaluate_file(self, element):
        """Convert a <file> element to a Python file object."""
        filename = element.getAttribute("filename")
        mode = element.getAttribute("mode") or 'r'
        bufsize = int(element.getAttribute("bufsize") or "-1")
        file_eval = aglyph.definition.Evaluator(file, filename, mode, bufsize)
        if (element.getAttribute("evaluate") != "eager"):
            return file_eval
        else:
            return file_eval.evaluate()

    def _evaluate_float(self, element):
        """Convert a <float> element to a Python float value."""
        if ((element.firstChild is not None)
                and (element.firstChild.nodeType == xml.dom.Node.TEXT_NODE)):
            return float(element.firstChild.nodeValue)
        else:
            return float()

    def _evaluate_frozenset(self, element):
        """Convert a <frozenset> element to a Python frozenset."""
        items = [self._evaluate(node) for node in element.childNodes
                if (node.nodeType == xml.dom.Node.ELEMENT_NODE)]
        frozenset_eval = aglyph.definition.Evaluator(frozenset, items)
        if (element.getAttribute("evaluate") != "eager"):
            return frozenset_eval
        else:
            return frozenset_eval.evaluate()

    def _evaluate_int(self, element):
        """Convert an <int> element to a Python int value."""
        if ((element.firstChild is not None)
                and (element.firstChild.nodeType == xml.dom.Node.TEXT_NODE)):
            radix = int(element.getAttribute("radix") or "10")
            return int(element.firstChild.nodeValue, radix)
        else:
            return int()

    def _evaluate_iter(self, element):
        """Convert an <iter> element to a Python iterator."""
        items = [self._evaluate(node) for node in element.childNodes
                if (node.nodeType == xml.dom.Node.ELEMENT_NODE)]
        iter_eval = aglyph.definition.Evaluator(iter, items)
        if (element.getAttribute("evaluate") != "eager"):
            return iter_eval
        else:
            return iter_eval.evaluate()

    def _evaluate_list(self, element):
        """Convert a <list> element to a Python list."""
        items = [self._evaluate(node) for node in element.childNodes
                if (node.nodeType == xml.dom.Node.ELEMENT_NODE)]
        list_eval = aglyph.definition.Evaluator(list, items)
        if (element.getAttribute("evaluate") != "eager"):
            return list_eval
        else:
            return list_eval.evaluate()

    def _evaluate_long(self, element):
        """Convert a <long> element to a Python long value."""
        if ((element.firstChild is not None)
                and (element.firstChild.nodeType == xml.dom.Node.TEXT_NODE)):
            radix = int(element.getAttribute("radix") or "10")
            return long(element.firstChild.nodeValue, radix)
        else:
            return long()

    def _evaluate_none(self, element):
        """Convert a <none> element to the Python builtin constant None."""
        return None

    def _evaluate_notimplemented(self, element):
        """Convert a <notimplemented> element to the builtin constant NotImplemented."""
        return NotImplemented

    def _evaluate_reference(self, element):
        """Convert a <reference> element to an Aglyph Reference type."""
        component_id = element.getAttribute("component").encode("us-ascii")
        return aglyph.definition.Reference(component_id)

    def _evaluate_set(self, element):
        """Convert a <set> element to a Python set."""
        items = set([self._evaluate(node) for node in element.childNodes
                if (node.nodeType == xml.dom.Node.ELEMENT_NODE)])
        set_eval = aglyph.definition.Evaluator(set, items)
        if (element.getAttribute("evaluate") != "eager"):
            return set_eval
        else:
            return set_eval.evaluate()

    def _evaluate_slice(self, element):
        """Convert a <slice> element to a Python slice."""
        start = None
        if (element.hasAttribute("start")):
            start = int(element.getAttribute("start"))
        stop = int(element.getAttribute("stop"))
        step = None
        if (element.hasAttribute("step")):
            step = int(element.getAttribute("step"))
        return slice(start, stop, step)

    def _evaluate_str(self, element):
        """Convert a <str> element to a Python string."""
        if ((element.firstChild is not None)
                and (element.firstChild.nodeType == xml.dom.Node.TEXT_NODE)):
            return str(element.firstChild.nodeValue.strip())
        else:
            return str()

    def _evaluate_true(self, element):
        """Convert a <true> element to the Python builtin constant True."""
        return True

    def _evaluate_tuple(self, element):
        """Convert a <tuple> element to a Python tuple."""
        items = [self._evaluate(node) for node in element.childNodes
                if (node.nodeType == xml.dom.Node.ELEMENT_NODE)]
        tuple_eval = aglyph.definition.Evaluator(tuple, items)
        if (element.getAttribute("evaluate") != "eager"):
            return tuple_eval
        else:
            return tuple_eval.evaluate()

    def _evaluate_unicode(self, element):
        """Convert a <unicode> element to a Python Unicode string."""
        if ((element.firstChild is not None)
                and (element.firstChild.nodeType == xml.dom.Node.TEXT_NODE)):
            # No conversion needed; the DOM stores Unicode strings by default
            return element.firstChild.nodeValue.strip()
        else:
            return unicode()

    def _evaluate_xrange(self, element):
        """Convert an <xrange> element to a Python xrange."""
        start = None
        if (element.hasAttribute("start")):
            start = int(element.getAttribute("start"))
        stop = int(element.getAttribute("stop"))
        step = None
        if (element.hasAttribute("step")):
            step = int(element.getAttribute("step"))
        if ((start is not None) and (step is not None)):
            return xrange(start, stop, step)
        elif (start is not None):
            return xrange(start, stop)
        elif (step is None):
            return xrange(stop)
        else:
            raise ValueError(
                "<xrange> must define 'start' if 'step' is defined")

    def _extract_context_info(self, context):
        """Extract the id, version, and description of this context."""
        if (context.hasAttribute("id")):
            self._id = context.getAttribute("version").encode("us-ascii")
        if (context.hasAttribute("version")):
            self._version = context.getAttribute("version").encode("us-ascii")
        description = context.getElementsByTagName("description")
        if (description):
            self._description = \
                description[0].firstChild.nodeValue.strip().encode("us-ascii")

    def _iter_component_values(self, component):
        """Return an iterator over this component's arguments and setters."""
        values = []
        init = component.getElementsByTagName("init")
        if (init):
            values.extend(self._parse_init(init[0]))
        setters = component.getElementsByTagName("setters")
        if (setters):
            values.extend(self._parse_setters(setters[0]))
        return iter(values)

    def _parse_init(self, init):
        """Return a list of initialization arguments."""
        values = []
        for arg in init.getElementsByTagName("arg"):
            value = arg.firstChild
            while (value.nodeType != xml.dom.Node.ELEMENT_NODE):
                value = value.nextSibling
            value = self._evaluate(value)
            if (arg.hasAttribute("name")):
                # keywords must be strings
                name = arg.getAttribute("name").encode("us-ascii")
                values.append(aglyph.definition.NamedValue(name, value))
            else:
                values.append(aglyph.definition.Value(value))
        return values

    def _parse_setters(self, setters):
        """Return a list of setters."""
        values = []
        for setter in setters.getElementsByTagName("setter"):
            attribute = setter.getAttribute("attribute").encode("us-ascii")
            value = setter.firstChild
            while (value.nodeType != xml.dom.Node.ELEMENT_NODE):
                value = value.nextSibling
            value = self._evaluate(value)
            values.append(aglyph.definition.Setter(attribute, value))
        return values

    def _parse_common_setters(self, common):
        """Return a list of common setters."""
        values = []
        for setter in common.getElementsByTagName("setter"):
            attribute = setter.getAttribute("attribute").encode("us-ascii")
            value = setter.firstChild
            while (value.nodeType != xml.dom.Node.ELEMENT_NODE):
                value = value.nextSibling
            value = self._evaluate(value)
            values.append(aglyph.definition.Setter(attribute, value))
        return values

