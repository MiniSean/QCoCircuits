# -------------------------------------------
# Module containing interface for draw methods.
# -------------------------------------------
from abc import ABC, abstractmethod
from matplotlib import pyplot as plt
from qce_circuit.utilities.custom_exceptions import InterfaceMethodException


class IDrawComponent(ABC):
    """
    Interface class, describing draw method.
    """

    # region Interface Methods
    @abstractmethod
    def draw(self, axes: plt.Axes) -> plt.Axes:
        """Method used for drawing component on Axes."""
        raise InterfaceMethodException
    # endregion
