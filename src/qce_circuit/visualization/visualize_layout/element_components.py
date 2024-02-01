# -------------------------------------------
# Module containing rectilinear/draw components that represent layout qubit dots.
# -------------------------------------------
from dataclasses import dataclass, field
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
    ElementStyleSettings,
)


@dataclass(frozen=True)
class DotComponent(IRectTransformComponent, IDrawComponent):
    """
    Data class, containing dimension data for drawing circle.
    """
    pivot: Vec2D
    alignment: TransformAlignment = field(default=TransformAlignment.MID_LEFT)
    style_settings: ElementStyleSettings = field(default=StyleManager.read_config().element_style)

    # region Interface Properties
    @property
    def rectilinear_transform(self) -> IRectTransform:
        """:return: 'Hard' rectilinear transform boundary. Should be treated as 'personal zone'."""
        return RectTransform(
            _pivot_strategy=FixedPivot(self.pivot),
            _width_strategy=FixedLength(self.style_settings.dot_radius),
            _height_strategy=FixedLength(self.style_settings.dot_radius),
            _parent_alignment=self.alignment,
        )
    # endregion

    # region Interface Methods
    def draw(self, axes: plt.Axes) -> plt.Axes:
        """Method used for drawing component on Axes."""
        dot = patches.Circle(
            xy=self.rectilinear_transform.center_pivot.to_tuple(),
            radius=self.style_settings.dot_radius,
            color=self.style_settings.background_color,
            zorder=2,
        )
        # Apply patches
        axes.add_patch(dot)
        return axes
    # endregion
