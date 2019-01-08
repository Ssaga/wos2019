import cCommonGame


class WosInterface(object):
    def __init__(self):
        self.actions = None
        self.battlefield = None
        self.cfg = None
        self.console = None
        self.is_debug = False
        self.player_info = None
        self.window = None

    def config(self):
        return self.cfg

    def log(self, text, type=cCommonGame.LogType.GAME):
        self.console.log_simple(text, type)

    def main_window(self):
        return self.window
