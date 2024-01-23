# -------------------------------------------
# Module describing interface for acquisition indexing strategy.
# Includes basic implementations
# -------------------------------------------
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from qce_utils.custom_exceptions import InterfaceMethodException
from qce_circuit.structure.acquisition_indexing.intrf_index_kernel import IIndexingKernel


class IIndexStrategy(ABC):
    """
    Interface class, describing strategy for (measurement) index offset.
    """

    # region Interface Properties
    @abstractmethod
    def get_index(self, task: IIndexingKernel) -> int:
        """:return: Index [a.u.]."""
        raise InterfaceMethodException
    # endregion


@dataclass(frozen=True)
class FixedIndexStrategy(IIndexStrategy):
    """
    Data class, implementing IIndexStrategy interface.
    Forces fixed indexing.
    """
    index: int = field(default=0)

    # region Interface Properties
    def get_index(self, task: IIndexingKernel) -> int:
        """:return: Index [a.u.]."""
        return self.index
    # endregion


@dataclass(frozen=True)
class RelativeIndexStrategy(IIndexStrategy):
    """
    Data class, implementing IIndexStrategy interface.
    Forces relative indexing.
    """
    reference_index_kernel: IIndexingKernel

    # region Interface Properties
    def get_index(self, task: IIndexingKernel) -> int:
        """:return: Index [a.u.]."""
        return self.reference_index_kernel.stop_index + 1
    # endregion
