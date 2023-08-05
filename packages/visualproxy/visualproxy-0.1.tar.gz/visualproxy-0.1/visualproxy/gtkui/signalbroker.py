import inspect
import re

import gobject

from visualproxy.interfaces import IWidgetContainer

_method_regex = re.compile(r'^(on|after)_(\w+)__(\w+)$')


class SignalBroker(object):
    def __init__(self, instance):
        self._autoconnected = {}
        self._container = IWidgetContainer(instance)
        self._autoconnectsignals(instance)

    def _autoconnectsignals(self, instance):
        """
        Offers autoconnection of widget signals based on function names.
        You simply need to define your controller method in the format::

            def on_widget_name__signal_name(self, widget):

        In other words, start the method by "on_", followed by the
        widget name, followed by two underscores ("__"), followed by the
        signal name. Note: If more than one double underscore sequences
        are in the string, the last one is assumed to separate the
        signal name.
        """

        for fname, method in inspect.getmethods(instance, inspect.ismethod):
            # `on_x__y' has 7 chars and is the smallest possible handler
            if len(fname) < 7:
                continue
            match = _method_regex.match(fname)
            if match is None:
                continue
            on_after, w_name, signal = match.groups()

            widget = self._container.get(w_name)
            if widget is None:
                raise AttributeError("couldn't find widget %r in %r" % (
                                     w_name, self._container))
            if not isinstance(widget, gobject.GObject):
                raise AttributeError("%r in %r is not a widget or an action "
                                     "and can't be connected to"
                                     % (w_name, self._container))

            if not gobject.signal_query(signal, widget):
                raise TypeError("Widget %s doesn't provide a signal %s" % (
                                widget.__class__, signal))

            if on_after == 'on':
                signal_id = widget.connect(signal, method)
            elif on_after == 'after':
                signal_id = widget.connect_after(signal, method)
            else:
                raise AssertionError

            self._autoconnected.setdefault(widget, []).append(
                (signal, signal_id))

    def block(self, widget, signal_name):
        signals = self._autoconnected
        if not widget in signals:
            return

        for signal, signal_id in signals[widget]:
            if signal_name is None or signal == signal_name:
                widget.handler_block(signal_id)

    def unblock(self, widget, signal_name):
        signals = self._autoconnected
        if not widget in signals:
            return

        for signal, signal_id in signals[widget]:
            if signal_name is None or signal == signal_name:
                widget.handler_unblock(signal_id)

    def disconnect(self):
        for widget, signals in self._autoconnected.items():
            for signal, signal_id in signals:
                widget.disconnect(signal_id)
