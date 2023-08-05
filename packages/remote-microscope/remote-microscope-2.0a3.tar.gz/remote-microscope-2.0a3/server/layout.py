"""mems.instrument.server.layout

Supports drawing layout diagrams on top of the microscope image.
"""

__revision__ = "$Id: layout.py,v 1.3 2003/01/02 16:19:38 akuchlin Exp $"

from PIL import ImageDraw

# XXX move module somewhere else!
from mems.mask import CIF

_cif_cache = {}

def parse_layout_file (filename):
    """parse_layout_file(filename:string) : CIFLayout

    XXX Later this should probably do caching.
    """
    layout = _cif_cache.get(filename)
    if layout is not None:
        return layout

    print 'parsing CIF file'
    cif_file = open(filename, 'r')
    cif_data = cif_file.read()
    cif_file.close()
    layout = CIF.CIFLayout() ; layout.parse(cif_data)
    _cif_cache[filename] = layout
    return layout


def draw_layout (uscope, image, filename):
    """draw_layout(image, filename) : Image
    Draw the layout on top of the image
    """
    return image
    scope_state = uscope.scope_state
    layout = parse_layout_file(filename)
    context = CIF.PILRenderingContext(image)

    w, h = uscope.get_image_size()
    context.set_scale(scope_state['x_scale'] /w,
                      scope_state['y_scale'] /h,
                      )
    context.set_translate(scope_state['x'], scope_state['y'])
    context.set_multiplier(6,6)
    context.set_multiplier(1,1)
    context.set_shift(w/2, h/2)
#    context.set_direction((1,1))
#    point = (0,0)
#    print point, context.transform_point(point)
    layout.display(context)
    return image

