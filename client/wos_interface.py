import cCommonGame
import json
import numpy
import sys


class WosInterface(object):
    def __init__(self):
        self.actions = None
        self.battlefield = None
        # Server config, server_cfg not in use to be refractored
        self.cfg = dict()
        self.client_cfg = dict()
        self.console = None
        self.is_debug = False
        self.loading_widget = None
        self.player_info = None
        self.server_cfg = None
        self.window = None
        self.read_client_config()
        self.overwrite_client_config()

    def clean_up(self):
        self.loading_widget.deleteLater()

    def client_config(self):
        return self.client_cfg

    def read_client_config(self):
        try:
            with open('client/game_client.cfg') as data_file:
                self.client_cfg = json.load(data_file)
                random_seed = self.client_cfg['random_seed']
                numpy.random.seed(seed=random_seed)
        except FileNotFoundError:
            print('No such file or directory: \'client/game_client2.cfg\'')

    def overwrite_client_config(self):
        if len(sys.argv) > 1:
            try:
                self.client_cfg.update(json.loads(sys.argv[1]))
            except TypeError:
                print("Second argument must be a valid JSON string")

    def log(self, text, type=cCommonGame.LogType.GAME):
        self.console.log_simple(text, type)

    def main_window(self):
        return self.window

    def toggle_overlay(self, is_show, text="Please wait..."):
        if self.loading_widget is None:
            return
        if is_show:
            self.loading_widget.set_text(text)
            self.loading_widget.show()
        else:
            self.loading_widget.close()

    def server_config(self):
        return self.server_cfg
