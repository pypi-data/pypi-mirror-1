import sys

# copied from twisted/python/reflect.py
def namedAny(name):
    """Get a fully named package, module, module-global object, or attribute.

    @param name:
    @returns: object, module or attribute
    """

    names = name.split('.')
    topLevelPackage = None
    moduleNames = names[:]
    while not topLevelPackage:
        try:
            trialname = '.'.join(moduleNames)
            topLevelPackage = __import__(trialname)
        except ImportError:
            # if the ImportError happened in the module being imported,
            # this is a failure that should be handed to our caller.
            # count stack frames to tell the difference.
            import traceback
            exc_info = sys.exc_info()
            if len(traceback.extract_tb(exc_info[2])) > 1:
                try:
                    # Clean up garbage left in sys.modules.
                    del sys.modules[trialname]
                except KeyError:
                    # Python 2.4 has fixed this.  Yay!
                    pass
                raise exc_info[0], exc_info[1], exc_info[2]
            moduleNames.pop()

    obj = topLevelPackage
    for n in names[1:]:
        obj = getattr(obj, n)

    return obj
