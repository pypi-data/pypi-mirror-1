from zope.interface.adapter import AdapterRegistry
from zope.interface.interface import adapter_hooks, providedBy

from visualproxy.reflect import namedAny

registry = AdapterRegistry()

def hook(provided, object):
    adapterClass = registry.lookup1(providedBy(object), provided, '')
    if adapterClass is not None:
        if type(adapterClass) is str:
            adapterClass = namedAny(adapterClass)
        return adapterClass(object)
adapter_hooks.append(hook)
