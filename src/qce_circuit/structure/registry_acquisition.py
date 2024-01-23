# -------------------------------------------
# Module describing acquisition (strategy) registry.
# A registry can be used to manage and access the acquisition channel of operations.
# -------------------------------------------
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Optional
from qce_circuit.utilities.custom_exceptions import InterfaceMethodException
from qce_circuit.structure.intrf_registry import (
    IRegistryGetter,
)
from qce_circuit.structure.intrf_circuit_operation import (
    ICircuitOperation,
)
from qce_circuit.structure.intrf_acquisition_operation import (
    IAcquisitionOperation,
    AcquisitionIdentifier,
)


@dataclass(frozen=True)
class AcquisitionIndexInfo:
    """
    Data class, containing detailed information about acquisition index.
    """
    qubit_level_index: int
    """Acquisition index on (single) qubit level."""
    circuit_level_index: int
    """Acquisition index on (multi-qubit) circuit level."""


class AcquisitionRegistry(IRegistryGetter[AcquisitionIdentifier, AcquisitionIndexInfo]):
    """
    Behaviour class, containing registry for setting and getting measure operation acquisition number.
    The registry is intended to be linked with (variable) acquisition strategies.
    """

    # region Class Constructor
    def __init__(self, circuit: ICircuitOperation):
        """
        Initializes the RepetitionRegistry with an empty dictionary for storing repetition numbers.
        """
        self.reference_circuit: ICircuitOperation = circuit
        self._default: AcquisitionIndexInfo = AcquisitionIndexInfo(-1, -1)
    # endregion

    # region Class Methods
    def get_registry_at(self, key: AcquisitionIdentifier) -> AcquisitionIndexInfo:
        """
        Retrieves value associated with a given key.
        :param key: The unique identifier for the registry value.
        :return: The registry value associated with the key. If the key is not found,
        a default value (e.g., None or a predefined default) can be returned.
        """
        qubit_level_acquisition_index: int = 0
        circuit_level_acquisition_index: int = 0
        for operation in self.reference_circuit.decomposed_operations():
            if isinstance(operation, IAcquisitionOperation):
                qubit_id_match: bool = operation.acquisition_identifier.qubit_index == key.qubit_index
                key_match: bool = operation.acquisition_identifier == key
                if key_match:
                    return AcquisitionIndexInfo(
                        qubit_level_index=qubit_level_acquisition_index,
                        circuit_level_index=circuit_level_acquisition_index,
                    )
                if qubit_id_match:
                    qubit_level_acquisition_index += 1
                circuit_level_acquisition_index += 1
        # Return default value if key was not found
        return self._default
    # endregion


class IAcquisitionStrategy(ABC):
    """
    Interface class, describing strategy for measure operation acquisitions.
    """

    # region Interface Methods
    @abstractmethod
    def get_acquisition_info(self, task: IAcquisitionOperation) -> AcquisitionIndexInfo:
        """:return: Channel index of acquisition."""
        raise InterfaceMethodException

    @abstractmethod
    def copy(self, strategy_transfer_lookup: Optional[Dict[ICircuitOperation, ICircuitOperation]] = None) -> 'IAcquisitionStrategy':
        """
        Creates a copy from self. Excluding any relation details.
        :param strategy_transfer_lookup: Lookup table used to transfer relation link.
        :return: Copy of self.
        """
        raise InterfaceMethodException
    # endregion


@dataclass(frozen=True)
class RegistryAcquisitionStrategy(IAcquisitionStrategy):
    """
    Data class, implementing IAcquisitionStrategy interface.
    """
    registry: AcquisitionRegistry = field(init=True, repr=False)

    # region Interface Methods
    def get_acquisition_info(self, task: IAcquisitionOperation) -> AcquisitionIndexInfo:
        """:return: Channel index of acquisition."""
        return self.registry.get_registry_at(key=task.acquisition_identifier)

    def copy(self, strategy_transfer_lookup: Optional[Dict[ICircuitOperation, ICircuitOperation]] = None) -> 'IAcquisitionStrategy':
        """
        Creates a copy from self. Excluding any relation details.
        :param strategy_transfer_lookup: Lookup table used to transfer relation link.
        :return: Copy of self with updated registry.
        """
        if strategy_transfer_lookup is None:
            strategy_transfer_lookup = {}
        new_reference_circuit: ICircuitOperation = strategy_transfer_lookup.get(self.registry.reference_circuit, self.registry.reference_circuit)

        return RegistryAcquisitionStrategy(
            registry=AcquisitionRegistry(circuit=new_reference_circuit)
        )
    # endregion
