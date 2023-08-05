import gtk
from zope.interface import implements

from visualproxy.interfaces import IProxyWidget
from visualproxy.gtkui.signal import Signal


class EntryWidgetProxy(object):
    implements(IProxyWidget)
    def __init__(self, context):
        self.context = context
        self.signals = {}

    def proxyattached(self, proxy):
        signal = Signal(self.context, proxy)
        signal.connect('changed', self._on_changed)
        self.signals[proxy] = signal

    def proxydetached(self, proxy):
        signal = self.signals.pop(proxy)
        signal.disconnectall()

    def get(self):
        return self.context.get_text()

    def set(self, value):
        self.context.set_text(value)
        self.context.set_position(len(value))

    def _on_changed(self, entry, proxy):
        proxy.notifychanged(self)



class LabelWidgetProxy(object):
    implements(IProxyWidget)

    def __init__(self, context):
        self.context = context
        self.signals = {}

    def proxyattached(self, proxy):
        signal = Signal(self.context, proxy)
        signal.connect('notify::label', self._on_label_notify)
        self.signals[proxy] = signal

    def proxydetached(self, proxy):
        signal = self.signals.pop(proxy)
        signal.disconnectall()

    def get(self):
        return self.context.get_label()

    def set(self, value):
        self.context.set_label(value)

    def _on_label_notify(self, label, pspec, proxy):
        proxy.notifychanged(self)



class SpinButtonWidgetProxy(object):
    implements(IProxyWidget)
    def __init__(self, context):
        self.context = context
        self.context.set_range(0, 100)
        self.context.set_increments(1, 10)
        self.signals = {}

    def proxyattached(self, proxy):
        signal = Signal(self.context, proxy)
        signal.connect('value-changed', self._on_changed)
        self.signals[proxy] = signal

    def proxydetached(self, proxy):
        signal = self.signals.pop(proxy)
        signal.disconnectall()

    def get(self):
        return self.context.get_value()

    def set(self, value):
        self.context.set_value(value)

    def _on_changed(self, spin, proxy):
        proxy.notifychanged(self)

