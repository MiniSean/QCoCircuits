# -------------------------------------------
# Module describing repetition (strategy) registry.
# A registry can be used to manage and access the repetition number of operations.
# -------------------------------------------
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Callable
from qce_circuit.utilities.custom_exceptions import InterfaceMethodException
from qce_circuit.structure.intrf_registry import IRegistry
from qce_circuit.structure.intrf_circuit_operation import ICircuitOperation


class RepetitionRegistry(IRegistry[str, int]):
    """
    Behaviour class, containing registry for setting and getting composite operation repetitions.
    The registry is intended to be linked with (variable) repetition strategies.
    """

    # region Class Constructor
    def __init__(self):
        """
        Initializes the RepetitionRegistry with an empty dictionary for storing repetition numbers.
        """
        self._variable_repetitions: Dict[str, int] = {}
        self._default_repetition: int = 1
    # endregion

    # region Class Methods
    def set_registry_at(self, key: str, value: int):
        """
        Sets the value for a given key.
        :param key: The unique identifier for the registry value.
        :param value: The value to be associated with the key.
        :return: Void
        """
        self._variable_repetitions[key] = value

    def get_registry_at(self, key: str) -> int:
        """
        Retrieves value associated with a given key.
        :param key: The unique identifier for the registry value.
        :return: The registry value associated with the key. If the key is not found,
        a default value (e.g., None or a predefined default) can be returned.
        """
        return self._variable_repetitions.get(key, self._default_repetition)
    # endregion


class IRepetitionStrategy(ABC):
    """
    Interface class, describing strategy for repetition of operations.
    """

    # region Interface Properties
    @abstractmethod
    def get_repetition_number(self, task: ICircuitOperation) -> int:
        """:return: Number of repetitions."""
        raise InterfaceMethodException
    # endregion


@dataclass(frozen=True)
class FixedRepetitionStrategy(IRepetitionStrategy):
    """
    Data class, implementing IRepetitionStrategy interface.
    Forces fixed number of repetitions.
    """
    repetitions: int = field(default=1)

    # region Interface Properties
    def get_repetition_number(self, task: ICircuitOperation) -> int:
        """:return: Number of repetitions."""
        return self.repetitions
    # endregion


@dataclass(frozen=True)
class DynamicRepetitionStrategy(IRepetitionStrategy):
    """
    Data class, implementing IRepetitionStrategy interface.
    Dynamic number of repetitions.
    """
    repetitions_call: Callable[[], int] = field(default=lambda: 1)

    # region Interface Properties
    def get_repetition_number(self, task: ICircuitOperation) -> int:
        """:return: Number of repetitions."""
        return self.repetitions_call()
    # endregion


@dataclass(frozen=True)
class RegistryRepetitionStrategy(IRepetitionStrategy):
    """
    Data class, implementing IRepetitionStrategy interface.
    """
    registry: RepetitionRegistry = field(init=True, repr=False)
    registry_key: str = field(init=True, repr=True)

    # region Class Properties
    @property
    def unique_key(self) -> str:
        """:return: Unique duration registry key."""
        return self.registry_key
    # endregion

    # region Interface Properties
    def get_repetition_number(self, task: ICircuitOperation) -> int:
        """:return: Number of repetitions."""
        return self.registry.get_registry_at(key=self.unique_key)
    # endregion
