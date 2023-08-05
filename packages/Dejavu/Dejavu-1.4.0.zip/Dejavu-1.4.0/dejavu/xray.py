"""Load modules, classes, functions, and attributes by dotted package names.

This work, including the source code, documentation
and related data, is placed into the public domain.

The orginal author is Robert Brewer, Amor Ministries.

THIS SOFTWARE IS PROVIDED AS-IS, WITHOUT WARRANTY
OF ANY KIND, NOT EVEN THE IMPLIED WARRANTY OF
MERCHANTABILITY. THE AUTHOR OF THIS SOFTWARE
ASSUMES _NO_ RESPONSIBILITY FOR ANY CONSEQUENCE
RESULTING FROM THE USE, MODIFICATION, OR
REDISTRIBUTION OF THIS SOFTWARE.

Usage:

    desiredClass = xray.classes("myapp.stringtools.alwayslowercase", str)
    newInstance = desiredClass()

or

    for f in startup_function_names:
        func_object = xray.functions(f)
        func_object()


Rationale:

I try to create systems that are configurable by deployers; mostly becase I
hate it when an application forces me to use the database, filesystem,
communication protocol, algorithm, or operating system du jour. Abstracting
these basic components of an application is its own study (look up the Gang
of Four "Strategy" pattern for a start); this is often accomplished with
classes which share signatures, often via subclassing. However, the deployer
then needs to specify the class they wish to use. This module gives them
the ability to specify that with a single string (for example, in a text
configuration file).

"""

import sys

def modules(modulePath):
    """Load a module and retrieve a reference to that module."""
    try:
        aMod = sys.modules[modulePath]
        if aMod is None:
            raise KeyError
    except KeyError:
        # The last [''] is important.
        aMod = __import__(modulePath, globals(), locals(), [''])
    return aMod

def attributes(fullAttributeName):
    """Load a module and retrieve an attribute of that module."""
    
    # Parse out the path, module, and attribute
    lastDot = fullAttributeName.rfind(u".")
    attrName = fullAttributeName[lastDot + 1:]
    modPath = fullAttributeName[:lastDot]
    
    aMod = modules(modPath)
    # Let an AttributeError propagate outward.
    try:
        anAttr = getattr(aMod, attrName)
    except AttributeError:
        raise AttributeError("'%s' object has no attribute '%s'"
                             % (modPath, attrName))
    
    # Return a reference to the attribute.
    return anAttr

def functions(fullFuncName):
    """Load a module and retrieve a function object."""
    
    aFunc = attributes(fullFuncName)
    
    # Assert that the function is a *callable* attribute.
    if not callable(aFunc):
        raise TypeError(u"'%s' is not callable." % fullFuncName)
    
    # Return a reference to the function itself,
    # not the results of the function.
    return aFunc

def classes(fullClassName, parentClass=None):
    """Load a module and retrieve a class (NOT an instance).
    
    If the parentClass is supplied, className must be of parentClass
    or a subclass of parentClass (or None is returned).
    """
    aClass = functions(fullClassName)
    
    # Assert that the class is a subclass of parentClass.
    if parentClass is not None:
        if not issubclass(aClass, parentClass):
            raise TypeError(u"'%s' is not a subclass of %s" %
                            (fullClassName, parentClass.__name__))
    
    # Return a reference to the class itself, not an instantiated object.
    return aClass

