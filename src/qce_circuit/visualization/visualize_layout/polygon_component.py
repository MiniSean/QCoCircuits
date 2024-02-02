# -------------------------------------------
# Module containing rectilinear/draw components that represent polygons.
# -------------------------------------------
from dataclasses import dataclass, field
from typing import List, Optional
from enum import unique, Enum, auto
import numpy as np
from matplotlib import pyplot as plt, patches as patches
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
    LineSettings,
)


@dataclass(frozen=True)
class PolylineComponent(IDrawComponent):
    """
    Data class, containing dimension data for drawing circle.
    """
    vertices: List[Vec2D]
    alignment: TransformAlignment = field(default=TransformAlignment.MID_LEFT)
    style_settings: LineSettings = field(default=StyleManager.read_config().line_style)

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
