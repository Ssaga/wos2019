class WosInterface(object):
    def __init__(self):
        self.actions = None
        self.battlefield = None
        self.cfg = None
        self.console = None
        self.is_debug = True
        self.player_info = None
        self.window = None

    def config(self):
        return self.cfg

    def log(self, text):
        self.console.log_simple(text)

    def main_window(self):
        return self.window