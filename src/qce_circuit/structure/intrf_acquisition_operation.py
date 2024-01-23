# -------------------------------------------
# Module containing interface and implementation of (declarative) acquisition operation.
# -------------------------------------------
from abc import ABC, abstractmethod, ABCMeta
from dataclasses import dataclass, field
from qce_circuit.utilities.custom_exceptions import InterfaceMethodException
from qce_circuit.structure.intrf_circuit_operation import ICircuitOperation


@dataclass(frozen=True)
class AcquisitionTag:
    """
    Data class, containing unique identifier for acquisition.
    """
    qubit_index: int = field(init=True, compare=True)
    tag: str = field(init=True, compare=True)

    def equal_tag(self, other: 'AcquisitionTag') -> bool:
        """:return: Boolean, whether qubit_index and tag match, ignoring unique identifier."""
        return self.qubit_index == other.qubit_index and self.tag == other.tag


@dataclass(frozen=True)
class AcquisitionIdentifier(AcquisitionTag):
    """
    Data class, containing unique identifier for acquisition.
    """
    unique_identifier: int = field(init=False, repr=True, compare=True, default_factory=lambda: AcquisitionIdentifier._id_counter)
    """Automatically populated (instance) identifier."""
    _id_counter: int = field(init=False, repr=False, compare=False, default=0)
    """Class level counter. Used to populate unique identifier."""

    # region Class Methods
    def __post_init__(self):
        AcquisitionIdentifier._id_counter += 1

    def __repr__(self):
        return f"{self.__class__.__name__}(#{str(self.unique_identifier).zfill(3)})"
    # endregion


class IAcquisitionComponent(ABC):
    """
    Interface class, describing acquisition channel index.
    """

    # region Interface Properties
    @property
    @abstractmethod
    def acquisition_identifier(self) -> AcquisitionIdentifier:
        """:return: Unique acquisition identifier."""
        raise InterfaceMethodException

    @property
    @abstractmethod
    def acquisition_index(self) -> int:
        """
        :return: Unique acquisition index on qubit level.
        Every (measure) operation acquisition is processed at its own index.
        """
        raise InterfaceMethodException

    @property
    @abstractmethod
    def circuit_level_acquisition_index(self) -> int:
        """
        :return: Unique acquisition index on circuit level.
        Every (measure) operation acquisition is processed at its own index.
        """
        raise InterfaceMethodException
    # endregion


class IAcquisitionOperation(ICircuitOperation, IAcquisitionComponent, metaclass=ABCMeta):
    """
    Interface class, extending ICircuitOperation with IAcquisitionComponent interface.
    Specific for acquisition operations and often used by index kernels.
    """
    pass
