# -------------------------------------------
# Module describing the generic interface for factory manager.
# -------------------------------------------
from abc import ABC, ABCMeta, abstractmethod
from typing import TypeVar, Type, Generic, List
from qce_circuit.utilities.custom_exceptions import InterfaceMethodException

T = TypeVar('T', bound=Type)


class IFactoryManager(ABC, Generic[T], metaclass=ABCMeta):
    """
    Interface class, describing methods for manager factories.
    """

    # region Interface Properties
    @property
    @abstractmethod
    def supported_factories(self) -> List[T]:
        """:return: Array-like of supported factory types."""
        raise InterfaceMethodException
    # endregion

    # region Interface Methods
    @abstractmethod
    def contains(self, factory_key: T) -> bool:
        """:return: Boolean, whether factory key is included in the manager."""
        raise InterfaceMethodException
    # endregion
