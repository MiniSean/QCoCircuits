# -------------------------------------------
# Module containing components that are used to build channel and circuit layout.
# -------------------------------------------
from dataclasses import dataclass, field
from matplotlib import pyplot as plt
from qce_circuit.visualization.intrf_draw_component import IDrawComponent
from qce_circuit.utilities.geometric_definitions import (
    IRectTransformComponent,
    ILengthStrategy,
    IRectTransform,
    RectTransform,
    DynamicPivot,
    DynamicLength,
    TransformAlignment,
    FixedPivot,
    FixedLength,
    Vec2D,
    Line2D
)
from qce_circuit.visualization.style_manager import (
    StyleManager,
    ChannelStyleSettings,
)


def count_latex_characters(latex_str: str) -> int:
    # Set of characters to exclude from counting
    exclusions = {'$'}

    # LaTeX specific adjustments with estimated character counts
    adjustments = {
        '\\rangle': 1,
        '\\langle': 1,
        '\\phi': 1,
        '\\theta': 1,
        # Add other LaTeX commands as needed
    }

    total_count: int = 0

    # Count occurrences of adjustment keys and remove them from the string
    for key, count in adjustments.items():
        occurrences = latex_str.count(key)
        total_count += occurrences * count
        latex_str = latex_str.replace(key, '')

    # Count the remaining characters, excluding the specified characters
    for char in latex_str:
        if char not in exclusions:
            total_count += 1

    return total_count


def estimate_latex_length(latex_str: str, font_size: float) -> float:
    # Define a scaling factor and calculate the average character width
    scaling_factor: float = 0.025
    avg_char_width: float = scaling_factor * font_size

    # Get the total character count
    char_count: int = count_latex_characters(latex_str=latex_str)

    # Calculate the estimated length
    estimated_length: float = char_count * avg_char_width
    return estimated_length


@dataclass(frozen=True)
class ChannelHeader(IRectTransformComponent, IDrawComponent):
    """
    Data class, describing channel transform.
    """
    pivot: Vec2D
    height: ILengthStrategy
    channel_name: str
    state_description: str
    style_settings: ChannelStyleSettings = field(default=StyleManager.read_config().channel_style)

    # region Interface Properties
    @property
    def rectilinear_transform(self) -> IRectTransform:
        """:return: 'Hard' rectilinear transform boundary. Should be treated as 'personal zone'."""
        return RectTransform(
            _pivot_strategy=DynamicPivot(lambda: self.pivot),
            _width_strategy=DynamicLength(lambda: self.channel_name_width + self.state_description_width + 2 * self.divider_width),
            _height_strategy=self.height,
            _parent_alignment=TransformAlignment.MID_RIGHT,
        )
    # endregion

    # region Class Properties
    @property
    def divider_width(self) -> float:
        return 0.4

    @property
    def channel_name_width(self) -> float:
        return estimate_latex_length(latex_str=self.channel_name, font_size=self.style_settings.font_size)

    @property
    def state_description_width(self) -> float:
        return 0.7

    @property
    def channel_name_pivot(self) -> Vec2D:
        return self.rectilinear_transform.left_pivot

    @property
    def state_description_pivot(self) -> Vec2D:
        return Vec2D(x=0.5 * (self.center_divider.end.x + self.right_divider.start.x), y=self.rectilinear_transform.left_pivot.y)

    @property
    def center_divider(self) -> Line2D:
        start: Vec2D = self.channel_name_pivot + Vec2D(x=self.channel_name_width, y=0)
        return Line2D(
            start=start,
            end=start + Vec2D(x=self.divider_width, y=0)
        )

    @property
    def right_divider(self) -> Line2D:
        end: Vec2D = self.rectilinear_transform.right_pivot
        return Line2D(
            start=end + Vec2D(x=-self.divider_width, y=0),
            end=end,
        )
    # endregion

    # region Interface Methods
    def draw(self, axes: plt.Axes) -> plt.Axes:
        """Method used for drawing component on Axes."""
        axes.text(
            x=self.channel_name_pivot.x,
            y=self.channel_name_pivot.y,
            s=self.channel_name,
            fontsize=self.style_settings.font_size,
            color=self.style_settings.text_color,
            ha='left',
            va='center',
        )
        axes.text(
            x=self.state_description_pivot.x,
            y=self.state_description_pivot.y,
            s=self.state_description,
            fontsize=self.style_settings.font_size,
            color=self.style_settings.text_color,
            ha='center',
            va='center',
        )
        axes.plot(
            [self.center_divider.start.x, self.center_divider.end.x],
            [self.center_divider.start.y, self.center_divider.end.y],
            linestyle='-',
            linewidth=self.style_settings.line_width,
            color=self.style_settings.line_color,
        )
        axes.plot(
            [self.right_divider.start.x, self.right_divider.end.x],
            [self.right_divider.start.y, self.right_divider.end.y],
            linestyle='-',
            linewidth=self.style_settings.line_width,
            color=self.style_settings.line_color,
        )
        return axes
    # endregion


@dataclass(frozen=True)
class ChannelBar(IRectTransformComponent, IDrawComponent):
    """
    Data class, describing channel transform.
    """
    pivot: Vec2D
    width: float
    height: float
    alignment: TransformAlignment = field(init=False, default=TransformAlignment.MID_LEFT)
    style_settings: ChannelStyleSettings = field(default=StyleManager.read_config().channel_style)

    # region Class Properties
    @property
    def end_vec(self) -> Vec2D:
        return self.pivot + Vec2D(x=self.width, y=0)
    # endregion

    # region Interface Properties
    @property
    def rectilinear_transform(self) -> IRectTransform:
        """:return: 'Hard' rectilinear transform boundary. Should be treated as 'personal zone'."""
        return RectTransform(
            _pivot_strategy=FixedPivot(self.pivot),
            _width_strategy=FixedLength(self.width),
            _height_strategy=FixedLength(self.height),
            _parent_alignment=TransformAlignment.MID_LEFT,
        )
    # endregion

    # region Interface Methods
    def draw(self, axes: plt.Axes) -> plt.Axes:
        """Method used for drawing component on Axes."""
        axes.plot(
            [self.pivot.x, self.end_vec.x],
            [self.pivot.y, self.end_vec.y],
            linestyle='-',
            linewidth=self.style_settings.line_width,
            color=self.style_settings.line_color,
            zorder=-2,
        )
        return axes
    # endregion

