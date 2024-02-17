# -------------------------------------------
# Customized exceptions for better maintainability
# -------------------------------------------


class InterfaceMethodException(Exception):
    """
    Raised when the interface method is not implemented.
    """


class ElementNotIncludedException(Exception):
    """
    Raised when element (such as IQubitID, IEdgeID or IFeedlineID) is not included in the connectivity layer.
    """


class NoReferenceOperationException(Exception):
    """
    Raised when functionality depending on non-zero number of (reference) operations fails.
    """


class RelationTypeNotImplementedException(Exception):
    """
    Raised when (operation) relation type is not implemented.
    """


class IsolatedGroupException(Exception):
    """
    Raised when a list of grouped elements are not isolated. Members from one group are shared in another group.
    """

class InvalidPointerException(Exception):
    """
    Raised when file-pointer is invalid (path-to-file does not exist).
    """