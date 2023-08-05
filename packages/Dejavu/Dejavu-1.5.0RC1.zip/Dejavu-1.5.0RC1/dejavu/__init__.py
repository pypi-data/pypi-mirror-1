"""Dejavu is an Object-Relational Mapper.

Persisted objects are called "Units", and are served into Sandboxes within
an Arena. Each Unit instance has a class, which maintains its schema via
Unit Properties.

"Dejavu", to quote Flying Circus episode 16, means "that strange feeling
we sometimes get that we've lived through something before." What better
name for a persistence system? Our terminology reflects this cognitive bent:
sandboxes "memorize", "recall" and "forget" Units.

Most Unit lifecycles follow the same pattern:
    aUnit = sandbox.unit(cls, ID=ID)
    val = aUnit.propertyName
    aUnit.propertyName = newValue
    del aUnit # or otherwise release the reference, e.g. close the scope.

When creating new Units, a similar pattern would be:
    newUnit = unit_class()
    newUnit.propertyName = newValue
    sandbox.memorize(newUnit)
    del newUnit # or otherwise release the reference.

Using recall(), you get a list; using xrecall(), you get an iterator:
    for unit in sandbox.recall(cls, expr):
        do_something_with(unit)

You destroy a Unit via Unit.forget().

Applications only need to call Unit.repress() when they wish to stop
caching the object, returning it to storage. This is very rare, and
should really only be performed within dejavu code.
"""

__version__ =  "1.5.0RC1"


import datetime as _datetime

from dejavu import analysis
sort = analysis.sort

from dejavu.arenas import *
from dejavu.schemas import *
from dejavu.units import *
from dejavu import logic


# Use this arena instance if you are deploying a single application per
# process. Otherwise, you should create your own instance per application.
dejavuarena = Arena()


###########################################################################
##                                                                       ##
##                           Logic functions                             ##
##                                                                       ##
###########################################################################


def icontains(a, b):
    """Case-insensitive test b in a. Note the operand order."""
    return icontainedby(b, a)

def icontainedby(a, b):
    """Case-insensitive test a in b. Note the operand order."""
    if isinstance(b, basestring):
        # Looking for text in a string.
        if a is None or b is None:
            return False
        return a.lower() in b.lower()
    else:
        # Looking for field in (a, b, c).
        # Force all args to lowercase for case-insensitive comparison.
        if a is None or not b:
            return False
        return a.lower() in [x.lower() for x in b]

def istartswith(a, b):
    """True if a starts with b (case-insensitive), False otherwise."""
    if a is None or b is None:
        return False
    return a.lower().startswith(b.lower())

def iendswith(a, b):
    """True if a ends with b (case-insensitive), False otherwise."""
    if a is None or b is None:
        return False
    return a.lower().endswith(b.lower())

def ieq(a, b):
    """True if a == b (case-insensitive), False otherwise."""
    if a is None or b is None:
        return False
    return (a.lower() == b.lower())

def year(value):
    """The year attribute of a date."""
    if isinstance(value, (_datetime.date, _datetime.datetime)):
        return value.year
    else:
        return None

def month(value):
    """The month attribute of a date."""
    if isinstance(value, (_datetime.date, _datetime.datetime)):
        return value.month
    else:
        return None

def day(value):
    """The day attribute of a date."""
    if isinstance(value, (_datetime.date, _datetime.datetime)):
        return value.day
    else:
        return None

def now():
    """Late-bound datetime.datetime.now(). Taint this when early binding."""
    return _datetime.datetime.now()
now.bind_late = True

def today():
    """Late-bound datetime.date.today(). Taint this when early binding."""
    return _datetime.date.today()
today.bind_late = True

def iscurrentweek(value):
    """If value is in the current week, return True, else False."""
    if isinstance(value, (_datetime.date, _datetime.datetime)):
        return _datetime.date.today().strftime('%W%Y') == value.strftime('%W%Y')
    else:
        return False
iscurrentweek.bind_late = True

# Inject these functions into the logic module's globals.
class _Empty(object): pass
_d = _Empty()
for _name in ['icontains', 'icontainedby', 'istartswith', 'iendswith',
              'ieq', 'year', 'month', 'now', 'today', 'iscurrentweek']:
    setattr(_d, _name, globals()[_name])
logic.dejavu = _d
del _name, _d, _Empty
