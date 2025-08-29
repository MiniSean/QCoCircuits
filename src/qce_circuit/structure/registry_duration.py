# -------------------------------------------
# Module describing duration (strategy) registry.
# A registry can be used to manage and access the variable durations.
# -------------------------------------------
import os
import contextlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Callable, Optional
from enum import Enum, unique
from qce_circuit.utilities.singleton_base import Singleton
from qce_circuit.utilities.custom_exceptions import InterfaceMethodException
from qce_circuit.utilities.readwrite_yaml import (
    get_yaml_file_path,
    write_yaml,
    read_yaml,
)
from qce_circuit.structure.intrf_registry import (
    IRegistry,
    IRegistryGetter,
)
from qce_circuit.structure.intrf_circuit_operation import ICircuitOperation


TRegistryKey = str


@unique
class GlobalRegistryKey(Enum):
    READOUT = 'default_allocated_readout_duration'
    MICROWAVE = 'default_allocated_microwave_duration'
    FLUX = 'default_allocated_flux_duration'
    RESET = 'default_allocated_reset_duration'
    QEC_BLOCK = 'default_allocated_qec_duration'
    BARRIER = 'default_allocated_barrier_duration'


@dataclass(frozen=True)
class GlobalDurationRegistry(IRegistryGetter[GlobalRegistryKey, float]):
    """
    Behaviour class, describing a global singleton registry.
    """
    _global_registry: Dict[str, float] = field(default_factory=lambda: {
        GlobalRegistryKey.READOUT.value: 2.0,
        GlobalRegistryKey.MICROWAVE.value: 1.0,
        GlobalRegistryKey.FLUX.value: 1.0,
        GlobalRegistryKey.RESET.value: 2.0,
        GlobalRegistryKey.QEC_BLOCK.value: 2.0,
        GlobalRegistryKey.BARRIER.value: 0.5,
    })

    # region Class Methods
    def get_registry_at(self, key: GlobalRegistryKey) -> Optional[float]:
        """
        Retrieves the duration associated with a given key.
        :param key: The unique identifier for the duration.
        :return: The duration value associated with the key. If the key is not found,
        a default value (e.g., None or a predefined default) can be returned.
        """
        return self._global_registry.get(key.value, None)
    # endregion


class GlobalDurationRegistryManager(metaclass=Singleton):
    """
    Behaviour Class, manages import of circuit-visualization style file.
    """
    CONFIG_NAME: str = 'config_default_operation_durations.yaml'

    # region Class Methods
    @classmethod
    def _default_config_object(cls) -> dict:
        """:return: Default config dict."""
        return GlobalDurationRegistry().__dict__

    @classmethod
    def read_config(cls) -> GlobalDurationRegistry:
        """:return: File-manager config file."""
        path = get_yaml_file_path(filename=cls.CONFIG_NAME)
        if not os.path.exists(path):
            # Construct config dict
            default_dict: dict = cls._default_config_object()
            write_yaml(
                filename=cls.CONFIG_NAME,
                packable=default_dict,
                make_file=True,
            )
        return GlobalDurationRegistry(**read_yaml(filename=cls.CONFIG_NAME))
    # endregion


@contextlib.contextmanager
def temporary_override_get_registry_at(temp_registry: Dict[GlobalRegistryKey, float]):
    """
    Context manager to temporarily override the get_registry_at method of
    GlobalDurationRegistry to use a predefined GlobalDurationRegistry instance.
    :param temp_registry:  (GlobalDurationRegistry) The temporary GlobalDurationRegistry instance to return.
    :yields: None
    """
    original_method = GlobalDurationRegistry.get_registry_at

    def temp_get_registry_at(self, key: GlobalRegistryKey) -> Optional[float]:
        extended_lookup: Dict[str, float] = GlobalDurationRegistry()._global_registry
        # Update
        for _key, _value in temp_registry.items():
            extended_lookup[_key.value] = _value

        return extended_lookup.get(key.value, None)

    try:
        GlobalDurationRegistry.get_registry_at = temp_get_registry_at
        yield
    finally:
        GlobalDurationRegistry.get_registry_at = original_method


class DurationRegistry(IRegistry[TRegistryKey, float]):
    """
    Behaviour class, containing registry for setting and getting operation duration values.
    The registry is intended to be linked with (variable) duration strategies.
    """

    # region Class Constructor
    def __init__(self):
        """
        Initializes the DurationRegistry with an empty dictionary for storing durations.
        """
        self._variable_durations: Dict[TRegistryKey, float] = {}
        self._default_duration: float = 0.0
    # endregion

    # region Class Methods
    def set_registry_at(self, key: TRegistryKey, value: float) -> None:
        """
        Sets the duration for a given key.
        :param key: The unique identifier for the duration.
        :param value: The duration value to be associated with the key.
        """
        self._variable_durations[key] = value

    def get_registry_at(self, key: TRegistryKey) -> float:
        """
        Retrieves the duration associated with a given key.
        :param key: The unique identifier for the duration.
        :return: The duration value associated with the key. If the key is not found,
        a default value (e.g., None or a predefined default) can be returned.
        """
        return self._variable_durations.get(key, self._default_duration)
    # endregion


class IDurationStrategy(ABC):
    """
    Interface class, describing strategy for exposing variable duration object.
    """

    # region Interface Properties
    @abstractmethod
    def get_variable_duration(self, task: ICircuitOperation) -> float:
        """:return: Duration [ns]."""
        raise InterfaceMethodException
    # endregion


@dataclass(frozen=True)
class RegistryDurationStrategy(IDurationStrategy):
    """
    Data class, implementing IDurationStrategy interface.
    Forces fixed duration.
    """
    registry: DurationRegistry = field(init=True, repr=False)
    registry_key: TRegistryKey = field(init=True, repr=True)

    # region Class Properties
    @property
    def unique_key(self) -> TRegistryKey:
        """:return: Unique duration registry key."""
        return self.registry_key
    # endregion

    # region Interface Properties
    def get_variable_duration(self, task: ICircuitOperation) -> float:
        """:return: Duration [ns]."""
        return self.registry.get_registry_at(key=self.unique_key)
    # endregion


@dataclass(frozen=True)
class GlobalDurationStrategy(IDurationStrategy):
    """
    Data class, implementing IDurationStrategy interface.
    Links strategy to global (operation) duration registry.
    """
    key: GlobalRegistryKey = field(compare=True, repr=True)
    """Registry key corresponding to the (operation) type that implements this duration strategy."""
    _registry: GlobalDurationRegistry = field(default_factory=GlobalDurationRegistryManager.read_config, compare=False, repr=False)

    # region Interface Properties
    def get_variable_duration(self, task: ICircuitOperation) -> float:
        """:return: Duration [ns]."""
        return self._registry.get_registry_at(key=self.key)
    # endregion


@dataclass(frozen=True)
class FixedDurationStrategy(IDurationStrategy):
    """
    Data class, implementing IDurationStrategy interface.
    Forces fixed duration.
    """
    duration: float = field(default=0.0)

    # region Interface Properties
    def get_variable_duration(self, task: ICircuitOperation) -> float:
        """:return: Duration [ns]."""
        return self.duration
    # endregion


@dataclass(frozen=True)
class DynamicDurationStrategy(IDurationStrategy):
    """
    Data class, implementing IDurationStrategy interface.
    Forces fixed duration.
    """
    duration_call: Callable[[], float] = field(default=lambda: 0.0)

    # region Interface Properties
    def get_variable_duration(self, task: ICircuitOperation) -> float:
        """:return: Duration [ns]."""
        return self.duration_call()
    # endregion
