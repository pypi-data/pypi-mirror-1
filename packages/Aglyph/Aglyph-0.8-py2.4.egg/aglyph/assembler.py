"""A basic component assembly class.

Assemblers have the following public methods:
assemble(component_id) -- build (or retrieve from cache) a fully-
                          assembled class instance
create(component_id) -- construct a new, fully-assembled class instance
iter_by_strategy(strategy) -- iterate over the component IDs in this
                              assembler's context that use the specified
                              assembly strategy

Additionally, assemblers support the "in" operation for both membership
testing and iteration (both with respect to component IDs).

"""

import logging

import aglyph.definition


class Assembler:

    """A class that provides composite classes with their dependencies.

    Each instance owns a context (for determining dependencies), a
    classloader (for creating class objects from classpaths), and a
    cache (for storing references to singleton instances).

    """

    logger = logging.getLogger("aglyph")

    def __init__(self, context, classloader, cache):
        """Create a new assembler.

        Arguments:
        context -- a mapping of component IDs to definitions
        classloader -- provides a load_class factory method for creating class
                      objects
        cache -- a mapping (assembler-managed) that will map component IDs to
                 cacheable assembled instances (e.g. singletons)

        """
        methodname = "__init__"
        self.logger.debug("ENTER %s", methodname)
        self.__context = context
        self.__classloader = classloader
        self.__cache = cache
        self.logger.debug("EXIT %s", methodname)

    def assemble(self, component_id):
        """Return a cached or created instance of the named component.

        Arguments:
        component_id -- a value that uniquely identifies a component in this
                        assembler's context

        """
        methodname = "assemble"
        self.logger.debug("ENTER %s", methodname)
        instance = self.__cache.get(component_id)
        if (instance is None):
            self.logger.info("%s: assembling %r", methodname, component_id)
            instance = self.create(component_id)
            strategy = self.__context.get_creation_strategy(component_id)
            if (strategy == "singleton"):
                self.logger.info("%s: caching %s %r", methodname, strategy,
                        component_id)
                self.__cache[component_id] = instance
        self.logger.debug("EXIT %s", methodname)
        return instance

    def create(self, component_id):
        """Create a new instance of the named component.

        Arguments:
        component_id -- a value that uniquely identifies a component in this
                        assembler's context

        """
        methodname = "create"
        self.logger.debug("ENTER %s", methodname)
        definition = self.__context[component_id]
        instance = self._realize(definition)
        self._wire(instance, definition)
        self.logger.debug("EXIT %s", methodname)
        return instance

    def iter_by_strategy(self, strategy):
        """Return an iterator over the component IDs for an assembly strategy.

        Arguments:
        strategy -- a named assembly strategy (e.g. "singleton")

        """
        for definition in self.__context.itervalues():
            if (definition.get_creation_strategy() == strategy):
                yield definition.get_component_id()

    def _evaluate(self, value):
        """Return the actual value of an init or setter argument.

        If the value is a reference to another component ID, the assembler
        recursively calls assemble for that component ID.

        """
        methodname = "_evaluate"
        self.logger.debug("ENTER %s", methodname)
        value = value.get_value()
        if (isinstance(value, aglyph.definition.Reference)):
            value = self.assemble(value)
        elif (isinstance(value, aglyph.definition.Evaluator)):
            value = value.evaluate()
        self.logger.debug("EXIT %s", methodname)
        return value

    def _realize(self, definition):
        """Return an instance of the defined component.

        This method performs Type 3 (constructor) injection.

        """
        methodname = "_realize"
        self.logger.debug("ENTER %s", methodname)
        self.logger.info("%s: %s", methodname, definition)
        class_ = self.__classloader.load_class(definition.get_classpath())
        inject_args = tuple(
            [self._evaluate(arg) for arg in definition.iter_init_args()])
        inject_kwargs = {}
        for kwarg in definition.iter_init_kwargs():
            inject_kwargs[kwarg.get_name()] = self._evaluate(kwarg)
        instance = class_(*inject_args, **inject_kwargs)
        self.logger.debug("EXIT %s", methodname)
        return instance

    def _wire(self, instance, definition):
        """Inject common and component dependencies into an instance."""
        methodname = "_wire"
        self.logger.debug("ENTER %s", methodname)
        for setter in self.__context.iter_common_setters():
            self._inject(instance, setter, False)
        for setter in definition.iter_setters():
            self._inject(instance, setter)
        self.logger.debug("EXIT %s", methodname)

    def _inject(self, instance, setter, raise_if_undefined=True):
        """Assign defined dependencies to a class instance.

        This method performs Type 2 (setter) injection.  The instance is
        modified in place.

        If raise_if_undefined is True (default), this method will raise
        AttributeError if the instance does not define the setter attribute.

        """
        methodname = "_inject"
        self.logger.debug("ENTER %s", methodname)
        instance_attributes = dir(instance)
        attribute_name = setter.get_name()
        if (attribute_name in instance_attributes):
            attribute_value = self._evaluate(setter)
            # Since hasattr(...) performs its test by calling __getattr__, the
            # following test allows attributes defined as setter-only
            # properties to be correctly; calling getattr(...) directly on such
            # attributes would otherwise raise AttributeError.
            if (hasattr(instance, attribute_name)):
                attr = getattr(instance, attribute_name)
            else:
                attr = None
            if (callable(attr)):
                attr(attribute_value)
            else:
                setattr(instance, attribute_name, attribute_value)
        elif (raise_if_undefined):
            self.logger.warning("%s: no setter attribute %r for %s",
                    methodname, attribute_name, definition.get_classpath())
            raise AttributeError(attribute_name)
        self.logger.debug("EXIT %s", methodname)

    def __contains__(self, component_id):
        """Return True if this assembler can assemble the named component."""
        return (component_id in self.__context)

    def __iter__(self):
        """Return an iterator over this assembler's component IDs."""
        return iter(self.__context)

