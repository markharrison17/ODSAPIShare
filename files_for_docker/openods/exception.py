# define Python user-defined exceptions
class Error(Exception):
    """Base class for other exceptions"""
    def __init__(self):
        pass


class DatabaseConnectionError(Error):
    """Raised when the Database can't be connected to"""
    def __init__(self):
        pass


class ServiceError(Error):
    """Raised when there is an error in one of the lower software stack layers"""
    def __init__(self):
        pass


class InvalidDataError(Error):
    """Raised when the data in the underlying DB doesn't conform to the schema"""
    def __init__(self):
        pass


class DatabaseError(Error):
    """Raised when there is a general database error"""
    def __init__(self):
        pass

class RoleCodeError(Error):
    """Raised when role code does not start with RO when calling the codesystems endpoint"""
    def __init__(self):
        pass

class UnfoundOrgError(Error):
    """Raised when an Organisation is not found for a particular organisation code"""
    def __init__(self):
        pass