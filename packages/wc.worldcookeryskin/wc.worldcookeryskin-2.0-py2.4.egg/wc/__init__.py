try:
    import pkg_resources
    pkg_resources.declare_namespace('zope')
except ImportError:
    pass
