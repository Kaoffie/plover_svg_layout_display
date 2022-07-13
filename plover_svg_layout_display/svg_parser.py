from typing import List, Dict
from lxml import etree as ET

from plover_svg_layout_display.qt_utils import load_qt_text
from plover_svg_layout_display.resources_rc import *


SVG_TEMPLATE = (
    "<svg{header}>\n{content}\n</svg>"
)


class SVGParser:
    
    __slots__ = ["group_svgs", "svg_attribs"]

    def load_file(self, path: str) -> List[str]:
        if not path.strip():
            return

        parser = ET.XMLParser(recover=True)
        svg_raw = load_qt_text(path)
        tree = ET.fromstring(svg_raw.encode("utf-8"), parser)

        self.group_svgs: Dict[str, str] = {}
        for child in tree:
            tag = child.tag
            if "}" in tag:
                tag = tag.split("}", 1)[1]

            if tag == "g" and "id" in child.attrib:
                self.group_svgs[child.attrib["id"]] = ET.tostring(child).decode()

        if "<svg" in svg_raw:
            self.svg_attribs = svg_raw.split("<svg", 1)[1].split(">")[0]


    def get_svg_content(
        self, 
        group_ids: List[str]
    ) -> str:
        content = "\n".join(
            self.group_svgs[id] 
            for id in group_ids
            if id in self.group_svgs
        )

        return SVG_TEMPLATE.format(
            header=self.svg_attribs,
            content=content
        )
    
    def get_whole_svg(self) -> str:
        return self.get_svg_content(self.group_svgs.keys())
