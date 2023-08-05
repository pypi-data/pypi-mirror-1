import gtk
from zope.interface import Interface, classImplements

from visualproxy.adapter import registry
from visualproxy.interfaces import IProxyWidget


class IGtkEntry(Interface):
    pass



class IGtkSpinButton(Interface):
    pass



class IGtkLabel(Interface):
    pass


def register():
    classImplements(gtk.Entry, IGtkEntry)
    registry.register([IGtkEntry], IProxyWidget, '',
                      'visualproxy.gtkui.widgets.EntryWidgetProxy')

    classImplements(gtk.SpinButton, IGtkSpinButton)
    registry.register([IGtkSpinButton], IProxyWidget, '',
                      'visualproxy.gtkui.widgets.SpinButtonWidgetProxy')

    classImplements(gtk.Label, IGtkLabel)
    registry.register([IGtkLabel], IProxyWidget, '',
                      'visualproxy.gtkui.widgets.LabelWidgetProxy')


