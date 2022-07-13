# Plover SVG Layout Display

[![PyPI](https://img.shields.io/pypi/v/plover-svg-layout-display)](https://pypi.org/project/plover-svg-layout-display/)
![GitHub](https://img.shields.io/github/license/Kaoffie/plover_svg_layout_display)

Display the last stroke in Plover, but ✨ *fancier* ✨

![svgld_1](https://user-images.githubusercontent.com/30435273/178503439-d0a2e839-0586-4c92-98bf-ba6df1727a25.png)

SVG Layout Display is based on the original [Layout Display Plugin](https://github.com/morinted/plover_layout_display) by [@morinted](https://github.com/morinted); it was designed to be more customizable than the original plugin, allowing the user to use custom shapes, and to define the behavior of these shapes using a custom script. The widget floats above other windows without a window frame, and can be configured to be translucent, which means that users have full control over how the display looks like.

## Settings

To open the settings page, focus on the display window and press `Ctrl + S` (or `Cmd + S` on mac). System settings are different for each stenographic system and will be recorded independently for each system.

## Customization

![svgld_2](https://user-images.githubusercontent.com/30435273/178503535-26bcdb13-d74b-40cf-ab64-e6c0c8e6d4dc.png)

Layouts are defined by two separate files - the svg file, which defines all the shapes and their respective positions, and the py script, which defines which shapes are drawn based on the latest stroke and translation. 

In the svg file, shapes are defined based on top-level `<g>` elements, identified by the `id` attribute. IDs should be unique between different groups, but there is no limit on the number of groups you can add in the svg file.

The python script should contain a `convert_stroke`, which takes a tuple of strokes and a translation, and outputs a list of shape IDs. The order of the IDs in the list matters, as they are drawn from the head of the list to the tail, and later shapes are drawn above earlier ones.

```py
def convert_stroke(stroke: Tuple[str, ...], translation: str) -> List[str]:
    return ...
```

Note that the `stroke` parameter is a tuple of individual keys, such as `("K-", "W-", "-U", "-P")`