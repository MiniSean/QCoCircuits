# -------------------------------------------
# Customized context managers for better maintainability
# -------------------------------------------
import warnings
from qce_circuit.utilities.custom_warnings import WhileLoopSafetyExceededWarning


class WhileLoopSafety:
    """
    Context manager class,
    """

    # region Class Constructor
    def __init__(self, max_iterations: int = 10):
        self.counter = 0
        self.max_iterations = max_iterations
    # endregion

    # region Class Methods
    def safety_condition(self):
        if self.counter >= self.max_iterations:
            warnings.warn(**WhileLoopSafetyExceededWarning.warning_format(max_iter=self.max_iterations))
            return False
        self.counter += 1
        return True

    def __enter__(self) -> 'WhileLoopSafety':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False
    # endregion
