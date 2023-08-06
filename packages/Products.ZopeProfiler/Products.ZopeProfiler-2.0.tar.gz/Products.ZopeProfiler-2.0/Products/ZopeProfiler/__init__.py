#       $Id: __init__.py,v 1.1.1.1 2008/08/18 10:17:30 dieter Exp $
from ZopeProfiler import _hookZServerPublisher, _initializeModule, \
     ZopeProfiler

_hookZServerPublisher()

def initialize(context):
  control_panel = context._ProductContext__app.Control_Panel
  zpid = ZopeProfiler.id
  zp = getattr(control_panel, zpid, None)
  if zp is None:
    zp = ZopeProfiler()
    control_panel._setObject(zpid, zp)
  _initializeModule(zp)
