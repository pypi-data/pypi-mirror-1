"""Aglyph -- A dependency injection framework for Python.

Aglyph supports Type 2 (setter) and Type 3 (constructor) injection, and
can be configured programmatically or via an XML configuration file.

"""

import ConfigParser
import logging

import aglyph.cache
import aglyph.classloader

__version__ = "0.8"

# Configure logging
log_formatter = logging.Formatter(
    "%(asctime)s %(levelname)s [%(module)s] %(message)s")
log_handler = logging.FileHandler("/tmp/aglyph.log")
log_handler.setFormatter(log_formatter)
logger = logging.getLogger("aglyph")
logger.setLevel(logging.DEBUG)
logger.addHandler(log_handler)
logger = logging.getLogger("aglyph")

_BootstrapClassLoader = aglyph.classloader.ClassLoader()

_AssemblerCache = aglyph.cache.Cache(aglyph.cache.Cache.NEVER_EXPIRE)


def get_assembler(fp, reload=False):
    """Return an assembler that uses the specified configuration.

    Arguments:
    fp -- a file-like object containing INI-style configuration settings
          (must minimally support read())
    reload -- if True, will always create the assembler, even if it's
              already cached (default False)

    """
    funcname = "get_assembler"
    assembler_id = "<anonymous>"
    need_close = True
    if (isinstance(fp, basestring)):
        fp = _BootstrapClassLoader.find_resource(fp)
        assembler_id = fp
        fp = file(fp, "rb")
    else:
        if (hasattr(fp, "name")):
            assembler_id = _BootstrapClassLoader.find_resource(fp.name)
        need_close = False

    assembler = _AssemblerCache.get(assembler_id)
    if ((assembler is None) or (reload is True)):
        logger.info("%s: loading assembler settings from %r", funcname,
                assembler_id)

        cp = ConfigParser.SafeConfigParser()
        cp.readfp(fp)
        if (need_close):
            fp.close()

        classpath = cp.get("ClassLoader", "classpath")
        logger.info("%s: using class loader %s", funcname, classpath)
        ClassLoaderClass = _BootstrapClassLoader.load_class(classpath)
        classloader = ClassLoaderClass()

        classpath = cp.get("Context", "classpath")
        logger.info("%s: using context %s", funcname, classpath)
        ContextClass = _BootstrapClassLoader.load_class(classpath)
        filename = None
        if (cp.has_option("Context", "filename")):
            filename = _BootstrapClassLoader.find_resource(
                cp.get("Context", "filename"))
        context = ContextClass()
        if (filename is not None):
            logger.info("%s: loading %s from %r", funcname, classpath,
                    filename)
            context.load(filename)

        classpath = cp.get("Cache", "classpath")
        logger.info("%s: using cache %s", funcname, classpath)
        CacheClass = _BootstrapClassLoader.load_class(classpath)
        ttl = None
        if (cp.has_option("Cache", "ttl")):
            ttl = cp.getint("Cache", "ttl")
        cache = CacheClass()
        if (ttl is not None):
            logger.info("%s: setting %s TTL to %ds", funcname, classpath,
                    ttl)
            cache.set_ttl(ttl)

        classpath = cp.get("Assembler", "classpath")
        logger.info("%s: using assembler %s", funcname, classpath)
        AssemblerClass = _BootstrapClassLoader.load_class(classpath)
        if (cp.has_option("Assembler", "preassemble")):
            preassemble = cp.get("Assembler", "preassemble").split()
        else:
            preassemble = []
        assembler = AssemblerClass(context, classloader, cache)
        for strategy in preassemble:
            for component_id in assembler.iter_by_strategy(strategy):
                logger.info("%s: preassembling %s %r", funcname, strategy,
                        component_id)
                assembler.assemble(component_id)
        if (assembler_id != "<anonymous>"):
            logger.info("%s: caching assembler %r", funcname, assembler_id)
            _AssemblerCache[assembler_id] = assembler

    return assembler

