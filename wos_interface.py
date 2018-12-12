class WosInterface(object):
    def __init__(self):
        self.battlefield = None
        self.console = None
        self.actions = None

    # def add_action(self, action):

    def log(self, text):
        self.console.log_simple(text)