import time
from threading import Thread
import numpy as np

import appWosBattleshipServer
import cMessages

import cCommonGame
import cCommonCommEngine

from cClientCommEngine import ClientCommEngine


is_running = True
is_server_ready = False

def wos_test_client():

    # Setup
    # Test setting
    num_of_rounds = 2
    num_of_player = 4
    list_client_comm_engine = dict()

    # network setting
    addr_svr = "127.0.0.1"
    port_req = 5556
    port_sub = 5557
    req_rep_if = cCommonCommEngine.ConnInfo(addr_svr, port_req)
    pub_sub_if = cCommonCommEngine.ConnInfo(addr_svr, port_sub)

    for i in range(num_of_player):
        player_id = i + 1
        print("Creating Client %s:" % player_id)
        client_comm_engine = ClientCommEngine(player_id, req_rep_if, pub_sub_if, 1000)
        list_client_comm_engine[player_id] = client_comm_engine

    for i in range(num_of_player):
        player_id = i + 1
        print("Starting Client %s:" % player_id)
        list_client_comm_engine[player_id].start()

    for i in range(num_of_player):
        player_id = i + 1
        print("Waiting for Client %s:" % player_id)
        while not list_client_comm_engine[player_id].is_ready:
            time.sleep(1)

    print("All the clients are ready...")

    map_x_len = 0
    map_y_len = 0
    # Test 1: Register four client to get the data map
    for i in range(num_of_player):
        player_id = i + 1

        client_comm_engine = list_client_comm_engine[player_id]

        if isinstance(client_comm_engine, ClientCommEngine):
            test_reply = client_comm_engine.req_register()
            if isinstance(test_reply, cMessages.MsgRepAckMap):
                print(test_reply)
                assert (test_reply.ack == True)
                map_x_len, map_y_len = np.shape(test_reply.map_data)
            else:
                print("Incorrect Msg type")
            assert(isinstance(test_reply, cMessages.MsgRepAckMap))


    # Test 2: Register the ships for the four client
    for i in range(num_of_player):
        player_id = i + 1

        col_count = int(np.ceil(num_of_player / 2))
        row_count = 2

        player_x_sz = int(map_x_len / col_count)
        player_y_sz = int(map_y_len / row_count)

        x1 = int((i % col_count) * player_x_sz)
        x2 = x1 + player_x_sz
        y1 = int((i // col_count) * player_y_sz)
        y2 = y1 + player_y_sz

        client_comm_engine = list_client_comm_engine[player_id]

        if isinstance(client_comm_engine, ClientCommEngine):

            ship_list = []
            for ship_id in range(3):
                ship_info = cCommonGame.ShipInfo(ship_id,
                                                 cCommonGame.Position(int(np.random.random_integers(x1+3, x2-3)),
                                                                      int(np.random.random_integers(y1+3, y2-3))),
                                                 0, 3, False)
                if ship_id == 1:
                    ship_info.position.x = x1 + 0
                    ship_info.position.y = y1 + 0
                    ship_info.heading = 0
                ship_list.append(ship_info)

            test_reply = client_comm_engine.req_register_ships(ship_list)
            if isinstance(test_reply, cMessages.MsgRepAck):
                print(test_reply)
                assert (test_reply.ack == True)
            else:
                print("Incorrect Msg type")
            assert(isinstance(test_reply, cMessages.MsgRepAck))

    # Test 3: Get the Game Configuration from the server
    game_config_list = dict()
    for i in range(num_of_player):
        player_id = i + 1

        client_comm_engine = list_client_comm_engine[player_id]

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
        time.sleep(1)
        game_status = client_comm_engine.recv_from_publisher()

    while game_status.get_enum_game_state() == cCommonGame.GameState.INIT:
        time.sleep(1)
        game_status = client_comm_engine.recv_from_publisher()

    # Test timeout for round 1
    game_status = client_comm_engine.recv_from_publisher()
    while game_status.game_round < 2:
        print("*** *** Round %s - Turn %s - Time remain %s" % (game_status.game_round,
                                                               game_status.player_turn,
                                                               game_status.time_remain))
        time.sleep(1)
        game_status = client_comm_engine.recv_from_publisher()


    # Test 4: Test Game Play
    for rounds_cnt in range(num_of_rounds):
        for turn_cnt in range(num_of_player):

            game_status = client_comm_engine.recv_from_publisher()
            while game_status.player_turn != (turn_cnt + 1):
                game_status = client_comm_engine.recv_from_publisher()

            print("*** *** Round %s - Turn %s - Time remain %s" % (game_status.game_round,
                                                                   game_status.player_turn,
                                                                   game_status.time_remain))

            # Test 4 i  : Get the Game Turn from the server
            for i in range(num_of_player):
                # player_id = i + 1
                player_id = ((turn_cnt + i + 1) % num_of_player) + 1
                client_comm_engine = list_client_comm_engine[player_id]
                if isinstance(client_comm_engine, ClientCommEngine):
                    test_reply = client_comm_engine.req_turn_info()
                    if isinstance(test_reply, cMessages.MsgRepTurnInfo):
                        print("%s/%s - %s" % (game_status.player_turn, player_id, test_reply))
                        if game_status.player_turn == player_id:
                            assert (test_reply.ack is True)
                        else:
                            assert (test_reply.ack is False)
                    else:
                        print("%s/%s - %s" % (game_status.player_turn, player_id, test_reply))
                        print("Incorrect Msg type")

                    assert(isinstance(test_reply, cMessages.MsgRepTurnInfo))

                    # Test 4 ii : Request satcom action
                    satcom_act = cCommonGame.SatcomInfo(1, 2, 3, 4, 5, 6, False, False)
                    test_reply = client_comm_engine.req_action_satcom(satcom_act)
                    if isinstance(test_reply, cMessages.MsgRepAckMap):
                        print("%s/%s - %s" % (game_status.player_turn, player_id, test_reply))
                        if (game_status.player_turn == player_id) and \
                                (game_config_list[player_id].config.en_satellite):
                            assert (test_reply.ack is True)
                        else:
                            assert (test_reply.ack is False)
                    else:
                        print("%s/%s - %s" % (game_status.player_turn, player_id, test_reply))
                        print("Incorrect Msg type")

                    assert (isinstance(test_reply, cMessages.MsgRepAckMap))

                    # Test 4 iii: Request move action
                    move_list = list()
                    move_list.append(cCommonGame.ShipMovementInfo(1, cCommonGame.Action.FWD))
                    move_list.append(cCommonGame.ShipMovementInfo(1, cCommonGame.Action.CW))
                    test_reply = client_comm_engine.req_action_move(move_list)
                    if isinstance(test_reply, cMessages.MsgRepAck):
                        print("%s/%s - %s" % (game_status.player_turn, player_id, test_reply))
                        if game_status.player_turn == player_id:
                            assert (test_reply.ack is True)
                        else:
                            assert (test_reply.ack is False)
                    else:
                        print("%s/%s - %s" % (game_status.player_turn, player_id, test_reply))
                        print("Incorrect Msg type")

                    assert (isinstance(test_reply, cMessages.MsgRepAck))


                    # Test 4 iv : Request fire action
                    fire_list = list()
                    fire_list.append(cCommonGame.FireInfo(cCommonGame.Position(0, 0)))
                    test_reply = client_comm_engine.req_action_fire(fire_list)
                    if isinstance(test_reply, cMessages.MsgRepAck):
                        print("%s/%s - %s" % (game_status.player_turn, player_id, test_reply))
                        if game_status.player_turn == player_id:
                            assert (test_reply.ack is True)
                        else:
                            assert (test_reply.ack is False)
                    else:
                        print("%s/%s - %s" % (game_status.player_turn, player_id, test_reply))
                        print("Incorrect Msg type")

                    assert (isinstance(test_reply, cMessages.MsgRepAck))


    # Teardown
    for i in range(num_of_player):
        player_id = i + 1
        list_client_comm_engine[player_id].stop()

    pass


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
    wosServer.stop();
    wosServer.join()
    print("WOS Battlership Server -- end")


if __name__ == '__main__':
    print("*** %s (%s)" % (__file__, time.ctime(time.time())))
    is_running = True

    print("Start the WOS server thread")
    server_thread = Thread(target=wos_battleship_server)
    server_thread.start()

    while not is_server_ready:
        time.sleep(1)

    print("Test client...")
    wos_test_client()

    is_running = False

    print("*** END (%s)" % (time.ctime(time.time())))
