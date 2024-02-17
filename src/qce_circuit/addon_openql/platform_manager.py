# -------------------------------------------
# Module for managing OpenQL output directory
# -------------------------------------------
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
import openql as ql
from qce_circuit.definitions import ROOT_DIR
from qce_circuit.utilities.custom_exceptions import InvalidPointerException
from qce_circuit.utilities.singleton_base import Singleton
from qce_circuit.utilities.readwrite_yaml import (
    get_yaml_file_path,
    write_yaml,
    read_yaml,
)
from qce_circuit.utilities.readwrite_json import (
    get_json_file_path,
    write_json,
    read_json,
)


TEMP_OUTPUT_DIR: str = str(Path(os.path.join(ROOT_DIR, 'temp', 'openql_output')))
CONFIG_PLATFORM_NAME: str = 'config_openql_platform.json'
TEMP_PLATFORM_FILE_PATH: str = str(get_json_file_path(filename=CONFIG_PLATFORM_NAME))
OPENQL_LOG_LEVEL: str = 'LOG_INFO'


@dataclass(frozen=True)
class Body:
    """
    Data class, describing a variety of parameter settings for stylization.
    """
    # Color schemes
    openql_output_directory: str = field(default=TEMP_OUTPUT_DIR)
    openql_platform_file_path: str = field(default=TEMP_PLATFORM_FILE_PATH)

    # region Class Properties
    @property
    def output_directory(self) -> Path:
        result: Path = Path(self.openql_output_directory)
        os.makedirs(result, exist_ok=True)
        return result
    
    @property
    def platform_config_filepath(self) -> Path:
        result: Path = Path(self.openql_platform_file_path)
        if not os.path.exists(result):
            # Construct config dict
            default_dict: dict = PlatformManager._default_config_platform()
            write_json(
                filename=CONFIG_PLATFORM_NAME,
                packable=default_dict,
                make_file=True,
            )
        return result
    # endregion


class PlatformManager(metaclass=Singleton):
    """
    Behaviour Class, manages OpenQl output directory.
    """
    CONFIG_OUTPUT_NAME: str = 'config_openql_output.yaml'
    _openql_platform: Optional[ql.Platform] = None
    
    # region Class Methods
    @classmethod
    def openql_output_directory(cls) -> Path:
        """:return: Directory path where compiled OpenQl (program) *.qasm files are stored."""
        body = cls.read_config()
        return body.output_directory

    @classmethod
    def openql_platform_config_path(cls) -> Path:
        """:return: File path where OpenQl platform config file is stored."""
        body = cls.read_config()
        return body.platform_config_filepath
    
    @classmethod
    def openql_platform(cls) -> ql.Platform:
        platform_file_path: str = str(cls.openql_platform_config_path())
        if not os.path.exists(platform_file_path):
            raise InvalidPointerException(f"File path: {platform_file_path} does not exist. Specify existing platform file in {str(get_yaml_file_path(filename=cls.CONFIG_OUTPUT_NAME))}.")
        # Singleton platform
        if cls._openql_platform is None:
            # Set options
            ql.set_option('output_dir', str(cls.openql_output_directory()))
            ql.set_option('log_level', OPENQL_LOG_LEVEL)
            cls._openql_platform = ql.Platform('platform_name', platform_file_path)  # Temporary
        return cls._openql_platform
    
    @classmethod
    def _default_config_object(cls) -> dict:
        """:return: Default config dict."""
        return Body().__dict__

    @classmethod
    def _default_config_platform(cls) -> dict:
        """
        :return: Default (OpenQL) platform config dict.
        This dictionary contains a full description of platform/instruments/quantum chip specific instructions and specifications.
        It contains information on:
        - Compiler architecture to use (e.g. Qutech Central Controller)
        - Hardware settings (e.g. cycle time 20ns and number of qubits in quantum chip)
        - Instruction containing native instruction set to which all higher-level instructions can be compiled to.
        """
        return ql.Platform.get_platform_json()

    @classmethod
    def read_config(cls) -> Body:
        """:return: File-manager config file."""
        path = get_yaml_file_path(filename=cls.CONFIG_OUTPUT_NAME)
        if not os.path.exists(path):
            # Construct config dict
            default_dict: dict = cls._default_config_object()
            write_yaml(
                filename=cls.CONFIG_OUTPUT_NAME,
                packable=default_dict,
                make_file=True,
            )
        return Body(**read_yaml(filename=cls.CONFIG_OUTPUT_NAME))

    @classmethod
    def read_platform_config(cls) -> dict:
        """:return: OpenQL platform config file."""
        config: Body = cls.read_config()
        path = config.platform_config_filepath
        return read_json(filename=path)
    
    @classmethod
    def construct_program(cls, name: str) -> ql.Program:
        """:return: Constructed OpenQL Program based on managed platform configuration."""
        platform: ql.Platform = cls.openql_platform()
        nr_qubits: int = platform.get_qubit_number()
        return ql.Program(name, platform, nr_qubits)
    
    @classmethod
    def construct_kernel(cls, name: str) -> ql.Kernel:
        """:return: Constructed OpenQL Kernel based on managed platform configuration."""
        platform: ql.Platform = cls.openql_platform()
        nr_qubits: int = platform.get_qubit_number()
        return ql.Kernel(name, platform, nr_qubits)
    # endregion
