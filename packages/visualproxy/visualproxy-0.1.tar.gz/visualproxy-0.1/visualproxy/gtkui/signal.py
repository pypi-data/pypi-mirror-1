class Signal(object):
    def __init__(self, widget, *user_data):
        self.widget = widget
        self.user_data = user_data
        self.signals = []

    def connect(self, signalName, callback):
        signalId = self.widget.connect(signalName, callback,
                                       *self.user_data)
        self.signals.append(signalId)

    def disconnectall(self):
        for signalId in self.signals:
            self.widget.disconnect(signalId)
        self.signals = []
