# -------------------------------------------
# Module containing rectilinear/draw components that represent layout qubit dots.
# -------------------------------------------
from dataclasses import dataclass, field
from matplotlib import pyplot as plt, patches as patches
import numpy as np
from typing import List
from qce_circuit.visualization.intrf_draw_component import IDrawComponent
from qce_circuit.utilities.geometric_definitions import (
    IRectTransformComponent,
    TransformAlignment,
    IRectTransform,
    RectTransform,
    FixedPivot,
    FixedLength,
    Vec2D,
)
from qce_circuit.visualization.visualize_layout.style_manager import (
    StyleManager,
    ElementStyleSettings,
    ElementTextStyleSettings,
    ParkOperationStyleSettings,
)


@dataclass(frozen=True)
class DotComponent(IRectTransformComponent, IDrawComponent):
    """
    Data class, containing dimension data for drawing circle.
    """
    pivot: Vec2D
    alignment: TransformAlignment = field(default=TransformAlignment.MID_LEFT)
    style_settings: ElementStyleSettings = field(default=StyleManager.read_config().dot_style)

    # region Interface Properties
    @property
    def rectilinear_transform(self) -> IRectTransform:
        """:return: 'Hard' rectilinear transform boundary. Should be treated as 'personal zone'."""
        return RectTransform(
            _pivot_strategy=FixedPivot(self.pivot),
            _width_strategy=FixedLength(self.style_settings.element_radius),
            _height_strategy=FixedLength(self.style_settings.element_radius),
            _parent_alignment=self.alignment,
        )
    # endregion

    # region Interface Methods
    def draw(self, axes: plt.Axes) -> plt.Axes:
        """Method used for drawing component on Axes."""
        dot = patches.Circle(
            xy=self.rectilinear_transform.center_pivot.to_tuple(),
            radius=self.style_settings.element_radius,
            color=self.style_settings.background_color,
            zorder=self.style_settings.zorder,
        )
        # Apply patches
        axes.add_patch(dot)
        return axes
    # endregion


@dataclass(frozen=True)
class HexagonComponent(IRectTransformComponent, IDrawComponent):
    """
    Data class, containing dimension data for drawing circle.
    """
    pivot: Vec2D
    rotation: float = field(default=0)
    alignment: TransformAlignment = field(default=TransformAlignment.MID_LEFT)
    style_settings: ElementStyleSettings = field(default=StyleManager.read_config().hexagon_style)

    # region Interface Properties
    @property
    def rectilinear_transform(self) -> IRectTransform:
        """:return: 'Hard' rectilinear transform boundary. Should be treated as 'personal zone'."""
        return RectTransform(
            _pivot_strategy=FixedPivot(self.pivot),
            _width_strategy=FixedLength(self.style_settings.element_radius),
            _height_strategy=FixedLength(self.style_settings.element_radius),
            _parent_alignment=self.alignment,
        )
    # endregion

    # region Class Properties
    @property
    def hexagon_vertices(self) -> List[Vec2D]:
        transform: IRectTransform = self.rectilinear_transform
        angle = np.linspace(0, 2 * np.pi, 7)
        vertices: List[Vec2D] = [
            transform.pivot + Vec2D(np.cos(a), np.sin(a)) * self.style_settings.element_radius
            for a in angle
        ]
        # Apply rotation
        rotation_pivot: Vec2D = transform.pivot
        vertices = [vertex.rotate(np.deg2rad(self.rotation), rotation_pivot.to_tuple()) for vertex in vertices]
        return vertices
    # endregion

    # region Interface Methods
    def draw(self, axes: plt.Axes) -> plt.Axes:
        """Method used for drawing component on Axes."""
        dot = DotComponent(
            pivot=self.pivot,
            alignment=self.alignment,
            style_settings=StyleManager.read_config().dot_style,
        )
        hexagon = patches.Polygon(
            [vertex.to_tuple() for vertex in self.hexagon_vertices],
            closed=True,
            color=self.style_settings.background_color,
            zorder=self.style_settings.zorder,
        )
        # Apply patches
        axes.add_patch(hexagon)
        dot.draw(axes=axes)
        return axes
    # endregion


@dataclass(frozen=True)
class ParkingComponent(IRectTransformComponent, IDrawComponent):
    """
    Data class, containing dimension data for drawing circle.
    """
    pivot: Vec2D
    alignment: TransformAlignment = field(default=TransformAlignment.MID_LEFT)
    style_settings: ParkOperationStyleSettings = field(default=StyleManager.read_config().park_operation_style)

    # region Interface Properties
    @property
    def rectilinear_transform(self) -> IRectTransform:
        """:return: 'Hard' rectilinear transform boundary. Should be treated as 'personal zone'."""
        return RectTransform(
            _pivot_strategy=FixedPivot(self.pivot),
            _width_strategy=FixedLength(self.style_settings.element_radius),
            _height_strategy=FixedLength(self.style_settings.element_radius),
            _parent_alignment=self.alignment,
        )
    # endregion

    # region Interface Methods
    def draw(self, axes: plt.Axes) -> plt.Axes:
        """Method used for drawing component on Axes."""
        dot = patches.Circle(
            xy=self.rectilinear_transform.center_pivot.to_tuple(),
            radius=self.style_settings.element_radius,
            edgecolor=self.style_settings.line_color,
            linewidth=self.style_settings.line_width,
            linestyle=self.style_settings.line_style,
            fill=False,
            zorder=self.style_settings.zorder,
        )
        # Apply patches
        axes.add_patch(dot)
        return axes
    # endregion


@dataclass(frozen=True)
class TextComponent(IRectTransformComponent, IDrawComponent):
    """
    Data class, containing data for centralised-text.
    """
    pivot: Vec2D
    text: str
    color: str = field(default=StyleManager.read_config().element_text_style.font_color)
    alignment: TransformAlignment = field(default=TransformAlignment.MID_LEFT)
    style_settings: ElementTextStyleSettings = field(default=StyleManager.read_config().element_text_style)

    # region Interface Properties
    @property
    def rectilinear_transform(self) -> IRectTransform:
        """:return: 'Hard' rectilinear transform boundary. Should be treated as 'personal zone'."""
        return RectTransform(
            _pivot_strategy=FixedPivot(self.pivot),
            _width_strategy=FixedLength(self.style_settings.element_radius),
            _height_strategy=FixedLength(self.style_settings.element_radius),
            _parent_alignment=self.alignment,
        )
    # endregion

    # region Interface Methods
    def draw(self, axes: plt.Axes) -> plt.Axes:
        """Method used for drawing component on Axes."""
        transform: IRectTransform = self.rectilinear_transform
        axes.text(
            x=transform.pivot.x,
            y=transform.pivot.y,
            s=self.text,
            color=self.color,
            fontsize=self.style_settings.font_size,
            ha='center',
            va='center',
            zorder=self.style_settings.zorder,
        )
        return axes
    # endregion
