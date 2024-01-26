# -------------------------------------------
# Customized warnings for better maintainability
# -------------------------------------------
import warnings


class WhileLoopSafetyExceededWarning(Warning):
    """
    Raised when while-loop safety counter exceeds the allowed number of iterations.
    """

    # region Class Methods
    @classmethod
    def warning_format(cls, max_iter: int) -> dict:
        return dict(
            message=f"Max iterations reached ({max_iter}/{max_iter}), exiting loop.",
            category=cls,
        )
    # endregion


class OperationNotFoundWarning(Warning):
    """
    Raised when (copied) operation instance is unknown or not found.
    """

    # region Class Methods
    @classmethod
    def warning_format(cls, value: object) -> dict:
        return dict(
            message=f"Operation ({value}) not found.",
            category=cls,
        )
    # endregion


# Apply Global warning filters
warnings.simplefilter("once", OperationNotFoundWarning)
