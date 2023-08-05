from zope.interface import Interface


class IProxyWidget(Interface):
    def set(value):
        pass

    def get():
        pass

    def proxyattached(proxy):
        pass

    def proxydetached(proxy):
        pass


class IWidgetContainer(Interface):
    def get(name):
        pass
