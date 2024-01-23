# -------------------------------------------
# Module containing interface and implementation of a rectilinear transform system.
# -------------------------------------------
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import unique, Enum, auto
from typing import Callable
from qce_circuit.utilities.custom_exceptions import InterfaceMethodException
from qce_circuit.utilities.geometric_definitions.vector_elements import Vec2D


@unique
class TransformAlignment(Enum):
    TOP_LEFT = auto()
    TOP_CENTER = auto()
    TOP_RIGHT = auto()
    MID_LEFT = auto()
    MID_CENTER = auto()
    MID_RIGHT = auto()
    BOT_LEFT = auto()
    BOT_CENTER = auto()
    BOT_RIGHT = auto()


class IRectTransform(ABC):
    """
    Interface class, describing rectilinear transform.
    """

    # region Interface Properties
    @property
    @abstractmethod
    def pivot(self) -> Vec2D:
        """:return: Self pivot."""
        raise InterfaceMethodException

    @property
    @abstractmethod
    def width(self) -> float:
        """:return: Self width."""
        raise InterfaceMethodException

    @property
    @abstractmethod
    def height(self) -> float:
        """:return: Self height."""
        raise InterfaceMethodException

    @property
    @abstractmethod
    def parent_alignment(self) -> TransformAlignment:
        """:return: Alignment style for self with respect to parent."""
        raise InterfaceMethodException

    @property
    def center_pivot(self) -> Vec2D:
        """:return: Mid-Center pivot point."""
        # Data allocation
        self_pivot: Vec2D = self.pivot
        x: float = self_pivot.x
        y: float = self_pivot.y
        # Determine center based on (parent) alignment
        if self.parent_alignment in [TransformAlignment.BOT_LEFT, TransformAlignment.MID_LEFT, TransformAlignment.TOP_LEFT]:
            x = self_pivot.x + 0.5 * self.width
        if self.parent_alignment in [TransformAlignment.BOT_RIGHT, TransformAlignment.MID_RIGHT, TransformAlignment.TOP_RIGHT]:
            x = self_pivot.x - 0.5 * self.width
        if self.parent_alignment in [TransformAlignment.BOT_LEFT, TransformAlignment.BOT_CENTER, TransformAlignment.BOT_RIGHT]:
            y = self_pivot.y + 0.5 * self.height
        if self.parent_alignment in [TransformAlignment.TOP_LEFT, TransformAlignment.TOP_CENTER, TransformAlignment.TOP_RIGHT]:
            y = self_pivot.y - 0.5 * self.height
        return Vec2D(x=x, y=y)

    @property
    def left_pivot(self):
        """:return: Mid-Left pivot point."""
        return self.center_pivot + Vec2D(x=-0.5 * self.width, y=0)

    @property
    def right_pivot(self):
        """:return: Mid-Right pivot point."""
        return self.center_pivot + Vec2D(x=+0.5 * self.width, y=0)

    @property
    def top_pivot(self):
        """:return: Top-Center pivot point."""
        return self.center_pivot + Vec2D(x=0, y=+0.5 * self.height)

    @property
    def bot_pivot(self):
        """:return: Bot-Center pivot point."""
        return self.center_pivot + Vec2D(x=0, y=-0.5 * self.height)

    @property
    def origin_pivot(self):
        """:return: Pivot point 0,0 (bottom left)."""
        return Vec2D(x=self.left_pivot.x, y=self.bot_pivot.y)

    @property
    def origin_opposite_pivot(self):
        """:return: Pivot point 1,1 (top right)."""
        return Vec2D(x=self.right_pivot.x, y=self.top_pivot.y)
    # endregion

    # region Interface Methods
    @abstractmethod
    def get_relative_dynamic_pivot(self, relative_x: float, relative_y: float) -> 'IPivotStrategy':
        """
        Constructs pivot strategy based on self (IRectTransform) and relative coordinates.
        Note: (0, 0) is bot-left, (1, 1) is top-right. This follows Matplotlib convention.
        :param relative_x: Normalized x-coordinate [0, 1].
        :param relative_y: Normalized y-coordinate [0, 1].
        :return: (Dynamic) pivot strategy.
        """
        raise InterfaceMethodException

    @abstractmethod
    def update_transform_pivot(self, pivot_strategy: 'IPivotStrategy') -> 'IRectTransform':
        """:return: transform after updating its pivot."""
        raise InterfaceMethodException
    # endregion


class IPivotStrategy(ABC):
    """
    Interface class, describing strategy for obtaining pivot information.
    """

    # region Interface Properties
    @abstractmethod
    def get_pivot(self, transform: IRectTransform) -> Vec2D:
        """:return: Pivot point (2D)."""
        raise InterfaceMethodException
    # endregion


@dataclass(frozen=True)
class FixedPivot(IPivotStrategy):
    _pivot: Vec2D

    # region Interface Properties
    def get_pivot(self, transform: IRectTransform) -> Vec2D:
        """:return: Pivot point (2D)."""
        return self._pivot
    # endregion


@dataclass(frozen=True)
class DynamicPivot(IPivotStrategy):
    _pivot_call: Callable[[], Vec2D]

    # region Interface Properties
    def get_pivot(self, transform: IRectTransform) -> Vec2D:
        """:return: Pivot point (2D)."""
        return self._pivot_call()
    # endregion


class ILengthStrategy(ABC):
    """
    Interface class, describing strategy for obtaining length (width or height) information.
    """
    _length: float

    # region Interface Properties
    @abstractmethod
    def get_length(self, transform: IRectTransform) -> float:
        """:return: Length (1D)."""
        raise InterfaceMethodException
    # endregion


@dataclass(frozen=True)
class FixedLength(ILengthStrategy):
    _length: float

    # region Interface Properties
    def get_length(self, transform: IRectTransform) -> float:
        """:return: Length (1D)."""
        return self._length
    # endregion


@dataclass(frozen=True)
class DynamicLength(ILengthStrategy):
    _length_call: Callable[[], float]

    # region Interface Properties
    def get_length(self, transform: IRectTransform) -> float:
        """:return: Length (1D)."""
        return self._length_call()
    # endregion


@dataclass(frozen=False)
class RectTransform(IRectTransform):
    """
    Data class, implementing IRectTransform interface.
    """
    _pivot_strategy: IPivotStrategy
    _width_strategy: ILengthStrategy
    _height_strategy: ILengthStrategy
    _parent_alignment: TransformAlignment = field(default=TransformAlignment.MID_CENTER)

    # region Interface Properties
    @property
    def pivot(self) -> Vec2D:
        """:return: Self pivot."""
        return self._pivot_strategy.get_pivot(self)

    @property
    def width(self) -> float:
        """:return: Self width."""
        return self._width_strategy.get_length(self)

    @property
    def height(self) -> float:
        """:return: Self height."""
        return self._height_strategy.get_length(self)

    @property
    def parent_alignment(self) -> TransformAlignment:
        """:return: Alignment style for self with respect to parent."""
        return self._parent_alignment
    # endregion

    # region Interface Methods
    def get_relative_dynamic_pivot(self, normalized_x: float, normalized_y: float) -> DynamicPivot:
        """
        Constructs pivot strategy based on self (IRectTransform) and relative coordinates.
        Note: (0, 0) is bot-left, (1, 1) is top-right. This follows Matplotlib convention.
        :param normalized_x: Normalized x-coordinate [0, 1].
        :param normalized_y: Normalized y-coordinate [0, 1].
        :return: (Dynamic) pivot strategy.
        """
        return DynamicPivot(
            _pivot_call=lambda: self.origin_pivot + Vec2D(x=normalized_x * self.width, y=normalized_y * self.height)
        )

    def update_transform_pivot(self, pivot_strategy: IPivotStrategy) -> 'RectTransform':
        """:return: transform after updating its pivot."""
        self._pivot_strategy = pivot_strategy
        return self
    # endregion


class IRectTransformComponent(ABC):

    # region Interface Properties
    @property
    @abstractmethod
    def rectilinear_transform(self) -> IRectTransform:
        """:return: 'Hard' rectilinear transform boundary. Should be treated as 'personal zone'."""
        raise InterfaceMethodException
    # endregion
