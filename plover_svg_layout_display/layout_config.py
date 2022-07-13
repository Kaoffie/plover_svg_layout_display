from typing import List, Tuple, Any


CONFIG_ITEMS = {
    "system_svg": "", 
    "system_py": "", 
    "system_scale": 100,
    "force_repaint": False
}

CONFIG_FILE_PARAMS = {
    "system_svg": ("Select Layout SVG", "Vector Graphics (*.svg)"),
    "system_py": ("Select Python Script", "Python Script (*.py)")
}

CONFIG_TYPES = {k: type(v) for k, v in CONFIG_ITEMS.items()}

CONFIG_NAMES = {
    "system_name": "Current System:",
    "system_svg": "Layout SVG",
    "system_py": "Layout Python Script",
    "system_scale": "Layout Scale",
    "force_repaint": "Force Repaint (macOS)"
}

CONFIG_ORDER = [
    "System Settings",
    "system_name",
    "system_svg",
    "system_py",
    "system_scale",

    "Force Repaint (macOS Window Shadow)",
    "force_repaint"
]


SYSTEM_NAME_PLACEHOLDER = "system_name"
SYSTEM_PREFIX = "system_"


class LayoutConfig:
    def __init__(self, system_map: dict = None, values: dict = None) -> None:
        if system_map is None:
            self.system_map = dict()
        else:
            self.system_map = system_map
        
        if values is None:
            values = dict()

        for key, default in CONFIG_ITEMS.items():
            if key in values:
                setattr(self, key, values[key])
            else:
                setattr(self, key, default)
    
    def copy(self) -> "LayoutConfig":
        value_dict = {k: getattr(self, k) for k in CONFIG_ITEMS.keys()}
        return LayoutConfig(self.system_map, value_dict)

    def get_values(self) -> List[Tuple[str, Any]]:
        results = []
        for key in CONFIG_ITEMS.keys():
            if not key.startswith(SYSTEM_PREFIX):
                results.append((key, getattr(self, key)))
        
        return results
