class Mediator(object):
    def __init__(self):
        self.signals = {}

    def signal(self, signal_name, *args, **kw):
        for handler in self.signals.get(signal_name, []):
            handler(*args, **kw)

    def connect(self, signal_name, receiver):
        handlers = self.signals.setdefault(signal_name, [])
        handlers.append(receiver)

    def disconnect(self, signal_name, receiver):
        handlers[signal_name].remove(receiver)

