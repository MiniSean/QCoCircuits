# -------------------------------------------
# Module containing components that represent operations.
# Usually rectangular or block components.
# -------------------------------------------
from dataclasses import dataclass, field
from enum import unique, Enum

import numpy as np
from matplotlib import pyplot as plt, patches as patches
from qce_circuit.visualization.visualize_circuit.draw_components.icon_components import IconMeasure
from qce_circuit.visualization.visualize_circuit.intrf_draw_component import IDrawComponent
from qce_circuit.utilities.geometric_definitions import (
    IRectTransformComponent,
    TransformAlignment,
    IRectTransform,
    RectTransform,
    FixedPivot,
    FixedLength,
    Vec2D,
)
from qce_circuit.visualization.visualize_circuit.style_manager import (
    StyleManager,
    OperationStyleSettings,
    ChannelStyleSettings,
)


@unique
class RotationAxis(Enum):
    X = 'X'
    Y = 'Y'
    Z = 'Z'
    PHI = r'\phi'
    X_EF = 'X12'
    Y_EF = 'Y12'
    Z_EF = 'Z12'


@unique
class RotationAngle(Enum):
    THETA = r'\theta'
    RAD90 = r'+\frac{\pi}{2}'
    RAD180 = r'+\pi'
    RAD90M = r'-\frac{\pi}{2}'
    RAD180M = r'-\pi'
    NONE = ''


@unique
class GateType(Enum):
    I = 'I'
    H = 'H'
    X = 'X'
    Y = 'Y'
    Z = 'Z'


@dataclass(frozen=True)
class RectangleBlock(IRectTransformComponent, IDrawComponent):
    """
    Data class, containing dimension data for drawing schedule block.
    """
    pivot: Vec2D
    width: float
    height: float
    alignment: TransformAlignment = field(default=TransformAlignment.MID_LEFT)
    style_settings: OperationStyleSettings = field(default=StyleManager.read_config().operation_style)

    # region Interface Properties
    @property
    def rectilinear_transform(self) -> IRectTransform:
        """:return: 'Hard' rectilinear transform boundary. Should be treated as 'personal zone'."""
        return RectTransform(
            _pivot_strategy=FixedPivot(self.pivot),
            _width_strategy=FixedLength(self.width),
            _height_strategy=FixedLength(self.height),
            _parent_alignment=self.alignment,
        )
    # endregion

    # region Class Methods
    def draw(self, axes: plt.Axes) -> plt.Axes:
        """Method used for drawing component on Axes."""
        rectangle = patches.Rectangle(
            xy=self.rectilinear_transform.origin_pivot.to_tuple(),
            width=self.rectilinear_transform.width,
            height=self.rectilinear_transform.height,
            linewidth=self.style_settings.border_width,
            edgecolor=self.style_settings.border_color,
            facecolor=self.style_settings.background_color,
            zorder=-1,
        )
        axes.add_patch(rectangle)
        return axes
    # endregion


@dataclass(frozen=True)
class RectangleTextBlock(RectangleBlock, IRectTransformComponent, IDrawComponent):
    """
    Data class, containing dimension data for drawing schedule block.
    """
    text_string: str = field(default='')

    # region Class Properties
    @property
    def text_center(self) -> Vec2D:
        return self.rectilinear_transform.center_pivot
    # endregion

    # region Class Methods
    def draw(self, axes: plt.Axes) -> plt.Axes:
        """Method used for drawing component on Axes."""
        super().draw(axes=axes)
        axes.text(
            x=self.text_center.x,
            y=self.text_center.y,
            s=self.text_string,
            fontsize=self.style_settings.font_size,
            ha='center',
            va='center',
        )
        return axes
    # endregion


@dataclass(frozen=True)
class RectangleVacantBlock(IRectTransformComponent, IDrawComponent):
    """
    Data class, containing dimension data for drawing schedule block.
    """
    pivot: Vec2D
    width: float
    height: float
    alignment: TransformAlignment = field(default=TransformAlignment.MID_LEFT)
    style_settings: OperationStyleSettings = field(default=StyleManager.read_config().vacant_operation_style)

    # region Interface Properties
    @property
    def rectilinear_transform(self) -> IRectTransform:
        """:return: 'Hard' rectilinear transform boundary. Should be treated as 'personal zone'."""
        return RectTransform(
            _pivot_strategy=FixedPivot(self.pivot),
            _width_strategy=FixedLength(self.width),
            _height_strategy=FixedLength(self.height),
            _parent_alignment=self.alignment,
        )
    # endregion

    # region Class Methods
    def draw(self, axes: plt.Axes) -> plt.Axes:
        """Method used for drawing component on Axes."""
        rectangle = patches.Rectangle(
            xy=self.rectilinear_transform.origin_pivot.to_tuple(),
            width=self.rectilinear_transform.width,
            height=self.rectilinear_transform.height,
            linewidth=self.style_settings.border_width,
            linestyle='--',
            edgecolor=self.style_settings.border_color,
            facecolor=self.style_settings.background_color,
            zorder=-1,
        )
        axes.add_patch(rectangle)
        return axes
    # endregion


@dataclass(frozen=True)
class SquareBlock(IRectTransformComponent, IDrawComponent):
    """
    Data class, containing dimension data for drawing schedule block.
    """
    pivot: Vec2D
    height: float
    alignment: TransformAlignment = field(default=TransformAlignment.MID_LEFT)
    style_settings: OperationStyleSettings = field(default=StyleManager.read_config().operation_style)
    _base_block: RectangleBlock = field(init=False)

    # region Interface Properties
    @property
    def rectilinear_transform(self) -> IRectTransform:
        """:return: 'Hard' rectilinear transform boundary. Should be treated as 'personal zone'."""
        return self._base_block.rectilinear_transform
    # endregion

    # region Class Methods
    def draw(self, axes: plt.Axes) -> plt.Axes:
        """Method used for drawing component on Axes."""
        return self._base_block.draw(axes=axes)

    def __post_init__(self):
        object.__setattr__(self, '_base_block', RectangleBlock(
            pivot=self.pivot,
            width=self.height,
            height=self.height,
            alignment=self.alignment,
            style_settings=self.style_settings,
        ))
    # endregion


@dataclass(frozen=True)
class SquareTextBlock(SquareBlock, IRectTransformComponent, IDrawComponent):
    """
    Data class, containing dimension data for drawing schedule block.
    """

    # region Class Properties
    @property
    def text_center(self) -> Vec2D:
        return self.rectilinear_transform.center_pivot
    # endregion


@dataclass(frozen=True)
class BlockMeasure(IRectTransformComponent, IDrawComponent):
    """
    Data class, containing dimension data for drawing schedule block.
    """
    pivot: Vec2D
    width: float
    height: float
    alignment: TransformAlignment = field(default=TransformAlignment.MID_LEFT)
    style_settings: OperationStyleSettings = field(default=StyleManager.read_config().operation_style)
    _base_block: RectangleBlock = field(init=False)

    # region Interface Properties
    @property
    def rectilinear_transform(self) -> IRectTransform:
        """:return: 'Hard' rectilinear transform boundary. Should be treated as 'personal zone'."""
        return self._base_block.rectilinear_transform
    # endregion

    # region Class Properties
    @property
    def icon(self) -> IconMeasure:
        icon_radius: float = self.rectilinear_transform.height * 0.4
        block_center: Vec2D = self.rectilinear_transform.center_pivot
        block_right: Vec2D = self.rectilinear_transform.center_pivot + Vec2D(x=+0.5 * self.width, y=0)
        fixed_offset: Vec2D = Vec2D(x=-0.7 * self.height, y=-0.5 * icon_radius)
        icon_center: Vec2D = Vec2D(x=max(block_right.x + fixed_offset.x, block_center.x), y=block_center.y + fixed_offset.y)
        return IconMeasure(
            center=icon_center,
            radius=icon_radius,
        )
    # endregion

    # region Class Methods
    def draw(self, axes: plt.Axes) -> plt.Axes:
        """Method used for drawing component on Axes."""
        axes = self._base_block.draw(axes=axes)
        axes = self.icon.draw(axes=axes)
        return axes

    def __post_init__(self):
        object.__setattr__(self, '_base_block', RectangleBlock(
            pivot=self.pivot,
            width=self.width,
            height=self.height,
            alignment=self.alignment,
            style_settings=self.style_settings,
        ))
    # endregion


@dataclass(frozen=True)
class BlockRotation(SquareTextBlock, IRectTransformComponent, IDrawComponent):
    """
    Data class, containing dimension data for drawing schedule block.
    """
    rotation_axes: RotationAxis = field(default=RotationAxis.PHI)
    rotation_angle: RotationAngle = field(default=RotationAngle.THETA)

    # region Class Methods
    def draw(self, axes: plt.Axes) -> plt.Axes:
        axes = self._base_block.draw(axes=axes)
        axes.text(
            x=self.text_center.x,
            y=self.text_center.y,
            s=rf'$\mathtt{{R_{{{self.rotation_axes.value}}}^{{{self.rotation_angle.value}}}}}$',
            fontsize=self.style_settings.font_size,
            ha='center',
            va='center',
        )
        return axes
    # endregion


@dataclass(frozen=True)
class BlockGate(SquareTextBlock, IRectTransformComponent, IDrawComponent):
    """
    Data class, containing dimension data for drawing schedule block.
    """
    gate_type: GateType = field(default=GateType.I)
    rotation_angle: RotationAngle = field(default=RotationAngle.NONE)

    # region Class Methods
    def draw(self, axes: plt.Axes) -> plt.Axes:
        axes = self._base_block.draw(axes=axes)
        axes.text(
            x=self.text_center.x,
            y=self.text_center.y,
            s=rf'$\mathtt{{{self.gate_type.value}^{{{self.rotation_angle.value}}}}}$',
            fontsize=self.style_settings.font_size,
            ha='center',
            va='center',
        )
        return axes
    # endregion


@dataclass(frozen=True)
class SquareParkBlock(IRectTransformComponent, IDrawComponent):
    """
    Data class, containing dimension data for drawing square (flux) parking block.
    """
    pivot: Vec2D
    height: float
    width: float
    alignment: TransformAlignment = field(default=TransformAlignment.MID_LEFT)
    style_settings: ChannelStyleSettings = field(default=StyleManager.read_config().channel_style)

    # region Interface Properties
    @property
    def rectilinear_transform(self) -> IRectTransform:
        """:return: 'Hard' rectilinear transform boundary. Should be treated as 'personal zone'."""
        return RectTransform(
            _pivot_strategy=FixedPivot(self.pivot),
            _width_strategy=FixedLength(self.width),
            _height_strategy=FixedLength(self.height),
            _parent_alignment=self.alignment,
        )
    # endregion

    # region Class Methods
    def draw(self, axes: plt.Axes) -> plt.Axes:
        """Method used for drawing component on Axes."""
        transform: IRectTransform = self.rectilinear_transform
        horizontal_extension: float = 0.1 * transform.width
        width_ratio: float = 0.8
        width: float = width_ratio * (transform.right_pivot.x - transform.left_pivot.x)
        half_width: float = 0.5 * width

        # Temporary to cover the background header bar
        cover_arc_xcoords: np.ndarray = np.asarray([
            transform.left_pivot.x,
            transform.right_pivot.x,
        ])
        cover_arc_ycoords: np.ndarray = np.asarray([
            transform.left_pivot.y,
            transform.right_pivot.y,
        ])
        axes.plot(
            cover_arc_xcoords,
            cover_arc_ycoords,
            linestyle='-',
            linewidth=self.style_settings.line_width * 2,
            color='white',  #
            zorder=-16,
        )

        # Parking line
        arc_xcoords: np.ndarray = np.asarray([
            transform.left_pivot.x - horizontal_extension,
            transform.center_pivot.x - half_width,
            transform.center_pivot.x - half_width,
            transform.center_pivot.x + half_width,
            transform.center_pivot.x + half_width,
            transform.right_pivot.x + horizontal_extension,
        ])
        arc_ycoords: np.ndarray = np.asarray([
            transform.left_pivot.y,
            transform.left_pivot.y,
            transform.bot_pivot.y,
            transform.bot_pivot.y,
            transform.right_pivot.y,
            transform.right_pivot.y,
        ])
        axes.plot(
            arc_xcoords,
            arc_ycoords,
            linestyle='-',
            linewidth=self.style_settings.line_width,
            color=self.style_settings.line_color,
            zorder=-15,
        )

        return axes
    # endregion


@dataclass(frozen=True)
class SquareNetZeroParkBlock(IRectTransformComponent, IDrawComponent):
    """
    Data class, containing dimension data for drawing (net-zero) square (flux) parking block.
    """
    pivot: Vec2D
    height: float
    width: float
    alignment: TransformAlignment = field(default=TransformAlignment.MID_LEFT)
    style_settings: ChannelStyleSettings = field(default=StyleManager.read_config().channel_style)

    # region Interface Properties
    @property
    def rectilinear_transform(self) -> IRectTransform:
        """:return: 'Hard' rectilinear transform boundary. Should be treated as 'personal zone'."""
        return RectTransform(
            _pivot_strategy=FixedPivot(self.pivot),
            _width_strategy=FixedLength(self.width),
            _height_strategy=FixedLength(self.height),
            _parent_alignment=self.alignment,
        )
    # endregion

    # region Class Methods
    def draw(self, axes: plt.Axes) -> plt.Axes:
        """Method used for drawing component on Axes."""
        transform: IRectTransform = self.rectilinear_transform
        horizontal_extension: float = 0.1 * transform.width
        width_ratio: float = 0.8
        width: float = width_ratio * (transform.right_pivot.x - transform.left_pivot.x)
        half_width: float = 0.5 * width

        # Temporary to cover the background header bar
        cover_arc_xcoords: np.ndarray = np.asarray([
            transform.left_pivot.x,
            transform.right_pivot.x,
        ])
        cover_arc_ycoords: np.ndarray = np.asarray([
            transform.left_pivot.y,
            transform.right_pivot.y,
        ])
        axes.plot(
            cover_arc_xcoords,
            cover_arc_ycoords,
            linestyle='-',
            linewidth=self.style_settings.line_width * 2,
            color='white',  #
            zorder=-16,
        )

        # Parking line
        arc_xcoords: np.ndarray = np.asarray([
            transform.left_pivot.x - horizontal_extension,
            transform.center_pivot.x - half_width,
            transform.center_pivot.x - half_width,
            transform.center_pivot.x,
            transform.center_pivot.x,
            transform.center_pivot.x + half_width,
            transform.center_pivot.x + half_width,
            transform.right_pivot.x + horizontal_extension,
        ])
        arc_ycoords: np.ndarray = np.asarray([
            transform.left_pivot.y,
            transform.left_pivot.y,
            transform.bot_pivot.y,
            transform.bot_pivot.y,
            transform.top_pivot.y,
            transform.top_pivot.y,
            transform.right_pivot.y,
            transform.right_pivot.y,
        ])
        axes.plot(
            arc_xcoords,
            arc_ycoords,
            linestyle='-',
            linewidth=self.style_settings.line_width,
            color=self.style_settings.line_color,
            zorder=-15,
        )

        return axes
    # endregion
