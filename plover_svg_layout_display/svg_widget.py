from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtCore import QByteArray, Qt, QRect, QPoint
from PyQt5.QtSvg import QSvgWidget

from typing import List

from plover_svg_layout_display.svg_parser import SVGParser


DUMMY_PATH = ":/svgld/invalid.svg"


class LayoutWidget(QSvgWidget):

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)

        self.setObjectName("layout_widget")
        self.setContextMenuPolicy(Qt.NoContextMenu)
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("border:0px; background:transparent;")
        self.renderer().setAspectRatioMode(Qt.KeepAspectRatio)
        self.is_invalid = False
        self.svg_size = None

        self.svg_parser = SVGParser()
        
    def update_groups(self, group_ids: List[str]) -> None:
        if self.is_invalid:
            svg_str = self.svg_parser.svg_raw
        else:
            svg_str = self.svg_parser.get_svg_content(group_ids)

        self.load(QByteArray(str.encode(svg_str, "utf-8")))
        self.update()
    
    def load_invalid(self, scale: int = 100) -> None:
        self.load_svg(DUMMY_PATH, scale, True)

    def load_svg(self, path: str, scale: int, invalid: bool = False) -> None:
        if not path.strip():
            self.load_invalid(scale)
            return
        try:
            self.svg_parser.load_file(path)
            svg_str = self.svg_parser.get_whole_svg()
            self.load(QByteArray(str.encode(svg_str, "utf-8")))

            scale_ratio = scale / 100
            new_size = self.renderer().defaultSize()
            new_size.scale(
                int(new_size.width() * scale_ratio), 
                int(new_size.height() * scale_ratio), 
                Qt.KeepAspectRatio
            )
            
            self.resize(new_size)
            self.renderer().setViewBox(QRect(QPoint(0, 0), new_size))
            self.svg_size = new_size
            self.is_invalid = invalid
        except:
            self.load_invalid(scale)
