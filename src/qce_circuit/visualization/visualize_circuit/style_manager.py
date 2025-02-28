# -------------------------------------------
# Module for specific (Quantum circuit visualization) style manager
# -------------------------------------------
import os
from dataclasses import dataclass, field
import threading
from contextlib import contextmanager
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
    border_line_style: str
    dot_radius: float
    font_size: float
    subtext_font_size: float
    rectilinear_margin: float
    """Margin variable used to shrink the drawn rectangle to allow for 'white-space'."""


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

    # Line styles
    line_style_border: str = field(default='-')

    # Spacing
    rectilinear_margin: float = field(default=0.1)

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
            border_line_style=self.line_style_border,
            dot_radius=self.radius_dot,
            font_size=self.font_size,
            subtext_font_size=self.font_size_small,
            rectilinear_margin=self.rectilinear_margin,
        )

    @property
    def vacant_operation_style(self) -> OperationStyleSettings:
        return OperationStyleSettings(
            border_color=self.color_outline_dim,
            background_color='none',
            text_color=self.color_text,
            border_width=self.width_border,
            line_width=self.width_line,
            border_line_style=self.line_style_border,
            dot_radius=self.radius_dot,
            font_size=self.font_size,
            subtext_font_size=self.font_size_small,
            rectilinear_margin=self.rectilinear_margin,
        )

    @property
    def empty_operation_style(self) -> OperationStyleSettings:
        return OperationStyleSettings(
            border_color='none',
            background_color='none',
            text_color=self.color_text,
            border_width=self.width_border,
            line_width=self.width_line,
            border_line_style=self.line_style_border,
            dot_radius=self.radius_dot,
            font_size=self.font_size,
            subtext_font_size=self.font_size_small,
            rectilinear_margin=self.rectilinear_margin,
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
    _override_stack = threading.local()  # Thread-safe storage for overrides

    # region Class Methods
    @classmethod
    def _default_config_object(cls) -> dict:
        """:return: Default config dict."""
        return StyleSettings().__dict__

    @classmethod
    def read_config(cls) -> StyleSettings:
        """:return: File-manager config file or overridden settings."""
        # Check for temporary override
        if hasattr(cls._override_stack, "current_override") and cls._override_stack.current_override:
            return cls._override_stack.current_override

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

    @classmethod
    @contextmanager
    def temporary_override(cls, **overrides):
        """
        Temporarily override specific style settings in memory.
        Ensures that changes do not persist beyond the 'with' block.
        """
        try:
            # Store the original settings
            original_config = cls.read_config()
            new_config_dict = original_config.__dict__.copy()
            new_config_dict.update(overrides)  # Apply overrides

            # Set thread-local override
            cls._override_stack.current_override = StyleSettings(**new_config_dict)
            yield  # Execute block within overridden context
        finally:
            cls._override_stack.current_override = None  # Restore original settings
    # endregion
