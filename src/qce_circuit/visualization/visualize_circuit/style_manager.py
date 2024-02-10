# -------------------------------------------
# Module for specific (Quantum circuit visualization) style manager
# -------------------------------------------
import os
from dataclasses import dataclass, field
from qce_circuit.utilities.singleton_base import Singleton
from qce_circuit.utilities.readwrite_yaml import (
    get_yaml_file_path,
    write_yaml,
    read_yaml,
)


@dataclass(frozen=True)
class ChannelStyleSettings:
    """
    Data class, containing channel specific style settings.
    """
    line_color: str
    text_color: str
    line_width: float
    font_size: float


@dataclass(frozen=True)
class OperationStyleSettings:
    """
    Data class, containing operation specific style settings.
    """
    border_color: str
    background_color: str
    text_color: str
    border_width: float
    line_width: float
    dot_radius: float
    font_size: float


@dataclass(frozen=True)
class IndicatorStyleSettings:
    """
    Data class, containing indicator specific style settings.
    """
    text_color: str
    arrow_color: str
    line_color: str
    line_width: float
    font_size: float


@dataclass(frozen=True)
class IconStyleSettings:
    """
    Data class, containing icon specific style settings.
    """
    icon_color: str
    icon_line_width: float


@dataclass(frozen=True)
class HighlightStyleSettings:
    """
    Data class, containing (footprint) highlight specific style settings.
    """
    text_color: str
    background_color: str
    line_color: str
    line_width: float
    font_size: float


@dataclass(frozen=True)
class StyleSettings:
    """
    Data class, describing a variety of parameter settings for stylization.
    """
    # Color schemes
    color_background: str = field(default='white')
    color_text: str = field(default='black')
    color_icon: str = field(default='black')
    color_outline: str = field(default='black')
    color_outline_dim: str = field(default='darkgrey')
    color_highlight_background: str = field(default='lightblue')
    color_highlight_outline: str = field(default='blue')

    # Widths
    width_line: float = field(default=2.0)
    width_line_small: float = field(default=1.0)
    width_line_icon: float = field(default=6.0)
    width_border: float = field(default=2.0)

    # Radius
    radius_dot: float = field(default=0.1)

    # Font sizes
    font_size: float = field(default=16.0)
    font_size_small: float = field(default=10.0)

    # region Class Properties
    @property
    def channel_style(self) -> ChannelStyleSettings:
        return ChannelStyleSettings(
            line_color=self.color_outline,
            text_color=self.color_text,
            line_width=self.width_line,
            font_size=self.font_size,
        )

    @property
    def operation_style(self) -> OperationStyleSettings:
        return OperationStyleSettings(
            border_color=self.color_outline,
            background_color=self.color_background,
            text_color=self.color_text,
            border_width=self.width_border,
            line_width=self.width_line,
            dot_radius=self.radius_dot,
            font_size=self.font_size,
        )

    @property
    def indicator_style(self) -> IndicatorStyleSettings:
        return IndicatorStyleSettings(
            text_color=self.color_text,
            arrow_color=self.color_outline,
            line_color=self.color_outline_dim,
            line_width=self.width_line,
            font_size=self.font_size_small,
        )

    @property
    def highlight_style(self) -> HighlightStyleSettings:
        return HighlightStyleSettings(
            text_color=self.color_text,
            background_color=self.color_highlight_background,
            line_color=self.color_highlight_outline,
            line_width=self.width_line,
            font_size=self.font_size_small,
        )

    @property
    def icon_style(self) -> IconStyleSettings:
        return IconStyleSettings(
            icon_color=self.color_icon,
            icon_line_width=self.width_line_icon,
        )
    # endregion


class StyleManager(metaclass=Singleton):
    """
    Behaviour Class, manages import of circuit-visualization style file.
    """
    CONFIG_NAME: str = 'config_circuit_style.yaml'

    # region Class Methods
    @classmethod
    def _default_config_object(cls) -> dict:
        """:return: Default config dict."""
        return StyleSettings().__dict__

    @classmethod
    def read_config(cls) -> StyleSettings:
        """:return: File-manager config file."""
        path = get_yaml_file_path(filename=cls.CONFIG_NAME)
        if not os.path.exists(path):
            # Construct config dict
            default_dict: dict = cls._default_config_object()
            write_yaml(
                filename=cls.CONFIG_NAME,
                packable=default_dict,
                make_file=True,
            )
        return StyleSettings(**read_yaml(filename=cls.CONFIG_NAME))
    # endregion
