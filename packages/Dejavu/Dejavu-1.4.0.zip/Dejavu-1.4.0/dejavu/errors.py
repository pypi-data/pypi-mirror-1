
__all__ = ['DejavuError', 'AssociationError', 'UnrecallableError',
           'StorageWarning']

class DejavuError(Exception):
    """Base class for errors which occur within Dejavu."""
    def __init__(self, *args):
        Exception.__init__(self)
        self.args = args
    
    def __str__(self):
        return u'\n'.join([unicode(eachArg) for eachArg in self.args])

class AssociationError(DejavuError):
    """Exception raised when a Unit association fails."""
    pass

class UnrecallableError(DejavuError):
    """Exception raised when a Unit was sought but not recalled."""
    pass

class StorageWarning(UserWarning):
    """Warning about functionality which is not supported by all SM's."""
    pass
