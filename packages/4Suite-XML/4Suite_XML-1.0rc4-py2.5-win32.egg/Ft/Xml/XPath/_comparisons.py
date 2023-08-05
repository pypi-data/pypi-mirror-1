# dynamic module loader stub for .egg zipfiles
def __bootstrap__():
    global __bootstrap__, __loader__, __file__
    import imp, pkg_resources
    __file__ = pkg_resources.resource_filename(__name__, '_comparisons.pyd')
    del __bootstrap__, __loader__
    imp.load_dynamic(__name__, __file__)
__bootstrap__()
