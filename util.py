from datetime import datetime

class Time_It(object):
    def __init__(self, label):
        self.start = datetime.now()
        self.label = label
        self.delta = None

    def finish(self):
        self.end = datetime.now()
        self.delta = self.end - self.start

    def __repr__(self):
        return "{0} {1}".format(self.label, self.delta)

