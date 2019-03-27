import time
from threading import Thread
import numpy as np
import json

import appWosBattleshipServer
import cMessages

import cCommonGame
import cCommonCommEngine
import wosBattleshipServer.cCommon as cCommon

from cClientCommEngine import ClientCommEngine

from wosBattleshipServer.cCommon import SvrCfgJsonDecoder
from wosBattleshipServer.cCommon import ServerGameConfig


is_running = True
is_server_ready = False

def wos_test_client(num_of_rounds, player_id, boundary):

    # network setting
    addr_svr = "127.0.0.1"
    port_req = 5556
    port_sub = 5557
    req_rep_if = cCommonCommEngine.ConnInfo(addr_svr, port_req)
    pub_sub_if = cCommonCommEngine.ConnInfo(addr_svr, port_sub)

    print("Client %s: Creating CommEngine" % player_id)
    client_comm_engine = ClientCommEngine(player_id, req_rep_if, pub_sub_if, 1000)

    print("Client %s: Starting CommEngine" % player_id)
    client_comm_engine.start()

    while not client_comm_engine.is_ready:
        print("Client %s: Waiting for CommEngine to be ready" % player_id)
        time.sleep(1)

    print("Client %s: READY..." % player_id)

    # map_x_len = 0
    # map_y_len = 0

    # Test 1: Register four client to get the data map
    test_reply = client_comm_engine.req_register()
    if isinstance(test_reply, cMessages.MsgRepAckMap):
        print(test_reply)
        assert (test_reply.ack is True)
        # map_x_len, map_y_len = np.shape(test_reply.map_data)
        print("Client %s: Recv Map Size: %s" % (player_id, np.shape(test_reply.map_data)))
    else:
        print("Incorrect Msg type : %s" % test_reply)
    assert(isinstance(test_reply, cMessages.MsgRepAckMap))


    # Test 2: Register the ships for the four client
    # Register 3x ship
    ship_list = []
    for ship_id in range(3):
        ship_info = cCommonGame.ShipInfo(ship_id=ship_id,
                                         ship_type=cCommonGame.ShipType.MIL,
                                         position=cCommonGame.Position(
                                             int(np.random.random_integers(boundary[0][0] + 3, boundary[0][1] - 3)),
                                             int(np.random.random_integers(boundary[1][0] + 3, boundary[1][1] - 3))),
                                         heading=0,
                                         size=3,
                                         is_sunken=False)
        if ship_id == 1:
            ship_info.position.x = boundary[0][0] + 0
            ship_info.position.y = boundary[1][0] + ((ship_info.size - 1) // 2)
            ship_info.heading = 0
        ship_list.append(ship_info)

    # Register 1x uw_ship
    uw_ship_list = []
    uw_ship_list.append(cCommon.UwShipInfo(ship_id=1,
                                        position=cCommonGame.Position(boundary[0][0],
                                                                      boundary[0][1])))

    test_reply = client_comm_engine.req_register_ships(ship_list=ship_list,
                                                       uw_ship_list=uw_ship_list)
    if isinstance(test_reply, cMessages.MsgRepAck):
        print(test_reply)
        assert (test_reply.ack == True)
    else:
        print("Incorrect Msg type")
    assert(isinstance(test_reply, cMessages.MsgRepAck))

    # Test 3: Get the Game Configuration from the server
    game_config_list = dict()
    if isinstance(client_comm_engine, ClientCommEngine):
        test_reply = client_comm_engine.req_config()
        if isinstance(test_reply, cMessages.MsgRepGameConfig):
            print(test_reply)
            assert (test_reply.ack == True)
            game_config_list[player_id] = test_reply
        else:
            print("Incorrect Msg type")
        assert(isinstance(test_reply, cMessages.MsgRepGameConfig))

    game_status = client_comm_engine.recv_from_publisher()
    while game_status is None:
        print("game status is None")
        time.sleep(1)
        game_status = client_comm_engine.recv_from_publisher()

    while game_status.get_enum_game_state() == cCommonGame.GameState.INIT:
        print("game status is INIT")
        time.sleep(1)
        game_status = client_comm_engine.recv_from_publisher()

    round_offset = 0
    # # Test timeout for round 1
    # game_status = client_comm_engine.recv_from_publisher()
    # while game_status.game_round < 2:
    #     print("*** *** Round %s - Turn %s - Time remain %s" % (game_status.game_round,
    #                                                            game_status.player_turn,
    #                                                            game_status.time_remain))
    #     time.sleep(1)
    #     game_status = client_comm_engine.recv_from_publisher()
    # round_offset = round_offset + 1


    # Test 4: Test Game Play
    for rounds_cnt in range(num_of_rounds):

        # Wait until new round has started
        game_status = client_comm_engine.recv_from_publisher()
        while game_status.game_round == (rounds_cnt + round_offset) and \
                game_status.get_enum_game_state() != cCommonGame.GameState.STOP:
            game_status = client_comm_engine.recv_from_publisher()

        print("*** *** Round %s - Turn %s - Time remain %s" % (game_status.game_round,
                                                               game_status.player_turn,
                                                               game_status.time_remain))

        if isinstance(client_comm_engine, ClientCommEngine):
            # Test 4 i  : Get the Game Turn from the server
            test_reply = client_comm_engine.req_turn_info()
            if (game_status.get_enum_game_state() != cCommonGame.GameState.STOP) and \
                    isinstance(test_reply, cMessages.MsgRepTurnInfo):
                print("%s/%s - %s" % (game_status.player_turn, player_id, test_reply))
                assert (test_reply.ack is True)
                # if game_status.player_turn == player_id:
                #     assert (test_reply.ack is True)
                # else:
                #     assert (test_reply.ack is False)
            elif (game_status.get_enum_game_state() == cCommonGame.GameState.STOP) and \
                    isinstance(test_reply, cMessages.MsgRepAck):
                print("%s/%s - %s" % (game_status.player_turn, player_id, test_reply))
                assert (test_reply.ack is False)
            else:
                print("Incorrect Msg type: %s/%s - %s %s" % (game_status.player_turn,
                                                             player_id,
                                                             test_reply,
                                                             type(test_reply)))

            if game_status.get_enum_game_state() != cCommonGame.GameState.STOP:
                assert(isinstance(test_reply, cMessages.MsgRepTurnInfo))
            else:
                assert (isinstance(test_reply, cMessages.MsgRepAck))

            # Test 4 ii : Request satcom action
            satcom_act = cCommonGame.SatcomInfo(6378 + 2000, 0, 5, 0, 150, 0, True, False)
            test_reply = client_comm_engine.req_action_satcom(satcom_act)
            if (game_status.get_enum_game_state() != cCommonGame.GameState.STOP) and \
                    isinstance(test_reply, cMessages.MsgRepAckMap):
                print("%s/%s - %s" % (game_status.player_turn, player_id, test_reply))
                if game_config_list[player_id].config.en_satellite:
                    assert (test_reply.ack is True)
                else:
                    assert (test_reply.ack is False)
                # if (game_status.player_turn == player_id) and \
                #         (game_config_list[player_id].config.en_satellite):
                #     assert (test_reply.ack is True)
                # else:
                #     assert (test_reply.ack is False)
            elif (game_status.get_enum_game_state() == cCommonGame.GameState.STOP) and \
                 isinstance(test_reply, cMessages.MsgRepAck):
                print("%s/%s - %s" % (game_status.player_turn, player_id, test_reply))
                assert (test_reply.ack is False)
            else:
                print("Incorrect Msg type: %s/%s - %s %s" % (game_status.player_turn,
                                                             player_id,
                                                             test_reply,
                                                             type(test_reply)))

            if game_status.get_enum_game_state() != cCommonGame.GameState.STOP:
                assert (isinstance(test_reply, cMessages.MsgRepAckMap))
            else:
                assert (isinstance(test_reply, cMessages.MsgRepAck))

            # Test 4 iii: Get the Game Turn from the server with satcom
            test_reply = client_comm_engine.req_turn_info()
            if (game_status.get_enum_game_state() != cCommonGame.GameState.STOP) and \
                    isinstance(test_reply, cMessages.MsgRepTurnInfo):
                print("%s/%s - %s" % (game_status.player_turn, player_id, test_reply))
                assert (test_reply.ack is True)
                # if game_status.player_turn == player_id:
                #     assert (test_reply.ack is True)
                # else:
                #     assert (test_reply.ack is False)
            elif (game_status.get_enum_game_state() == cCommonGame.GameState.STOP) and \
                    isinstance(test_reply, cMessages.MsgRepAck):
                print("%s/%s - %s" % (game_status.player_turn, player_id, test_reply))
                assert (test_reply.ack is False)
            else:
                print("Incorrect Msg type: %s/%s - %s %s" % (game_status.player_turn,
                                                             player_id,
                                                             test_reply,
                                                             type(test_reply)))

            if game_status.get_enum_game_state() != cCommonGame.GameState.STOP:
                assert(isinstance(test_reply, cMessages.MsgRepTurnInfo))
            else:
                assert (isinstance(test_reply, cMessages.MsgRepAck))

            # Test 4 iv : Request uw report / action
            test_reply = client_comm_engine.req_uw_report(ship_id=1)
            if isinstance(test_reply, cMessages.MsgRepUwReport):
                print("uw_report: %s/%s - %s" % (game_status.player_turn, player_id, test_reply))
            elif (game_status.get_enum_game_state() == cCommonGame.GameState.STOP) and \
                    isinstance(test_reply, cMessages.MsgRepAck):
                print("uw_report: %s/%s - %s" % (game_status.player_turn, player_id, test_reply))
            else:
                print("uw_report: Incorrect Msg type: %s/%s - %s %s" % (game_status.player_turn,
                                                             player_id,
                                                             test_reply,
                                                             type(test_reply)))
            if game_status.get_enum_game_state() != cCommonGame.GameState.STOP:
                assert (isinstance(test_reply, cMessages.MsgRepUwReport))
            else:
                assert (isinstance(test_reply, cMessages.MsgRepAck))

            if isinstance(test_reply, cMessages.MsgRepUwReport) and (test_reply.ack is True):
                # send new order to the server
                ship_1_uw_action_list = list()
                ship_1_uw_action_list.append(cCommonGame.UwActionMoveScan(
                    goto_pos=cCommonGame.Position(int((boundary[0][0] + boundary[1][0]) // 2),
                                                  int((boundary[1][0] + boundary[1][1]) // 2)),
                    scan_dur=10))
                # ship_2_uw_action_list = list()
                # ship_2_uw_action_list.append(cCommonGame.UwActionMoveScan(
                #     goto_pos=cCommonGame.Position(int((boundary[0][0] + boundary[1][0]) // 2),
                #                                   int((boundary[1][0] + boundary[1][1]) // 2)),
                #     scan_dur=10))
                uw_move_info_list = list()
                uw_move_info_list.append(cCommonGame.UwShipMovementInfo(ship_id=1,
                                                                        actions=ship_1_uw_action_list))
                # uw_move_info_list.append(cCommonGame.UwShipMovementInfo(ship_id=2,
                #                                                         actions=ship_2_uw_action_list))
                test_reply = client_comm_engine.req_action_uw_ops(uw_move_info_list)
                if isinstance(test_reply, cMessages.MsgRepAck):
                    print("uw_ops_action : player_id: %s - %s" % (player_id, test_reply.ack))
                else:
                    print("uw_ops_action : %s" % test_reply)
                assert (isinstance(test_reply, cMessages.MsgRepAck))
            # else do nothing

            # Test 4  v : Request move action
            move_list = list()
            move_list.append(cCommonGame.ShipMovementInfo(1, cCommonGame.Action.FWD))
            move_list.append(cCommonGame.ShipMovementInfo(1, cCommonGame.Action.CW))
            test_reply = client_comm_engine.req_action_move(move_list)
            if isinstance(test_reply, cMessages.MsgRepAck):
                print("%s/%s - %s" % (game_status.player_turn, player_id, test_reply))
                if game_status.get_enum_game_state() != cCommonGame.GameState.STOP:
                    assert (test_reply.ack is True)
                else:
                    assert (test_reply.ack is False)
                # if game_status.get_enum_game_state() != cCommonGame.GameState.STOP and \
                #         game_status.player_turn == player_id:
                #     assert (test_reply.ack is True)
                # else:
                #     assert (test_reply.ack is False)
            else:
                print("Incorrect Msg type: %s/%s - %s %s" % (game_status.player_turn,
                                                             player_id,
                                                             test_reply,
                                                             type(test_reply)))

            assert (isinstance(test_reply, cMessages.MsgRepAck))


            # Test 4 vi : Request fire action
            fire_list = list()
            fire_list.append(cCommonGame.FireInfo(cCommonGame.Position(0, 0)))
            test_reply = client_comm_engine.req_action_fire(fire_list)
            if isinstance(test_reply, cMessages.MsgRepAck):
                print("%s/%s - %s" % (game_status.player_turn, player_id, test_reply))
                if game_status.get_enum_game_state() != cCommonGame.GameState.STOP:
                    assert (test_reply.ack is True)
                else:
                    assert (test_reply.ack is False)
                # if game_status.get_enum_game_state() != cCommonGame.GameState.STOP and \
                #         game_status.player_turn == player_id:
                #     assert (test_reply.ack is True)
                # else:
                #     assert (test_reply.ack is False)
            else:
                print("%s/%s - %s" % (game_status.player_turn, player_id, test_reply))
                print("Incorrect Msg type")

            assert (isinstance(test_reply, cMessages.MsgRepAck))


    # Teardown
    client_comm_engine.stop()

    pass


def wos_test_clients():
    # load the game setting
    game_setting = load_server_setting("game_server.cfg")
    if isinstance(game_setting, ServerGameConfig):
        # basic game setting
        num_of_rounds = game_setting.num_of_rounds + 2
        num_of_player = game_setting.num_of_player

        # Test setting
        list_thread_clients = dict()

        print("start : wos_test_clients ---------------")
        for i in range(num_of_player):
            # Get the current player id
            player_id = i + 1
            # compute the player boundary
            col_count = int(np.ceil(num_of_player / 2))
            row_count = game_setting.num_of_row

            player_x_sz = int(game_setting.map_size.x / col_count)
            player_y_sz = int(game_setting.map_size.y / row_count)

            x1 = int((i % col_count) * player_x_sz)
            x2 = x1 + player_x_sz
            y1 = int((i // col_count) * player_y_sz)
            y2 = y1 + player_y_sz

            boundary = ((x1, x2), (y1, y2))

            # Create the client
            print("Creating Client %s" % player_id)
            thread_client = Thread(name=str("client-%s-thread" % player_id),
                                   target=wos_test_client,
                                   args=(num_of_rounds, player_id, boundary))
            thread_client.start()
            list_thread_clients[player_id] = thread_client

        # Wait for the test-client-thread to terminate before we continue
        for player_id in list_thread_clients.keys():
            list_thread_clients[player_id].join()
    else:
        print("error : Unable to load server configuration")
    print("exit  : wos_test_clients ---------------")


def wos_battleship_server():
    global is_running
    global is_server_ready
    print("WOS Battlership Server -- started")

    wosServer = appWosBattleshipServer.WosBattleshipServer()
    wosServer.start()

    # Wait for the wosServer to complete is start operation
    while not wosServer.comm_engine.is_ready:
        time.sleep(1)

    # Loop until the program exit
    is_server_ready = True
    while is_running:
        time.sleep(1)

    # Stop the communication engine and wait for it to stop
    wosServer.stop()
    wosServer.join()
    print("WOS Battlership Server -- end")

# ---------------------------------------------------------------------------
def load_server_setting(filename):
    game_setting = None
    try:
        with open(filename) as infile:
            game_setting = json.load(infile, cls=SvrCfgJsonDecoder)
    except:
        print("Unable to load server setting")

    return game_setting



if __name__ == '__main__':
    print("*** %s (%s)" % (__file__, time.ctime(time.time())))
    is_running = True

    print("Start the WOS server thread")
    server_thread = Thread(target=wos_battleship_server)
    server_thread.start()

    while not is_server_ready:
        time.sleep(1)

    print("Starting WOS test client...")
    wos_test_clients()

    is_running = False

    print("*** END (%s)" % (time.ctime(time.time())))
