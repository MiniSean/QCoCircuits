# -------------------------------------------
# Module containing Singleton config manager.
# Allows for importing noise settings from config *.yaml file.
# -------------------------------------------
import os
from dataclasses import dataclass, field, asdict
from typing import Dict, List
from qce_circuit.utilities.singleton_base import Singleton
from qce_circuit.connectivity.intrf_channel_identifier import IQubitID, QubitIDObj
from qce_circuit.utilities.readwrite_yaml import (
    get_yaml_file_path,
    write_yaml,
    read_yaml,
)


@dataclass(frozen=True)
class OperationDurationParameters:
    """Data class, containing duration values [s] of operations."""
    duration_mz: float = field(default=500e-9)
    duration_cz: float = field(default=60e-9)
    duration_h: float = field(default=20e-9)
    duration_x: float = field(default=20e-9)

    # region Class Properties
    @property
    def duration_mapper(self) -> Dict[str, float]:
        return {
            'MZ': self.duration_mz,
            'CZ': self.duration_cz,
            'H': self.duration_h,
            'X': self.duration_x,
        }

    @property
    def default_duration(self) -> float:
        return 0.0
    # endregion


@dataclass(frozen=True)
class QubitNoiseModelParameters:
    """Data class, containing noise model parameters for single qubit."""
    t1: float = field(default=1e-3)
    t2: float = field(default=2e-3)
    assignment_error: float = field(default=0.0)
    single_qubit_gate_error: float = field(default=0.0)


@dataclass(frozen=True)
class NoiseSettings:
    """
    Data class, describing a variety of parameter settings for circuit-level noise.
    """
    default_t1: float = field(default=10e-6)
    default_t2: float = field(default=20e-6)
    default_assignment_error: float = field(default=0.01)
    default_single_qubit_gate_error: float = field(default=0.0)

    individual_noise: Dict[IQubitID, QubitNoiseModelParameters] = field(default_factory=dict)
    operation_durations: OperationDurationParameters = field(default_factory=OperationDurationParameters)

    # region Class Methods
    def get_default_noise_settings(self) -> QubitNoiseModelParameters:
        return QubitNoiseModelParameters(
            t1=self.default_t1,
            t2=self.default_t2,
            assignment_error=self.default_assignment_error,
            single_qubit_gate_error=self.default_single_qubit_gate_error,
        )

    def get_noise_settings(self, qubit_id: IQubitID) -> QubitNoiseModelParameters:
        if qubit_id in self.individual_noise:
            return self.individual_noise[qubit_id]
        return self.get_default_noise_settings()

    def to_dict(self):
        # Manually serialize, especially for the individual_noise dictionary
        serialized_data = {
            "default_t1": self.default_t1,
            "default_t2": self.default_t2,
            "default_assignment_error": self.default_assignment_error,
            "default_single_qubit_gate_error": self.default_single_qubit_gate_error,
            "individual_noise": {key.id: asdict(value) for key, value in self.individual_noise.items()},
            "operation_durations": asdict(self.operation_durations),
        }
        return serialized_data

    @classmethod
    def from_dict(cls, data: Dict):
        # Extract and remove the individual_noise from the input dictionary to handle it separately
        data_copy = data.copy()
        individual_noise_data = data_copy.pop("individual_noise", {})
        operation_durations_data = data_copy.pop("operation_durations", asdict(OperationDurationParameters()))
        # Reconstruct the individual_noise dictionary
        individual_noise = {QubitIDObj(key): QubitNoiseModelParameters(**value) for key, value in individual_noise_data.items()}
        operation_durations = OperationDurationParameters(**operation_durations_data)
        # Construct and return the NoiseSettings instance
        return cls(
            **data_copy,
            individual_noise=individual_noise,
            operation_durations=operation_durations,
        )
    # endregion


class NoiseSettingManager(metaclass=Singleton):
    """
    Behaviour Class, manages import of circuit-noise settings file.
    """
    CONFIG_NAME: str = 'config_circuit_noise.yaml'

    # region Class Methods
    @classmethod
    def _default_config_object(cls) -> dict:
        """:return: Default config dict."""
        return NoiseSettings().to_dict()

    @classmethod
    def read_config(cls) -> NoiseSettings:
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
        return NoiseSettings.from_dict(read_yaml(filename=cls.CONFIG_NAME))
    # endregion


@dataclass(frozen=True)
class IndexedNoiseSettings:
    """Behaviour class, containing indexed noise settings."""
    noise_settings: NoiseSettings
    qubit_index_lookup: Dict[int, IQubitID]

    # region Class Methods
    def contains(self, index: int) -> bool:
        """:return: True if contains index reference."""
        return index in self.qubit_index_lookup

    def get_noise_settings(self, index: int) -> QubitNoiseModelParameters:
        if self.contains(index):
            qubit_id: IQubitID = self.qubit_index_lookup[index]
            return self.noise_settings.get_noise_settings(qubit_id)
        return self.noise_settings.get_default_noise_settings()

    def get_operation_duration(self, identifier: str) -> float:
        duration_mapper: Dict[str, float] = self.noise_settings.operation_durations.duration_mapper
        if identifier in duration_mapper:
            return duration_mapper[identifier]
        return self.noise_settings.operation_durations.default_duration

    @classmethod
    def from_noise_manager(cls, qubit_ids: List[IQubitID]) -> 'IndexedNoiseSettings':
        return IndexedNoiseSettings(
            noise_settings=NoiseSettingManager.read_config(),
            qubit_index_lookup={
                i: qubit_id
                for i, qubit_id in enumerate(qubit_ids)
            },
        )
    # endregion
