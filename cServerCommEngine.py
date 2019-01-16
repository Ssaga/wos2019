from json import JSONDecoder

import zmq
import json
import threading
import time

from cCommonCommEngine import ConnInfo
from cCommonGame import GameStatus

import cMessages
from cMessages import MsgJsonEncoder
from cMessages import MsgJsonDecoder

#
#
#
class ServerCommEngine:
    #
    def __init__(self,
                 rep_if = ConnInfo("*", 5556), 	# server-client
                 pub_if = ConnInfo("*", 5557),	# publisher
                 polling_rate = 1000,			# unit in millisecond
                 bc_rate = 1000):				# unit in millisecond
        self.rep_if = rep_if
        self.pub_if = pub_if
        self.start_time = None
        self.pub_thread = None
        self.game_status = None
        self.context = None
        self.socket = None
        self.poller = zmq.Poller()
        self.reset_conn = False
        self.is_ready = False
        self.polling_rate = polling_rate
        self.bc_rate = bc_rate


    def start(self):
        # create the thread for the subscriber & start it
        if (self.pub_thread is not None):
            self.pub_thread.stop()
            self.pub_thread.join()
        self.pub_thread = ServerCommEnginePublisher(self.pub_if.addr, self.pub_if.port, self.bc_rate)
        self.pub_thread.start()
        # setup the server
        self.setup_server()
        print("\tServer CommEngine Started...")
        self.is_ready = True


    def stop(self):
        self.is_ready = False
        # stop the created subscriber thread
        if (self.pub_thread is not None):
            try:
                self.pub_thread.stop()
                self.pub_thread.join()
                self.pub_thread = None
                print("\tPublisher thread stopped.")
            except RuntimeError:
                print("\tPublisher thread not started.")
        # stop the server
        self.teardown_server()
        print("\tServer CommEngine Stopped...")


    def setup_server(self):
        # create the req-rep i/f with the server
        if (self.context is not None):
            print("\tRecreate server...")
            self.teardown_server(self)
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        connString = str("tcp://%s:%s" % (self.rep_if.addr, self.rep_if.port,))
        print("\tSetting up server... [%s]" % connString)
        self.socket.bind(connString)
        self.socket.setsockopt(zmq.LINGER, 0)
        self.poller.register(self.socket, zmq.POLLIN)


    def teardown_server(self):
        # close the connection of the rep socket
        if (self.socket is not None):
            try:
                self.poller.unregister(self.socket)
            except:
                print("\tSocket is not registered in poller")

            try:
                self.socket.close()
                self.socket = None
            except zmq.ZMQError:
                print("\tError closing the socket")

        # terminate the context
        if (self.context is not None):
            try:
                self.context.term()
                self.context = None
            except zmq.ZMQError:
                print("Error terminating context")


    def set_game_status(self, game_status=GameStatus()):
        msg_game_status = cMessages.MsgPubGameStatus(game_status.get_enum_game_state(),
                                                     game_status.game_round,
                                                     game_status.player_turn,
                                                     game_status.time_remain)
        self.pub_thread.set_game_status(msg_game_status)


    def recv(self):
        msg = None
        if (self.socket is not None):
            try:
                socks = dict(self.poller.poll(self.polling_rate))
                if (self.socket in socks) and (socks[self.socket] == zmq.POLLIN):
                    # msg = self.socket.recv_json(0, cls=MsgJsonDecoder)
                    msg_str = self.socket.recv_string()
                    msg = json.loads(msg_str, cls=MsgJsonDecoder)
                    print("\tServer: RECV: %s" % msg)
            except zmq.ZMQError:
                self.reset_conn = True
        else:
            print("\tCommEngine is not started")
        return msg


    def send(self, msg):
        if self.socket is not None:
            if issubclass(type(msg), cMessages.Msg):
                try:
                    print("\tServer: sending: %s" % vars(msg))
                    #self.socket.send_json(msg, 0, cls=MsgJsonEncoder)
                    msg_str = json.dumps(msg, cls=MsgJsonEncoder)
                    self.socket.send_string(msg_str)
                except zmq.ZMQError:
                    self.reset_conn = True
            else:
                print("\tServer: Unknown msg-type: %s" % type(msg))
        else:
            print("\tCommEngine is not started")

#
#
#
class ServerCommEnginePublisher(threading.Thread):
    def __init__(self, addr_svr, port_pub, bc_rate):
        threading.Thread.__init__(self)
        self.addr_svr = addr_svr
        self.port_pub = port_pub
        self.bc_rate = bc_rate / 1000
        self.is_running = False
        self.game_status = None
        self.context = None
        self.socket = None

    # Main Thread body
    def run(self):
        # setup the connection with the publisher from game server
        self.setup()

        self.is_running = True
        while self.is_running:
            if (self.game_status is not None) and (self.socket is not None):
                # send the game status to the client
                # print("\tPublish game status: %s" % vars(self.game_status));
                # self.socket.send_json(self.game_status, 0, cls=MsgJsonEncoder);
                msg_str = json.dumps(self.game_status, cls=MsgJsonEncoder)
                self.socket.send_string(msg_str)

            # Put the thread to sleep
            time.sleep(self.bc_rate)

        # teardown the connection
        self.teardown()

        print("\tServerCommEnginePublisher thread has exited")


    # Stop the execution of this thread
    def stop(self):
        self.is_running = False


    # Setup the Publisher of the Server
    def setup(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        conn_string = str("tcp://%s:%s" % (self.addr_svr, self.port_pub,))
        print("\tRegistering publisher server... [%s]" % conn_string)
        self.socket.bind(conn_string)
        self.socket.setsockopt(zmq.LINGER, 0)


    # Teardown the connection
    def teardown(self):
        self.socket.close()
        self.context.term()


    # Update game status data
    def set_game_status(self, game_status=cMessages.MsgPubGameStatus()):
        self.game_status = game_status



