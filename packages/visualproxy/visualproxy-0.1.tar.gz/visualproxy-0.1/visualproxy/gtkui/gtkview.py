class WidgetNameSpace(object):
    def __getattr__(self, attr):
        return


class GtkView(object):
    def __init__(self, toplevel):
        self.toplevel = toplevel

        self.w = WidgetNamespace()

