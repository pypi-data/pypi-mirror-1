"""mems.instrument.server.ui

Quixote-based interface for the microscope
"""

__revision__ = "$Id: __init__.py,v 1.10 2002/11/22 20:25:03 akuchlin Exp $"


from quixote import enable_ptl
enable_ptl()

from microscope import _q_access, _q_index, _q_exports
from microscope import image, handle, login, debug, save
