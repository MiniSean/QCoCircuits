# -------------------------------------------
# Module describing interface for registries.
# -------------------------------------------
from abc import ABC, abstractmethod, ABCMeta
from typing import Generic, TypeVar
import uuid
from qce_utils.custom_exceptions import InterfaceMethodException


TRegistryKey = TypeVar('TRegistryKey')
TRegistryValue = TypeVar('TRegistryValue')


class IRegistryGetter(ABC, Generic[TRegistryKey, TRegistryValue]):
    """
    Interface Class, describing registry method access.
    """

    # region Interface Methods
    @abstractmethod
    def get_registry_at(self, key: TRegistryKey) -> TRegistryValue:
        """
        Retrieves value associated with a given key.
        :param key: The unique identifier for the registry value.
        :return: The registry value associated with the key. If the key is not found,
        a default value (e.g., None or a predefined default) can be returned.
        """
        raise InterfaceMethodException
    # endregion


class IRegistrySetter(ABC, Generic[TRegistryKey, TRegistryValue]):
    """
    Interface Class, describing registry method access.
    """

    # region Interface Methods
    @abstractmethod
    def set_registry_at(self, key: TRegistryKey, value: TRegistryValue):
        """
        Sets the value for a given key.
        :param key: The unique identifier for the registry value.
        :param value: The value to be associated with the key.
        :return: Void
        """
        raise InterfaceMethodException
    # endregion


class IRegistry(IRegistryGetter[TRegistryKey, TRegistryValue], IRegistrySetter[TRegistryKey, TRegistryValue], Generic[TRegistryKey, TRegistryValue], metaclass=ABCMeta):
    """
    Interface Class, describing registry method access.
    """

    # region Class Method
    @classmethod
    def generate_unique_key(cls) -> str:
        """
        Generates a unique key for a duration entry.
        :return: A unique key as a string.
        """
        return str(uuid.uuid4())
    # endregion
