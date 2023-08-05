"""Classes used to define a component."""


class Evaluator:

    """A class that knows how to create an object on demand."""

    def __init__(self, initializer, *args, **kwargs):
        """Create an object that returns fresh values.

        Arguments:
        initializer -- a builtin callable that constructs some type
        args -- a tuple of positional arguments passed to the initializer
        kwargs -- a map of named arguments passed to the initializer

        """
        self.__initializer = initializer
        self.__args = args
        self.__kwargs = kwargs.copy()

    def evaluate(self):
        """Return a fresh object."""
        return self.__initializer(
            *self._evaluate_args(self.__args),
            **self._evaluate_kwargs(self.__kwargs))

    def _evaluate_args(self, args):
        """Evaluate each argument in the sequence."""
        return tuple([self._evaluate(arg) for arg in args])

    def _evaluate_kwargs(self, kwargs):
        """Evaluate each named argument in the mapping."""
        return dict(
            [(self._evaluate(k), self._evaluate(v))
                for (k, v) in kwargs.iteritems()])

    def _evaluate(self, value):
        """Return the value as a Python builtin type."""
        if (isinstance(value, Evaluator)):
            return value.evaluate()
        elif (isinstance(value, dict)):
            return dict(
                [(self._evaluate(k), self._evaluate(v))
                    for (k, v) in value.iteritems()])
        elif (hasattr(value, "__iter__")
                and (not isinstance(value, basestring))):
            return value.__class__([self._evaluate(v) for v in value])
        else:
            return value

    def __str__(self):
        return "%s *%s **%s" % (self.__initializer, self.__args, self.__kwargs)


class Value:

    """A class that defines an argument value."""

    def __init__(self, value):
        """Create an anonymous (non-named) argument value.

        Arguments:
        value -- the actual value

        """
        self.__value = value

    def get_value(self):
        """Return the argument value."""
        return self.__value


class NamedValue(Value):

    """A class that defines a named argument value."""

    def __init__(self, name, value):
        """Create a named argument value.

        Arguments:
        name -- the name to which the value is bound
        value -- the actual value

        """
        Value.__init__(self, value)
        self.__name = name

    def get_name(self):
        """Return the argument name."""
        return self.__name

    def __eq__(self, other):
        return (isinstance(other, NamedValue)
                and (self.__name == other.get_name()))

    def __hash__(self):
        return hash(self.__name)


class Setter(NamedValue):

    """A class that defines an instance attribute and its value."""

    pass


class Reference(str):

    """A class that defines the Aglyph Reference type."""

    pass


class Definition:

    """A class that defines a component's constructor arguments and setters."""

    def __init__(self, component_id, classpath, creation_strategy):
        """Create a new component definition.

        Arguments:
        component_id -- a value that identifies some component
        classpath -- the Python classpath of the component's class object
        creation_strategy -- the creation strategy for this component
                             (e.g. "singleton")

        """
        self.__component_id = component_id
        self.__classpath = classpath
        self.__creation_strategy = creation_strategy
        self.__init_args = []
        self.__init_kwargs = []
        self.__setters = []

    def add(self, value):
        """Add a constructor argument or setter to this definition.

        Arguments:
        value -- a Value, NamedValue, or Setter instance

        """
        if (isinstance(value, Setter)):
            if (value not in self.__setters):
                self.__setters.append(value)
            else:
                raise ValueError("setter %r already defined for %s"
                        % (value.get_name(), self))
        elif (isinstance(value, NamedValue)):
            if (value not in self.__init_kwargs):
                self.__init_kwargs.append(value)
            else:
                raise ValueError("init kwarg %r already defined for %s"
                        % (value.get_name(), self))
        elif (isinstance(value, Value)):
            self.__init_args.append(value)
        else:
            raise TypeError(str(type(value)))

    def add_init_arg(self, value):
        """Add a positional constructor argument to this definition.

        Arguments:
        value -- the argument value

        """
        self.add(Value(value))

    def add_init_kwarg(self, name, value):
        """Add a keyword constructor argument to this definition.

        Arguments:
        name -- the argument name
        value -- the argument value

        """
        self.add(NamedValue(name, value))

    def add_setter(self, name, value):
        """Add a setter to this definition.

        Arguments:
        name -- the instance attribute name
        value -- the value to assign to the instance attribute

        The name can be the name of a simple instance property, a managed
        instance property, or a mutator method.

        """
        self.add(Setter(name, value))

    def get_component_id(self):
        """Return the ID of the defined component."""
        return self.__component_id

    def get_classpath(self):
        """Return the classpath of the defined component."""
        return self.__classpath

    def get_creation_strategy(self):
        """Return the creation strategy of the defined component."""
        return self.__creation_strategy

    def iter_init_args(self):
        """Return an iterator over the positional constructor arguments."""
        return iter(self.__init_args)

    def iter_init_kwargs(self):
        """Return an iterator over the keyword constructor arguments."""
        return iter(self.__init_kwargs)

    def iter_setters(self):
        """Return an iterator over the setter attributes."""
        return iter(self.__setters)

    def __str__(self):
        """Return a meaningful representation of this definition."""
        return "%s (%s)" % (self.__component_id, self.__classpath)

