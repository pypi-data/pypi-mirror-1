
class DejavuError(Exception):
    """Base class for errors which occur within Dejavu."""
    def __init__(self, *args):
        Exception.__init__(self)
        self.args = args
    
    def __str__(self):
        return u'\n'.join([unicode(arg) for arg in self.args])

class AssociationError(DejavuError):
    """Exception raised when a Unit association fails."""
    pass

class UnrecallableError(DejavuError):
    """Exception raised when a Unit was sought but not recalled."""
    pass

class MappingError(DejavuError):
    """Exception raised when a Unit class cannot be mapped to storage.
    
    This exception should be raised when a consumer attempts to build
    a map between a Unit class and existing internal storage structures.
    Other exceptions may be raised when trying to find such a map after
    it has already (supposedly) been created. That is, the questions
    "do we have a map?" and "can we create a map?" are distinct.
    The latter should raise this exception whenever possible.
    The behavior of the former is not specified.
    """
    pass

class StorageWarning(UserWarning):
    """Warning about functionality which is not supported by all SM's."""
    pass
