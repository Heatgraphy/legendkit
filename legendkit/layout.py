from functools import partial
from typing import List, Optional, Dict

from matplotlib.artist import Artist
from matplotlib.legend import Legend
from matplotlib.offsetbox import VPacker, HPacker, AnchoredOffsetbox, TextArea
from matplotlib.patches import FancyBboxPatch

from ._colorart import ColorArt
from ._locs import Locs


def _create_children(artists: List[Artist]):
    children = []
    for art in artists:
        if isinstance(art, Legend):
            c1, c2 = art.get_children()
            if isinstance(c1, FancyBboxPatch):
                children.append(c2)
            else:
                children.append(c1)
        elif isinstance(art, AnchoredOffsetbox):
            children += art.get_children()
        elif isinstance(art, ColorArt):
            children += art.get_children().get_children()
        elif isinstance(art, Artist):
            children.append(art)
        else:
            raise TypeError(f"Cannot parse object {str(art)} with type {type(art)}")
        try:
            # remove artist from the canvas to avoid rendering overlay
            art.remove()
        except Exception:
            pass
    return children


def stack(legends,
          ax=None,
          orientation: str = "vertical",
          spacing=2,
          padding=2,
          align="baseline",
          mode="fixed",
          loc="lower left",
          frameon=False,
          bbox_to_anchor=None,
          bbox_transform=None,
          deviation=0.05,
          title: str = None,
          title_loc: str = "top",
          alignment: str = "center",
          title_fontproperties: Dict = None
          ):
    """

    Parameters
    ----------
    legends
    ax
    orientation
    spacing
    padding
    align
    mode
    loc
    frameon
    bbox_to_anchor
    bbox_transform
    deviation
    title
    title_loc
    alignment
    title_fontproperties

    Returns
    -------

    """
    children = _create_children(legends)
    # Call different layout helper depends on orientation
    if orientation == "vertical":
        packer = VPacker
    else:
        packer = HPacker
    vpack = packer(pad=0,
                   sep=spacing,
                   align=align,
                   mode=mode,
                   children=children
                   )
    if title is not None:
        if title_fontproperties is None:
            title_fontproperties = {'weight': 600}
        title_box = TextArea(title, textprops=title_fontproperties)
        content = [title_box, vpack]
        if title_loc == "top":
            vpack = VPacker(pad=0, sep=spacing / 2, align=alignment, mode=mode, children=content)
    # If user supply the ax
    # The legend box will be rendered on the axes
    # So user don't have to call ax.add_artist()
    if ax is not None:
        loc, bbox_to_anchor, bbox_transform = \
            Locs().transform(ax, loc, bbox_to_anchor=bbox_to_anchor,
                             bbox_transform=bbox_transform,
                             deviation=deviation)
    legend_box = AnchoredOffsetbox(child=vpack,
                                   loc=loc,
                                   pad=padding,
                                   borderpad=0,
                                   prop=None,
                                   frameon=frameon,
                                   bbox_to_anchor=bbox_to_anchor,
                                   bbox_transform=bbox_transform, )
    if ax is not None:
        ax.add_artist(legend_box)
    return legend_box


# Create two helper function
vstack = partial(stack, orientation="vertical")
hstack = partial(stack, orientation="horizontal")
