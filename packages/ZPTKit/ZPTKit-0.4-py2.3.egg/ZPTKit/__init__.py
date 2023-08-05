try:
    from pkg_resource import require
except ImportError:
    pass
else:
    require('Component')

try:
    from zptcomponent import ZPTComponent
except ImportError, e:
    pass

def InstallInWebKit(appServer):
    pass
