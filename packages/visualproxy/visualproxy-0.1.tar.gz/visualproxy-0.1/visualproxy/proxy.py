from visualproxy.interfaces import IProxyWidget

_Unset = object()


class Proxy(object):
    def __init__(self, model=None):
        self.widgets = {}
        self.names = {}
        self.model = model

    def addmodel(self, model):
        self.model = model

    def addwidget(self, attribute, widget):
        proxywidget = IProxyWidget(widget)
        proxywidget.proxyattached(self)
        self.widgets[attribute] = proxywidget
        self.names[proxywidget] = attribute
        if self.model is not None:
            value = getattr(self.model, attribute, _Unset)
            if value is not _Unset:
                proxywidget.set(value)

        return proxywidget

    def addwidgets(self, **widgets):
        for attribute, widget, in widgets.items():
            self.addwidget(attribute, widget)

    def getwidgets(self):
        return self.widgets.values()

    def getvalues(self):
        if self.model is None:
            raise StopIteration

        for attribute in self.widgets:
            value = getattr(self.model, attribute, _Unset)
            if value is not _Unset:
                yield attribute, value

    def removewidget(self, name):
        proxywidget = self.widgets.pop(name)
        del self.names[proxywidget]
        proxywidget.proxydetached(self)

    def notifychanged(self, proxywidget):
        name = self.names[proxywidget]
        if self.model is not None:
            value = proxywidget.get()
            setattr(self.model, name, value)
