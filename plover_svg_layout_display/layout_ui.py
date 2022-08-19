from typing import Any, Callable, Tuple, Union

from plover import system
from plover.engine import StenoEngine
from plover.oslayer.config import PLUGINS_PLATFORM
from plover.gui_qt.tool import Tool
from plover.steno import Stroke

from PyQt5.QtWidgets import QAction, QHBoxLayout, QGraphicsView
from PyQt5.QtGui import QKeySequence, QMouseEvent, QColor
from PyQt5.QtCore import Qt, QRect, QSettings

from plover_svg_layout_display.resources_rc import *
from plover_svg_layout_display.config_ui import ConfigUI
from plover_svg_layout_display.layout_config import CONFIG_ITEMS, CONFIG_TYPES, SYSTEM_PREFIX, LayoutConfig
from plover_svg_layout_display.svg_widget import LayoutWidget
from plover_svg_layout_display.qt_utils import load_qt_text



STYLESHEET = "border:0px; background:transparent;"
DEFAULT_SVG = ":/svgld/en_layout.svg"
DEFAULT_SCALE = 100
DEFAULT_PY = ":/svgld/en_convert.py"


class SVGLayoutDisplayTool(Tool):
    TITLE = "SVG Layout Display"
    ICON = ":/svgld/icon.svg"
    ROLE = "svgld"

    def __init__(self, engine: StenoEngine) -> None:
        super().__init__(engine)
        self.setObjectName("svgld")
        engine.signal_connect("stroked", self.on_stroke)
        engine.signal_connect("config_changed", self.on_config_changed)

        self.system_name = system.NAME
        self.repaint_offset = False
        self.convert_stroke = None

        self.config = LayoutConfig()
        self.restore_state()
        self.setup_actions()
        self.setup_trans()
        self.setup_layout()
        self.reload_config()

        self.finished.connect(self.save_state)

    def _restore_state(self, settings: QSettings) -> None:
        # Cross system settings
        for field_name in CONFIG_ITEMS.keys():
            if settings.contains(field_name) and not field_name.startswith(SYSTEM_PREFIX):
                setattr(
                    self.config, 
                    field_name, 
                    settings.value(field_name, type=CONFIG_TYPES[field_name])
                )

            elif (
                field_name == "force_repaint"
                and PLUGINS_PLATFORM is not None and PLUGINS_PLATFORM == "mac"
            ):
                self.config.force_repaint = True
        
        # System specific settings
        for field_name in settings.allKeys():
            if "/" in field_name:
                sys_name, sys_field = field_name.split("/", 1)
                if sys_field in CONFIG_ITEMS.keys():
                    if sys_name not in self.config.system_map:
                        self.config.system_map[sys_name] = dict()
                    
                    self.config.system_map[sys_name][sys_field] = settings.value(
                        field_name,
                        type=CONFIG_TYPES[sys_field]
                    )

    def _save_state(self, settings: QSettings) -> None:
        for key, value in self.config.get_values():
            settings.setValue(key, value)
        
        for sys_name, sys_map in self.config.system_map.items():
            for key, value in sys_map.items():
                settings.setValue(sys_name + "/" + key, value)
    
    def view_mouse_move(self, event: QMouseEvent) -> None:
        if event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)

    def view_mouse_press(self, event: QMouseEvent) -> None:
        if event.buttons() & Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
    
    def setup_actions(self) -> None:
        self.close_action = QAction(self)
        self.close_action.setText("Close Display")
        self.close_action.triggered.connect(self.accept)
        self.close_action.setShortcut(QKeySequence("Ctrl+X"))
        self.addAction(self.close_action)

        self.settings_action = QAction(self)
        self.settings_action.setText("Configure Display")
        self.settings_action.triggered.connect(self.on_settings)
        self.settings_action.setShortcut(QKeySequence("Ctrl+S"))
        self.addAction(self.settings_action)
    
    def on_stroke(self, stroke: Union[Stroke, Tuple[str, ...]]) -> None:
        if isinstance(stroke, Stroke):
            stroke_tup = tuple(stroke.steno_keys)
        else:
            stroke_tup = stroke

        if self.convert_stroke is not None:
            prev_translations = self._engine.translator_state.prev()
            if not prev_translations:
                output = ""
            else:
                output = prev_translations[-1].english

            group_ids = self.convert_stroke(stroke_tup, output)
            self.svg_widget.update_groups(group_ids)

        self.repaint()

    def setup_trans(self) -> None:
        # For some strange reason, even though this piece of code doesn't
        # actually draw anything, the widget refuses to be transparent on
        # some systems unless this is included.
        self.trans_view = QGraphicsView(self)
        self.trans_view.setStyleSheet(STYLESHEET)

    def setup_layout(self) -> None:
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("QWidget#svgld {background:transparent;}")

        self.svg_widget = LayoutWidget()

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.svg_widget)
        self.setLayout(self.layout)

        self.mouseMoveEvent = self.view_mouse_move
        self.mousePressEvent = self.view_mouse_press

        self.show()

    def on_config_changed(self, config: dict) -> None:
        if "system_name" not in config:
            return
        
        new_sys_name = config["system_name"]
        if new_sys_name == self.system_name:
            return
 
        self.reload_config()
    
    def on_settings(self) -> None:
        config_dialog = ConfigUI(self.config.copy(), self.system_name, self)
        if config_dialog.exec():
            self.config = config_dialog.temp_config
            self.reload_config()
    
    def load_py_script(self, py_path: str) -> None:
        py_text = load_qt_text(py_path)

        if not py_text.strip():
            self.convert_stroke = None
            return

        try:
            globs = {}
            exec(py_text, globs)

            convert_stroke = globs.get("convert_stroke")
            if not isinstance(convert_stroke, Callable):
                self.convert_stroke = None
            
            self.convert_stroke = convert_stroke

        except:
            self.convert_stroke = None

    def reload_config(self) -> None:
        if self.system_name in self.config.system_map:
            sys_config = self.config.system_map[self.system_name]
            if "system_svg" in sys_config:
                svg_path = sys_config["system_svg"]
                self.svg_widget.load_svg(
                    svg_path, 
                    sys_config.get("system_scale", 100)
                )

            if "system_py" in sys_config:
                py_path = sys_config["system_py"]
                self.load_py_script(py_path)
                
        elif self.system_name == "English Stenotype":
            self.svg_widget.load_svg(DEFAULT_SVG, DEFAULT_SCALE)
            self.load_py_script(DEFAULT_PY)
        
        self.on_stroke(tuple())

    def repaint_rect(self) -> QRect:
        window_rect = self.rect()
        if self.repaint_offset:
            window_rect.setWidth(window_rect.width() - 1)
        
        return window_rect

    def repaint(self) -> None:
        self.repaint_offset = not self.repaint_offset
        svg_size = self.svg_widget.svg_size

        if svg_size is not None:
            right_margin_px = 1 * self.config.force_repaint * self.repaint_offset
            self.layout.setContentsMargins(0, 0, right_margin_px, 0)
            self.setFixedWidth(svg_size.width() + right_margin_px)
            self.setFixedHeight(svg_size.height())

    # def repaint(self) -> None:
    #     self.repaint_offset = not self.repaint_offset
    #     self.setFixedWidth(self.width + self.repaint_offset * self.config.force_repaint_px)
        
