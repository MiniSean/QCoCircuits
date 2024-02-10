# -------------------------------------------
# Module containing components that draw icon's or other cosmetics.
# -------------------------------------------
from dataclasses import dataclass, field
import numpy as np
from matplotlib import pyplot as plt, patches as patches
from qce_circuit.visualization.visualize_circuit.intrf_draw_component import IDrawComponent
from qce_circuit.utilities.geometric_definitions import Vec2D
from qce_circuit.visualization.visualize_circuit.style_manager import (
    StyleManager,
    IconStyleSettings,
)


@dataclass(frozen=True)
class IconMeasure(IDrawComponent):
    """
    Data class, containing dimension data for drawing icon.
    """
    center: Vec2D
    radius: float
    style_settings: IconStyleSettings = field(default=StyleManager.read_config().icon_style)

    # region Class Properties
    @property
    def circle_center(self) -> Vec2D:
        return Vec2D(x=0.0, y=0.0) + self.center

    @property
    def circle_radius(self) -> float:
        return self.radius

    @property
    def circle_thickness(self) -> float:
        return self.radius * self.style_settings.icon_line_width

    @property
    def arrow_base_radius(self) -> float:
        return self.circle_radius * 0.1

    @property
    def arrow_length(self) -> float:
        return self.circle_radius * 1.7

    @property
    def arrow_angle(self) -> float:
        return 60

    @property
    def arrow_end_vec(self) -> Vec2D:
        return Vec2D(
            x=self.circle_center.x + self.arrow_length * np.cos(np.deg2rad(self.arrow_angle)),
            y=self.circle_center.y + self.arrow_length * np.sin(np.deg2rad(self.arrow_angle)),
        )

    @property
    def arrow_thickness(self) -> float:
        return self.radius * self.style_settings.icon_line_width * 0.5

    @property
    def arrow_head_width(self) -> float:
        return self.radius * self.style_settings.icon_line_width * 2.0

    @property
    def arrow_head_length(self) -> float:
        return self.arrow_head_width * (2/3)
    # endregion

    # region Class Methods
    def draw(self, axes: plt.Axes) -> plt.Axes:
        arc = patches.Arc(
            xy=self.circle_center.to_tuple(),
            width=2 * self.radius,
            height=2 * self.radius,
            angle=0,
            theta1=0,
            theta2=180,
            edgecolor=self.style_settings.icon_color,
            facecolor='none',
            linewidth=self.circle_thickness,
        )
        arrow = patches.FancyArrowPatch(
            posA=self.circle_center.to_tuple(),
            posB=self.arrow_end_vec.to_tuple(),
            connectionstyle="arc3",
            arrowstyle=patches.ArrowStyle.Simple(
                head_length=self.arrow_head_length,
                head_width=self.arrow_head_width,
                tail_width=self.arrow_thickness,
            ),
            color=self.style_settings.icon_color,
        )
        arrow_base = patches.Circle(
            xy=self.circle_center.to_tuple(),
            radius=self.arrow_base_radius,
            color=self.style_settings.icon_color,
        )
        # Apply patches
        axes.add_patch(arc)
        axes.add_patch(arrow)
        axes.add_patch(arrow_base)
        return axes
    # endregion
