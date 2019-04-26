import zmq
import json
import threading

import cCommonGame
from cCommonCommEngine import ConnInfo

import cMessages
from cMessages import MsgJsonEncoder
from cMessages import MsgJsonDecoder

#
#
#
class ClientCommEngine:
    #
    def __init__(self, client_id = 0,
                 req_if = ConnInfo("127.0.0.1", 5556),
                 sub_if = ConnInfo("127.0.0.1", 5557),
                 polling_rate=1000):
        self.client_id = client_id
        self.req_if = req_if			# server-client
        self.sub_if = sub_if			# publisher
        self.polling_rate = polling_rate

        self.start_time = None
        self.sub_thread = None
        self.context = None
        self.socket = None
        self.reset_conn = False
        self.is_ready = False

    def start(self):
        # create the thread for the subscriber & start it
        if (self.sub_thread is not None):
            self.sub_thread.stop()
            self.sub_thread.join()
        self.sub_thread = ClientCommEngineSubscriber(self.sub_if.addr, self.sub_if.port, self.polling_rate)
        self.sub_thread.start()

        # set the flag to create the connection with server
        self.reset_conn = True

        print("\tClient %s CommEngine Started..." % self.client_id)
        # set the flag to indicate that commEngine is ready
        self.is_ready = True

    def stop(self):
        self.is_ready = False
        # stop the created subscriber thread
        if (self.sub_thread is not None):
            try:
                self.sub_thread.stop()
                self.sub_thread.join()
                self.sub_thread = None
                print("Subscriber thread stopped.")
            except RuntimeError:
                print("Subscriber thread not started.")
        # end the connection with server
        self.teardown_connect()
        print("\tClient %s CommEngine Stopped..." % self.client_id)

    def recv_from_publisher(self):
        data = None
        if self.sub_thread is not None:
            recv_data = self.sub_thread.get()
            if isinstance(recv_data, cMessages.MsgPubGameStatus):
                data = cCommonGame.GameStatus(recv_data.game_state,
                                              recv_data.game_round,
                                              recv_data.player_turn,
                                              recv_data.time_remain)
        else:
            print("Subscription thread in no available...")
        return data

    def setup_connect(self):
        # create the req-rep i/f with the server
        if (self.context is not None):
            print("\tReset connection with server")
            self.teardown_connect()
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        connString = str("tcp://%s:%s" % (self.req_if.addr, self.req_if.port,))
        print("\tClient %s: Setup connection to server... [%s]" % (self.client_id, connString))
        self.socket.connect(connString)
        self.socket.setsockopt(zmq.LINGER, 0)
        self.socket.RCVTIMEO = 300000			# in milliseconds
        # self.poller = zmq.Poller()
        # self.poller.register(self.socket, zmq.POLLIN)

    def teardown_connect(self):
        # close the connection of the req socket
        if (self.socket is not None):
            try:
                print("Unregister socket")
                self.poller.unregister(self.socket)
            except:
                print("\tUnable to unregister socket")
            try:
                print("Close socket")
                self.socket.close()
                self.socket = None
            except:
                print("\tError closing the socket")

        # teminate the context
        if (self.context is not None):
            try:
                print("Terminate context")
                self.context.term()
                self.context = None
            except:
                print("\tError terminating context")
        print("Teardown completed")

    def send(self, msg):
        """
        Send the given message to the server.
        Note: This is a blocking operation
        :param msg: Msg Request type sub-class
        :return: reply msg from the server
        """
        # reset the connection if required
        if (self.reset_conn is True):
            self.setup_connect()
            self.reset_conn = False

        reply = None
        if issubclass(type(msg), cMessages.Msg):
            # send the request to the server
            try:
                print("\rClient %s: SEND: %s" % (self.client_id, vars(msg)))
                # self.socket.send_json(msg, 0, cls=MsgJsonEncoder)
                msg_str = json.dumps(msg, cls=MsgJsonEncoder)
                self.socket.send_string(msg_str)
            except zmq.ZMQError:
                self.reset_conn = True

            # wait for the reply from the server
            try:
                # reply = self.socket.recv_json(0, cls=MsgJsonDecoder)
                reply_str = self.socket.recv_string()
                reply = json.loads(reply_str, cls=MsgJsonDecoder)
                if reply is not None:
                    print("\rClient %s: RECV: %s" % (self.client_id, reply))
                else:
                    print("\rClient %s: RECV: --NO DATA--" % self.client_id)
            except zmq.ZMQError:
                self.reset_conn = True

            # # wait for the reply from the server
            # try:
            # 	socks = dict(self.poller.poll(2000))
            # 	if (self.socket in socks) and (socks[self.socket] == zmq.POLLIN):
            # 		# reply = self.socket.recv_json(0, cls=MsgJsonDecoder)
            # 		reply_str = self.socket.recv_string()
            # 		reply = json.loads(reply_str, cls=MsgJsonDecoder)
            # 		if reply is not None:
            # 			print("\rClient %s: RECV: %s" % (self.client_id, reply))
            # 		else:
            # 			print("\rClient %s: RECV: --NO DATA--" % self.client_id)
            # except zmq.ZMQError:
            # 	self.reset_conn = True
        else:
            print("\tUnable to send unsupported message")
        return reply

    def req_register(self):
        """
        Get the game map data initialized at start-up
        :return: MsgRepAckMap msg
        """
        request = cMessages.MsgReqRegister(self.client_id)
        data = self.send(request)
        reply = None
        if isinstance(data, cMessages.MsgRep):
            reply = data
        return reply

    def req_register_ships(self, ship_list=[], uw_ship_list=[]):
        """
        Message for the player to register their ships for the game
        :param ship_list: List of ShipInfo to be registered
        :param uw_ship_list: List of UwShipInfo to be registered
        :return: MsgRepAck msg [indicate if it is successful]
        """
        request = cMessages.MsgReqRegShips(player_id=self.client_id,
                                           ship_list=ship_list,
                                           uw_ship_list=uw_ship_list)
        data = self.send(request)
        reply = None
        if isinstance(data, cMessages.MsgRep):
            reply = data
        return reply

    def req_config(self):
        """
        Request the configuration of the current game
        :return: MsgRepGameConfig msg
        """
        request = cMessages.MsgReqConfig(self.client_id)
        data = self.send(request)
        reply = None
        if isinstance(data, cMessages.MsgRep):
            reply = data
        return reply

    def req_turn_info(self):
        """
        Get the information of the player for the current turn
        This includes the following:
            - List of Player ships' status
            - List of Civilian / Enemy ships visable to the user
            - Information on the player being bombarded
            - Map data [Cloud and Island]
            - Player's Uw ships' position
        :return: MsgRepTurnInfo msg
        """
        request = cMessages.MsgReqTurnInfo(self.client_id)
        data = self.send(request)
        reply = None
        if isinstance(data, cMessages.MsgRep):
            reply = data
        return reply

    def req_action_move(self, move):
        """
        Send the data for the Ship Movement Action
        :param move: ShipMovementInfo / List of ShipMovementInfo
        :return: MsgRepAck msg
        """
        request = cMessages.MsgReqTurnMoveAct(self.client_id, move)
        data = self.send(request)
        reply = None
        if isinstance(data, cMessages.MsgRep):
            reply = data
        return reply

    def req_action_fire(self, fire):
        """
        Send the data for the Fire Action
        :param fire: FireInfo / List of FireInfo
        :return: MsgRepAck msg
        """
        request = cMessages.MsgReqTurnFireAct(self.client_id, fire)
        data = self.send(request)
        reply = None
        if isinstance(data, cMessages.MsgRep):
            reply = data
        return reply

    def req_action_satcom(self, satcom):
        """
        Send the Satcom parameter to trigger a satcom action
        :param satcom: SatcomInfo class
        :return: MsgRepAckMap msg
        """
        request = cMessages.MsgReqTurnSatAct(self.client_id, satcom)
        data = self.send(request)
        reply = None
        if isinstance(data, cMessages.MsgRep):
            reply = data
        return reply

    def req_action_uw_ops(self, uw_actions):
        """
        Send a list of required uw operation to the server
        :param uw_actions: List of UwAction msgs
        :return: MsgRepAck msg
        """
        request = cMessages.MsgReqUwAction(self.client_id, uw_actions)
        data = self.send(request)
        reply = None
        if isinstance(data, cMessages.MsgRep):
            reply = data
        return reply

    def req_uw_report(self, ship_id):
        """
        Request for the uw report from the uw action list carried-out by the
        uw operation
        :param ship_id: Ship Id of the uw ship
        :return: MsgRepUwReport msg
        """
        request = cMessages.MsgReqUwReport(self.client_id, ship_id)
        data = self.send(request)
        reply = None
        if isinstance(data, cMessages.MsgRep):
            reply = data
        return reply


    # def req_action(self, move, fire, satcom):
    # 	# TODO:...
    # 	pass


    # def req_from_publisher(self):
    #     data = None
    #     if (self.sub_thread is not None):
    #         recv_data = self.sub_thread.get()
    #         if isinstance(recv_data, cMessages.MsgPubGameStatus):
    #             data = cCommonGame.GameStatus(recv_data.game_state,
    #                                           recv_data.game_round,
    #                                           recv_data.player_turn,
    #                                           recv_data.time_remain)
    #     return data



#
#
#
class ClientCommEngineSubscriber(threading.Thread):
    #
    def __init__(self, addr_svr, port_pub, polling_rate):
        threading.Thread.__init__(self)
        self.addr_svr = addr_svr
        self.port_pub = port_pub
        self.polling_rate = polling_rate
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
            # Poll from the socket
            socks = dict(self.poller.poll(self.polling_rate))
            if (self.socket in socks) and (socks[self.socket] == zmq.POLLIN):
                # msg = self.socket.recv_json(0, cls=MsgJsonDecoder)
                msg_str = self.socket.recv_string()
                msg = json.loads(msg_str, cls=MsgJsonDecoder)
                # print("\tsubscriber-recv: %s" % msg)

                # set  game status
                if isinstance(msg, cMessages.MsgPubGameStatus):
                    self.game_status = msg

        # teardown the connection
        self.teardown()

        print("\tClientCommEngineSubscriber thread has exited")

    # Stop the execution of this thread
    def stop(self):
        self.is_running = False

    # Subscribe to the Server Publishing/Billboard
    def setup(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        conn_string = str("tcp://%s:%s" % (self.addr_svr, self.port_pub,))
        print("\tSubscribing to server... [%s]" % conn_string)
        self.socket.connect(conn_string)
        self.socket.setsockopt(zmq.LINGER, 0)
        self.socket.setsockopt(zmq.SUBSCRIBE, b"");
        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)

    # Teardown the connection
    def teardown(self):
        self.poller.unregister(self.socket)
        self.socket.close()
        self.context.term()

    def get(self):
        return self.game_status
