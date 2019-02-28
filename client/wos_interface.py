import cCommonGame
import json


class WosInterface(object):
    def __init__(self):
        self.actions = None
        self.battlefield = None
        self.client_cfg = None
        self.console = None
        self.is_debug = False
        self.player_info = None
        self.server_cfg = None
        self.window = None
        self.read_client_config()

    def client_config(self):
        return self.client_cfg

    def read_client_config(self):
        try:
            with open('client/game_client.cfg') as data_file:
                self.client_cfg = json.load(data_file)
        except FileNotFoundError:
            print('No such file or directory: \'client/game_client2.cfg\'')

    def log(self, text, type=cCommonGame.LogType.GAME):
        self.console.log_simple(text, type)

    def main_window(self):
        return self.window

    def server_config(self):
        return self.server_cfg
