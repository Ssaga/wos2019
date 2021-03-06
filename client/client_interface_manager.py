from cClientCommEngine import ClientCommEngine
from cCommonCommEngine import ConnInfo
import cMessages
import json
import threading
import time


class WosClientInterfaceManager(object):
    __instance = None
    __init_flag = False

    # Singleton pattern
    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(WosClientInterfaceManager, cls).__new__(cls, *args, **kwargs)
        return cls.__instance

    def __init__(self):
        if self.__init_flag:
            return
        self.__init_flag = True

        self.addr_svr = "127.0.0.1"
        self.port_req = 5556
        self.port_sub = 5557

        self.read_from_config()

        self.req_rep_if = ConnInfo(self.addr_svr, self.port_req)
        self.pub_sub_if = ConnInfo(self.addr_svr, self.port_sub)

        self.thread_client = None
        self.client_commEngine = None
        self.is_running = True

    def read_from_config(self):
        try:
            with open('client/game_client.cfg') as data_file:
                client_cfg = json.load(data_file)
                self.addr_svr = client_cfg['server']['addr']
                self.port_req = client_cfg['server']['req_rep_port']
                self.port_sub = client_cfg['server']['pub_sub_port']
        except FileNotFoundError:
            print('No such file or directory: \'client/game_client2.cfg\'')

    def client_thread(self, commEngine=ClientCommEngine()):
        print("*** client %s commEngine thread start ***" % commEngine.client_id)
        # global is_running
        commEngine.start()
        while self.is_running:
            time.sleep(1)
        commEngine.stop()
        print("*** client %s commEngine thread exit ***" % commEngine.client_id)

    def connect_to_server(self, player_id):
        self.client_commEngine = ClientCommEngine(player_id, self.req_rep_if, self.pub_sub_if)
        self.client_commEngine.start()
        time.sleep(1)

        self.thread_client = threading.Thread(name='client-thread', target=self.client_thread,
                                              args=(self.client_commEngine,))
        self.thread_client.start()
        return True

    def disconnect_from_server(self):
        print("Terminating connection from server...")
        self.is_running = False
        if self.thread_client is not None:
            self.thread_client.join()

    def get_config(self):
        cfg = self.client_commEngine.req_config()
        # print(vars(cfg))
        if isinstance(cfg, cMessages.MsgRepGameConfig):
            return cfg.config
        return False

    def get_game_status(self):
        rep = self.client_commEngine.recv_from_publisher()
        return rep

    def get_turn_info(self):
        rep = self.client_commEngine.req_turn_info()
        # print(vars(rep))
        if isinstance(rep, cMessages.MsgRepTurnInfo):
            return rep
        return False

    def get_uw_report(self, ship_id):
        rep = self.client_commEngine.req_uw_report(ship_id)
        # print(vars(rep))
        if isinstance(rep, cMessages.MsgRepUwReport):
            print(vars(rep))
            return rep
        print(rep)
        return False

    def register_player(self):
        rep = self.client_commEngine.req_register()
        # print(vars(rep))
        if isinstance(rep, cMessages.MsgRepAckMap):
            return rep
        return False

    def send_action_attack(self, fire_list):
        rep = self.client_commEngine.req_action_fire(fire_list)
        if isinstance(rep, cMessages.MsgRepAck):
            return rep.ack
        return False

    def send_action_move(self, move_list):
        rep = self.client_commEngine.req_action_move(move_list)
        if isinstance(rep, cMessages.MsgRepAck):
            return rep.ack
        return False

    def send_action_satcom(self, satcom):
        rep = self.client_commEngine.req_action_satcom(satcom)
        if isinstance(rep, cMessages.MsgRepAckMap):
            return rep
        return False

    def send_action_uw_ops(self, uw_actions):
        rep = self.client_commEngine.req_action_uw_ops(uw_actions)
        if isinstance(rep, cMessages.MsgRepAck):
            return rep
        return False

    def send_deployment(self, ship_list, ship_uw_list=list()):
        rep = self.client_commEngine.req_register_ships(ship_list, ship_uw_list)
        if isinstance(rep, cMessages.MsgRepAck):
            return rep.ack
        return False
