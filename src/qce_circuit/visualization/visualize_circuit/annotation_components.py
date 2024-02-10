# -------------------------------------------
# Module containing components that are used for annotation purposes.
# -------------------------------------------
from dataclasses import dataclass, field
from matplotlib import pyplot as plt, patches as patches
from qce_circuit.visualization.visualize_circuit.intrf_draw_component import IDrawComponent
from qce_circuit.utilities.geometric_definitions import (
    IRectTransformComponent,
    TransformAlignment,
    IRectTransform,
    RectTransform,
    FixedPivot,
    FixedLength,
    Vec2D,
    Line2D
)
from qce_circuit.visualization.visualize_circuit.style_manager import (
    StyleManager,
    IndicatorStyleSettings,
    HighlightStyleSettings,
)


@dataclass(frozen=True)
class HorizontalVariableIndicator(IRectTransformComponent, IDrawComponent):
    """
    Data class, containing dimension data for drawing horizontal variable indicator.
    """
    pivot: Vec2D
    width: float
    height: float
    alignment: TransformAlignment = field(default=TransformAlignment.MID_LEFT)
    style_settings: IndicatorStyleSettings = field(default=StyleManager.read_config().indicator_style)
    text_string: str = field(default=r'$\mathtt{{\delta}}$')

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

    # region Class Properties
    @property
    def left_border(self) -> Line2D:
        start: Vec2D = self.rectilinear_transform.left_pivot
        return Line2D(
            start=start,
            end=start + Vec2D(x=0, y=0.5 * self.rectilinear_transform.height),
        )

    @property
    def right_border(self) -> Line2D:
        start: Vec2D = self.rectilinear_transform.right_pivot
        return Line2D(
            start=start,
            end=start + Vec2D(x=0, y=0.5 * self.rectilinear_transform.height),
        )

    @property
    def arrow_line(self) -> Line2D:
        height: float = 0.4 * self.height
        return Line2D(
            start=self.rectilinear_transform.left_pivot + Vec2D(x=0, y=height),
            end=self.rectilinear_transform.right_pivot + Vec2D(x=0, y=height),
        )

    @property
    def text_center(self) -> Vec2D:
        return self.rectilinear_transform.top_pivot

    @property
    def arrow_head_width(self) -> float:
        return self.style_settings.line_width

    @property
    def arrow_head_length(self) -> float:
        return self.arrow_head_width * (2/3)
    # endregion

    # region Interface Methods
    def draw(self, axes: plt.Axes) -> plt.Axes:
        """Method used for drawing component on Axes."""
        arrow = patches.FancyArrowPatch(
            posA=self.arrow_line.start.to_tuple(),
            posB=self.arrow_line.end.to_tuple(),
            connectionstyle="arc3",
            arrowstyle=patches.ArrowStyle(
                stylename='<->',
                head_length=self.arrow_head_length,
                head_width=self.arrow_head_width,
            ),
            linewidth=self.style_settings.line_width,
            color=self.style_settings.arrow_color,
        )
        axes.plot(
            [self.left_border.start.x, self.left_border.end.x],
            [self.left_border.start.y, self.left_border.end.y],
            linestyle='--',
            linewidth=self.style_settings.line_width,
            color=self.style_settings.line_color,
            marker='none',
            zorder=-5,
        )
        axes.plot(
            [self.right_border.start.x, self.right_border.end.x],
            [self.right_border.start.y, self.right_border.end.y],
            linestyle='--',
            linewidth=self.style_settings.line_width,
            color=self.style_settings.line_color,
            marker='none',
            zorder=-5,
        )
        axes.text(
            x=self.text_center.x,
            y=self.text_center.y,
            s=self.text_string,
            fontsize=self.style_settings.font_size,
            ha='center',
            va='bottom',
            color=self.style_settings.text_color,
        )
        # Apply patches
        axes.add_patch(arrow)
        return axes
    # endregion


@dataclass(frozen=True)
class RoundedRectangleHighlight(IRectTransformComponent, IDrawComponent):
    """
    Data class, containing dimension data for drawing rounded-rectangular highlight.
    """
    pivot: Vec2D
    width: float
    height: float
    alignment: TransformAlignment = field(default=TransformAlignment.MID_LEFT)
    style_settings: HighlightStyleSettings = field(default=StyleManager.read_config().highlight_style)
    text_string: str = field(default='x1')

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

    # region Class Properties
    @property
    def text_pivot(self) -> Vec2D:
        return self.rectilinear_transform.origin_opposite_pivot + Vec2D(x=-self.rectilinear_transform.width, y=0)
    # endregion

    # region Interface Methods
    def draw(self, axes: plt.Axes) -> plt.Axes:
        """Method used for drawing component on Axes."""
        box_style: str = "round,pad=0.02,rounding_size=0.3"
        rounded_rectangle = patches.FancyBboxPatch(
            xy=self.rectilinear_transform.origin_pivot.to_tuple(),
            width=self.rectilinear_transform.width,
            height=self.rectilinear_transform.height,
            boxstyle=box_style,
            linestyle='none',
            facecolor=self.style_settings.background_color,
            zorder=-20,
        )
        rounded_rectangle_border = patches.FancyBboxPatch(
            xy=self.rectilinear_transform.origin_pivot.to_tuple(),
            width=self.rectilinear_transform.width,
            height=self.rectilinear_transform.height,
            boxstyle=box_style,
            linestyle='--',
            linewidth=self.style_settings.line_width,
            edgecolor=self.style_settings.line_color,
            facecolor='none',
            zorder=-19,
        )
        axes.text(
            x=self.text_pivot.x,
            y=self.text_pivot.y,
            s=self.text_string,
            fontsize=self.style_settings.font_size,
            fontweight='bold',
            ha='left',
            va='bottom',
            color=self.style_settings.line_color,
        )
        # Apply patches
        axes.add_patch(rounded_rectangle)
        axes.add_patch(rounded_rectangle_border)
        return axes
    # endregion
