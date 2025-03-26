# -------------------------------------------
# Module containing rectilinear/draw components that represent polygons.
# -------------------------------------------
from dataclasses import dataclass, field
from typing import List
from matplotlib import pyplot as plt, patches as patches
from qce_circuit.visualization.visualize_circuit.intrf_draw_component import IDrawComponent
from qce_circuit.utilities.geometric_definitions import (
    TransformAlignment,
    IRectTransform,
    RectTransform,
    FixedPivot,
    FixedLength,
    Vec2D,
)
from qce_circuit.visualization.visualize_layout.style_manager import (
    StyleManager,
    LineSettings,
    GateOperationStyleSettings,
)


@dataclass(frozen=True)
class PolylineComponent(IDrawComponent):
    """
    Data class, containing dimension data for drawing circle.
    """
    vertices: List[Vec2D]
    alignment: TransformAlignment = field(default=TransformAlignment.MID_LEFT)
    style_settings: LineSettings = field(default_factory=lambda: StyleManager.read_config().line_style)

    # region Interface Methods
    def draw(self, axes: plt.Axes) -> plt.Axes:
        """Method used for drawing component on Axes."""
        polygon = patches.Polygon(
            [vertex.to_tuple() for vertex in self.vertices],
            closed=False,
            fill=False,
            color=self.style_settings.line_color,
            linewidth=self.style_settings.line_width,
            zorder=self.style_settings.zorder,
        )
        # Apply patches
        axes.add_patch(polygon)
        return axes
    # endregion


@dataclass(frozen=True)
class GateOperationComponent(IDrawComponent):
    """
    Data class, containing dimension data for drawing circle.
    """
    pivot0: Vec2D
    pivot1: Vec2D
    alignment: TransformAlignment = field(default=TransformAlignment.MID_LEFT)
    style_settings: GateOperationStyleSettings = field(default_factory=lambda: StyleManager.read_config().gate_operation_style)

    # region Class Properties
    @property
    def vertices(self) -> List[Vec2D]:
        return [self.pivot0, self.pivot1]
    # endregion

    # region Interface Methods
    def draw(self, axes: plt.Axes) -> plt.Axes:
        """Method used for drawing component on Axes."""
        transform0: IRectTransform = RectTransform(
            _pivot_strategy=FixedPivot(self.pivot0),
            _width_strategy=FixedLength(self.style_settings.dot_settings.element_radius),
            _height_strategy=FixedLength(self.style_settings.dot_settings.element_radius),
            _parent_alignment=self.alignment,
        )
        transform1: IRectTransform = RectTransform(
            _pivot_strategy=FixedPivot(self.pivot1),
            _width_strategy=FixedLength(self.style_settings.dot_settings.element_radius),
            _height_strategy=FixedLength(self.style_settings.dot_settings.element_radius),
            _parent_alignment=self.alignment,
        )

        polygon = patches.Polygon(
            [vertex.to_tuple() for vertex in self.vertices],
            closed=False,
            fill=False,
            color=self.style_settings.line_settings.line_color,
            linewidth=self.style_settings.line_settings.line_width,
            zorder=self.style_settings.line_settings.zorder,
        )
        dot0 = patches.Circle(
            xy=transform0.center_pivot.to_tuple(),
            radius=self.style_settings.dot_settings.element_radius,
            color=self.style_settings.dot_settings.line_color,
            fill=True,
            zorder=self.style_settings.dot_settings.zorder,
        )
        dot1 = patches.Circle(
            xy=transform1.center_pivot.to_tuple(),
            radius=self.style_settings.dot_settings.element_radius,
            color=self.style_settings.dot_settings.line_color,
            fill=True,
            zorder=self.style_settings.dot_settings.zorder,
        )
        # Apply patches
        axes.add_patch(polygon)
        axes.add_patch(dot0)
        axes.add_patch(dot1)
        return axes
    # endregion
