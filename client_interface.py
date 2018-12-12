from cClientCommEngine import ClientCommEngine
from cCommonCommEngine import ConnInfo
import threading
import time


class WosClicentInterface(object):
    addr_svr = "127.0.0.1"
    port_req = 5556
    port_sub = 5557

    req_rep_if = ConnInfo(addr_svr, port_req)
    pub_sub_if = ConnInfo(addr_svr, port_sub)

    thread_client = None
    is_running = True

    @staticmethod
    def client_thread(commEngine=ClientCommEngine()):
        print("*** client %s commEngine thread start ***" % commEngine.client_id)
        # global is_running
        commEngine.start()
        while (WosClicentInterface.is_running == True):
            time.sleep(1)
        commEngine.stop()
        print("*** client %s commEngine thread exit ***" % commEngine.client_id)

    @staticmethod
    def connect_to_server():
        client_commEngine = ClientCommEngine(1, WosClicentInterface.req_rep_if, WosClicentInterface.pub_sub_if)
        WosClicentInterface.thread_client = threading.Thread(name='client-thread',
                                                             target=WosClicentInterface.client_thread,
                                                             args=(client_commEngine,))
        WosClicentInterface.thread_client.start()
        # rep = client_commEngine.req_register()
        # print(vars(rep))
        # rep = list_client_comm_engine[player_turn].req_register_ships([])

    @staticmethod
    def disconnect_from_server():
        print("Terminating connection from server...")
        WosClicentInterface.is_running = False
        WosClicentInterface.thread_client.join()

    @staticmethod
    def send_deployment():
        pass
