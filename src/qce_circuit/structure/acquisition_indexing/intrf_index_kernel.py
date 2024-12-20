# -------------------------------------------
# Module describing interface for acquisition indexing.
# Intended to be used in combination with acquisition registry.
# -------------------------------------------
from abc import ABC, abstractmethod
from typing import List
from qce_circuit.utilities.custom_exceptions import InterfaceMethodException
from qce_circuit.connectivity.intrf_channel_identifier import IQubitID


class IIndexingKernel(ABC):
    """
    Interface class, describing qubit acquisition indexing.
    """

    # region Interface Properties
    @property
    @abstractmethod
    def start_index(self) -> int:
        """:return: Starting index."""
        raise InterfaceMethodException

    @property
    @abstractmethod
    def stop_index(self) -> int:
        """:return: End index."""
        raise InterfaceMethodException

    @property
    def kernel_length(self) -> int:
        """:return: Length of indexing kernel."""
        return self.stop_index - self.start_index + 1  # +1 used to make sure all other indices are INCLUSIVE.
    # endregion

    # region Interface Methods
    @abstractmethod
    def contains(self, element: IQubitID) -> List[int]:
        """:return: Array-like of measurement indices corresponding to element within this indexing kernel."""
        raise InterfaceMethodException
    # endregion
