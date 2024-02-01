# -------------------------------------------
# Module containing rectilinear/draw components that represent layout plaquettes.
# -------------------------------------------
from dataclasses import dataclass, field
from enum import unique, Enum, auto
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
    PlaquetteStyleSettings,
)


@unique
class BackgroundType(Enum):
    Z = auto()
    X = auto()


@dataclass(frozen=True)
class RectanglePlaquette(IRectTransformComponent, IDrawComponent):
    """
    Data class, containing dimension data for drawing plaquette rectangle.
    """
    pivot: Vec2D
    width: float
    height: float
    background_type: BackgroundType = field(default=BackgroundType.X)
    alignment: TransformAlignment = field(default=TransformAlignment.MID_LEFT)
    style_settings: PlaquetteStyleSettings = field(default=StyleManager.read_config().plaquette_style)

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
            edgecolor='none',
            facecolor=self.style_settings.background_color,  # Depends on background type
            zorder=-1,
        )
        axes.add_patch(rectangle)
        return axes
    # endregion
