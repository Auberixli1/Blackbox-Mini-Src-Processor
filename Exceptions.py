class Error(Exception):
    """Base class for other exceptions"""
    pass

class SourceEmptyError(Error):
    """Raised when no units are found within the source ML"""
    pass
