import time
from threading import Thread
import numpy as np
import json
import collections
import copy

import appWosBattleshipServer
import cMessages

import cCommonGame
import cCommonCommEngine
import wosBattleshipServer.cCommon as cCommon

from cClientCommEngine import ClientCommEngine

from wosBattleshipServer.cCommon import SvrCfgJsonDecoder
from wosBattleshipServer.cCommon import ServerGameConfig


def wos_test_client(client_comm_engine, game_state, round_count, ):

    if isinstance(client_comm_engine, ClientCommEngine) and \
            isinstance(game_state, cCommonGame.GameState):

        if game_state is cCommonGame.GameState.INIT:
            # Register the ships for the player
            ship_list = []

            # Ship id 0
            ship_info = copy.deepcopy(cCommonGame.ShipInfo(ship_id=0,
                                                           ship_type=cCommonGame.ShipType.MIL,
                                                           position=cCommonGame.Position(0, 0),
                                                           heading=0,
                                                           size=3,
                                                           is_sunken=False))
            ship_list.append(ship_info)

            # Ship id 1
            ship_info = copy.deepcopy(cCommonGame.ShipInfo(ship_id=1,
                                                           ship_type=cCommonGame.ShipType.MIL,
                                                           position=cCommonGame.Position(0, 0),
                                                           heading=0,
                                                           size=3,
                                                           is_sunken=False))
            ship_list.append(ship_info)

            # Ship id 2
            ship_info = copy.deepcopy(cCommonGame.ShipInfo(ship_id=2,
                                                           ship_type=cCommonGame.ShipType.MIL,
                                                           position=cCommonGame.Position(0, 0),
                                                           heading=0,
                                                           size=3,
                                                           is_sunken=False))
            ship_list.append(ship_info)

            # Ship id 3
            ship_info = copy.deepcopy(cCommonGame.ShipInfo(ship_id=3,
                                                           ship_type=cCommonGame.ShipType.MIL,
                                                           position=cCommonGame.Position(0, 0),
                                                           heading=0,
                                                           size=3,
                                                           is_sunken=False))
            ship_list.append(ship_info)

            # Ship id 4
            ship_info = copy.deepcopy(cCommonGame.ShipInfo(ship_id=4,
                                                           ship_type=cCommonGame.ShipType.MIL,
                                                           position=cCommonGame.Position(0, 0),
                                                           heading=0,
                                                           size=3,
                                                           is_sunken=False))
            ship_list.append(ship_info)

            # Ship id 5
            ship_info = copy.deepcopy(cCommonGame.ShipInfo(ship_id=5,
                                                           ship_type=cCommonGame.ShipType.MIL,
                                                           position=cCommonGame.Position(0, 0),
                                                           heading=0,
                                                           size=3,
                                                           is_sunken=False))
            ship_list.append(ship_info)

            # Ship id 6
            ship_info = copy.deepcopy(cCommonGame.ShipInfo(ship_id=6,
                                                           ship_type=cCommonGame.ShipType.MIL,
                                                           position=cCommonGame.Position(0, 0),
                                                           heading=0,
                                                           size=3,
                                                           is_sunken=False))
            ship_list.append(ship_info)

            test_reply = client_comm_engine.req_register_ships(ship_list=ship_list)
            if isinstance(test_reply, cMessages.MsgRepAck):
                print("Is registration ok: %s" % test_reply.ack)
            else:
                print("Incorrect Msg type")

        elif game_state is cCommonGame.GameState.PLAY_INPUT:
            if round_count is 1:
                pass
                # Perform Satcom action

                # Perform Ship movement

                # Perform Fire action

            elif round_count is 2:
                pass
                # Perform Satcom action

                # Perform Ship movement

                # Perform Fire action

            elif round_count is 3:
                pass
                # Perform Satcom action

                # Perform Ship movement

                # Perform Fire action

            elif round_count is 4:
                pass
                # Perform Satcom action

                # Perform Ship movement

                # Perform Fire action

            elif round_count is 5:
                pass
                # Perform Satcom action

                # Perform Ship movement

                # Perform Fire action

            elif round_count is 6:
                pass
                # Perform Satcom action

                # Perform Ship movement

                # Perform Fire action

            elif round_count is 7:
                pass
                # Perform Satcom action

                # Perform Ship movement

                # Perform Fire action

            elif round_count is 8:
                pass
                # Perform Satcom action

                # Perform Ship movement

                # Perform Fire action

            elif round_count is 9:
                pass
                # Perform Satcom action

                # Perform Ship movement

                # Perform Fire action

            elif round_count is 10:
                pass
                # Perform Satcom action

                # Perform Ship movement

                # Perform Fire action

            elif round_count is 11:
                pass
                # Perform Satcom action

                # Perform Ship movement

                # Perform Fire action

            elif round_count is 12:
                pass
                # Perform Satcom action

                # Perform Ship movement

                # Perform Fire action

            elif round_count is 13:
                pass
                # Perform Satcom action

                # Perform Ship movement

                # Perform Fire action

            elif round_count is 14:
                pass
                # Perform Satcom action

                # Perform Ship movement

                # Perform Fire action

            elif round_count is 15:
                pass
                # Perform Satcom action

                # Perform Ship movement

                # Perform Fire action

            else:
                pass

        elif game_state is cCommonGame.GameState.PLAY_COMPUTE:
            # do nothing
            print("Server is processing...")
            time.sleep(2)

        elif game_state is cCommonGame.GameState.STOP:
            # do nothing
            print("Game has ended...")
            time.sleep(1)

    else:
        print("Unexpected input parameters")


    # # map_x_len = 0
    # # map_y_len = 0
    # 
    # # Test 1: Register four client to get the data map
    # test_reply = client_comm_engine.req_register()
    # if isinstance(test_reply, cMessages.MsgRepAckMap):
    #     print(test_reply)
    #     assert (test_reply.ack is True)
    #     # map_x_len, map_y_len = np.shape(test_reply.map_data)
    #     print("Client %s: Recv Map Size: %s" % (player_id, np.shape(test_reply.map_data)))
    # else:
    #     print("Incorrect Msg type : %s" % test_reply)
    # assert(isinstance(test_reply, cMessages.MsgRepAckMap))
    # 
    # 
    # # Test 2: Register the ships for the four client
    # ship_list = []
    # for ship_id in range(3):
    #     ship_info = cCommonGame.ShipInfo(ship_id=ship_id,
    #                                      ship_type=cCommonGame.ShipType.MIL,
    #                                      position=cCommonGame.Position(
    #                                          int(np.random.random_integers(boundary[0][0] + 3, boundary[0][1] - 3)),
    #                                          int(np.random.random_integers(boundary[1][0] + 3, boundary[1][1] - 3))),
    #                                      heading=0,
    #                                      size=3,
    #                                      is_sunken=False)
    #     if ship_id == 1:
    #         ship_info.position.x = boundary[0][0] + 0
    #         ship_info.position.y = boundary[1][0] + ((ship_info.size - 1) // 2)
    #         ship_info.heading = 0
    #     ship_list.append(ship_info)
    # 
    # uw_ship_list = []
    # ship_list.append(cCommon.UwShipInfo(ship_id=1,
    #                                     position=cCommonGame.Position(boundary[0][0],
    #                                                                   boundary[0][1])))
    # 
    # test_reply = client_comm_engine.req_register_ships(ship_list=ship_list,
    #                                                    uw_ship_list=uw_ship_list)
    # if isinstance(test_reply, cMessages.MsgRepAck):
    #     print(test_reply)
    #     assert (test_reply.ack == True)
    # else:
    #     print("Incorrect Msg type")
    # assert(isinstance(test_reply, cMessages.MsgRepAck))
    # 
    # # Test 3: Get the Game Configuration from the server
    # game_config_list = dict()
    # if isinstance(client_comm_engine, ClientCommEngine):
    #     test_reply = client_comm_engine.req_config()
    #     if isinstance(test_reply, cMessages.MsgRepGameConfig):
    #         print(test_reply)
    #         assert (test_reply.ack == True)
    #         game_config_list[player_id] = test_reply
    #     else:
    #         print("Incorrect Msg type")
    #     assert(isinstance(test_reply, cMessages.MsgRepGameConfig))
    # 
    # game_status = client_comm_engine.recv_from_publisher()
    # while game_status is None:
    #     print("game status is None")
    #     time.sleep(1)
    #     game_status = client_comm_engine.recv_from_publisher()
    # 
    # while game_status.get_enum_game_state() == cCommonGame.GameState.INIT:
    #     print("game status is INIT")
    #     time.sleep(1)
    #     game_status = client_comm_engine.recv_from_publisher()
    # 
    # round_offset = 0
    # # # Test timeout for round 1
    # # game_status = client_comm_engine.recv_from_publisher()
    # # while game_status.game_round < 2:
    # #     print("*** *** Round %s - Turn %s - Time remain %s" % (game_status.game_round,
    # #                                                            game_status.player_turn,
    # #                                                            game_status.time_remain))
    # #     time.sleep(1)
    # #     game_status = client_comm_engine.recv_from_publisher()
    # # round_offset = round_offset + 1
    # 
    # 
    # # Test 4: Test Game Play
    # for rounds_cnt in range(num_of_rounds):
    # 
    #     # Wait until new round has started
    #     game_status = client_comm_engine.recv_from_publisher()
    #     while game_status.game_round == (rounds_cnt + round_offset) and \
    #             game_status.get_enum_game_state() != cCommonGame.GameState.STOP:
    #         game_status = client_comm_engine.recv_from_publisher()
    # 
    #     print("*** *** Round %s - Turn %s - Time remain %s" % (game_status.game_round,
    #                                                            game_status.player_turn,
    #                                                            game_status.time_remain))
    # 
    #     if isinstance(client_comm_engine, ClientCommEngine):
    #         # Test 4 i  : Get the Game Turn from the server
    #         test_reply = client_comm_engine.req_turn_info()
    #         if (game_status.get_enum_game_state() != cCommonGame.GameState.STOP) and \
    #                 isinstance(test_reply, cMessages.MsgRepTurnInfo):
    #             print("%s/%s - %s" % (game_status.player_turn, player_id, test_reply))
    #             assert (test_reply.ack is True)
    #             # if game_status.player_turn == player_id:
    #             #     assert (test_reply.ack is True)
    #             # else:
    #             #     assert (test_reply.ack is False)
    #         elif (game_status.get_enum_game_state() == cCommonGame.GameState.STOP) and \
    #                 isinstance(test_reply, cMessages.MsgRepAck):
    #             print("%s/%s - %s" % (game_status.player_turn, player_id, test_reply))
    #             assert (test_reply.ack is False)
    #         else:
    #             print("Incorrect Msg type: %s/%s - %s %s" % (game_status.player_turn,
    #                                                          player_id,
    #                                                          test_reply,
    #                                                          type(test_reply)))
    # 
    #         if game_status.get_enum_game_state() != cCommonGame.GameState.STOP:
    #             assert(isinstance(test_reply, cMessages.MsgRepTurnInfo))
    #         else:
    #             assert (isinstance(test_reply, cMessages.MsgRepAck))
    # 
    #         # Test 4 ii : Request satcom action
    #         satcom_act = cCommonGame.SatcomInfo(6378 + 2000, 0, 5, 0, 150, 0, True, False)
    #         test_reply = client_comm_engine.req_action_satcom(satcom_act)
    #         if (game_status.get_enum_game_state() != cCommonGame.GameState.STOP) and \
    #                 isinstance(test_reply, cMessages.MsgRepAckMap):
    #             print("%s/%s - %s" % (game_status.player_turn, player_id, test_reply))
    #             if game_config_list[player_id].config.en_satellite:
    #                 assert (test_reply.ack is True)
    #             else:
    #                 assert (test_reply.ack is False)
    #             # if (game_status.player_turn == player_id) and \
    #             #         (game_config_list[player_id].config.en_satellite):
    #             #     assert (test_reply.ack is True)
    #             # else:
    #             #     assert (test_reply.ack is False)
    #         elif (game_status.get_enum_game_state() == cCommonGame.GameState.STOP) and \
    #              isinstance(test_reply, cMessages.MsgRepAck):
    #             print("%s/%s - %s" % (game_status.player_turn, player_id, test_reply))
    #             assert (test_reply.ack is False)
    #         else:
    #             print("Incorrect Msg type: %s/%s - %s %s" % (game_status.player_turn,
    #                                                          player_id,
    #                                                          test_reply,
    #                                                          type(test_reply)))
    # 
    #         if game_status.get_enum_game_state() != cCommonGame.GameState.STOP:
    #             assert (isinstance(test_reply, cMessages.MsgRepAckMap))
    #         else:
    #             assert (isinstance(test_reply, cMessages.MsgRepAck))
    # 
    #         # Test 4 iii: Get the Game Turn from the server with satcom
    #         test_reply = client_comm_engine.req_turn_info()
    #         if (game_status.get_enum_game_state() != cCommonGame.GameState.STOP) and \
    #                 isinstance(test_reply, cMessages.MsgRepTurnInfo):
    #             print("%s/%s - %s" % (game_status.player_turn, player_id, test_reply))
    #             assert (test_reply.ack is True)
    #             # if game_status.player_turn == player_id:
    #             #     assert (test_reply.ack is True)
    #             # else:
    #             #     assert (test_reply.ack is False)
    #         elif (game_status.get_enum_game_state() == cCommonGame.GameState.STOP) and \
    #                 isinstance(test_reply, cMessages.MsgRepAck):
    #             print("%s/%s - %s" % (game_status.player_turn, player_id, test_reply))
    #             assert (test_reply.ack is False)
    #         else:
    #             print("Incorrect Msg type: %s/%s - %s %s" % (game_status.player_turn,
    #                                                          player_id,
    #                                                          test_reply,
    #                                                          type(test_reply)))
    # 
    #         if game_status.get_enum_game_state() != cCommonGame.GameState.STOP:
    #             assert(isinstance(test_reply, cMessages.MsgRepTurnInfo))
    #         else:
    #             assert (isinstance(test_reply, cMessages.MsgRepAck))
    # 
    #         # Test 4 iv : Request uw report / action
    #         test_reply = client_comm_engine.req_uw_report(ship_id=1)
    #         if isinstance(test_reply, cMessages.MsgRepUwReport):
    #             print("%s/%s - %s" % (game_status.player_turn, player_id, test_reply))
    #         elif (game_status.get_enum_game_state() == cCommonGame.GameState.STOP) and \
    #                 isinstance(test_reply, cMessages.MsgRepAck):
    #             print("%s/%s - %s" % (game_status.player_turn, player_id, test_reply))
    #         else:
    #             print("Incorrect Msg type: %s/%s - %s %s" % (game_status.player_turn,
    #                                                          player_id,
    #                                                          test_reply,
    #                                                          type(test_reply)))
    #         if game_status.get_enum_game_state() != cCommonGame.GameState.STOP:
    #             assert (isinstance(test_reply, cMessages.MsgRepUwReport))
    #         else:
    #             assert (isinstance(test_reply, cMessages.MsgRepAck))
    # 
    #         if isinstance(test_reply, cMessages.MsgRepUwReport) and (test_reply.ack is True):
    #             # send new order to the server
    #             ship_1_uw_action_list = list()
    #             ship_1_uw_action_list.append(cCommonGame.UwActionMoveScan(
    #                 goto_pos=cCommonGame.Position(int((boundary[0][0] + boundary[1][0]) // 2),
    #                                               int((boundary[1][0] + boundary[1][1]) // 2)),
    #                 scan_dur=10))
    #             ship_2_uw_action_list = list()
    #             ship_2_uw_action_list.append(cCommonGame.UwActionMoveScan(
    #                 goto_pos=cCommonGame.Position(int((boundary[0][0] + boundary[1][0]) // 2),
    #                                               int((boundary[1][0] + boundary[1][1]) // 2)),
    #                 scan_dur=10))
    #             uw_move_info_list = list()
    #             uw_move_info_list.append(cCommonGame.UwShipMovementInfo(ship_id=1,
    #                                                                     actions=ship_1_uw_action_list))
    #             uw_move_info_list.append(cCommonGame.UwShipMovementInfo(ship_id=2,
    #                                                                     actions=ship_2_uw_action_list))
    #             test_reply = client_comm_engine.req_action_uw_ops(uw_move_info_list)
    #             assert (isinstance(test_reply, cMessages.MsgRepAck))
    #         # else do nothing
    # 
    #         # Test 4  v : Request move action
    #         move_list = list()
    #         move_list.append(cCommonGame.ShipMovementInfo(1, cCommonGame.Action.FWD))
    #         move_list.append(cCommonGame.ShipMovementInfo(1, cCommonGame.Action.CW))
    #         test_reply = client_comm_engine.req_action_move(move_list)
    #         if isinstance(test_reply, cMessages.MsgRepAck):
    #             print("%s/%s - %s" % (game_status.player_turn, player_id, test_reply))
    #             if game_status.get_enum_game_state() != cCommonGame.GameState.STOP:
    #                 assert (test_reply.ack is True)
    #             else:
    #                 assert (test_reply.ack is False)
    #             # if game_status.get_enum_game_state() != cCommonGame.GameState.STOP and \
    #             #         game_status.player_turn == player_id:
    #             #     assert (test_reply.ack is True)
    #             # else:
    #             #     assert (test_reply.ack is False)
    #         else:
    #             print("Incorrect Msg type: %s/%s - %s %s" % (game_status.player_turn,
    #                                                          player_id,
    #                                                          test_reply,
    #                                                          type(test_reply)))
    # 
    #         assert (isinstance(test_reply, cMessages.MsgRepAck))
    # 
    # 
    #         # Test 4 vi : Request fire action
    #         fire_list = list()
    #         fire_list.append(cCommonGame.FireInfo(cCommonGame.Position(0, 0)))
    #         test_reply = client_comm_engine.req_action_fire(fire_list)
    #         if isinstance(test_reply, cMessages.MsgRepAck):
    #             print("%s/%s - %s" % (game_status.player_turn, player_id, test_reply))
    #             if game_status.get_enum_game_state() != cCommonGame.GameState.STOP:
    #                 assert (test_reply.ack is True)
    #             else:
    #                 assert (test_reply.ack is False)
    #             # if game_status.get_enum_game_state() != cCommonGame.GameState.STOP and \
    #             #         game_status.player_turn == player_id:
    #             #     assert (test_reply.ack is True)
    #             # else:
    #             #     assert (test_reply.ack is False)
    #         else:
    #             print("%s/%s - %s" % (game_status.player_turn, player_id, test_reply))
    #             print("Incorrect Msg type")
    # 
    #         assert (isinstance(test_reply, cMessages.MsgRepAck))
    # 
    # 
    # 
    # 
    # pass

def wos_fake_player(player_id=2):

    print("start : wos_fake_player ---------------")
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

    print("Client %s Comm Engine: READY..." % player_id)

    pub_data = client_comm_engine.recv_from_publisher()
    last_round_count = 0
    while pub_data.get_enum_game_state() is not cCommonGame.GameState.STOP:

        if last_round_count is not pub_data.game_round:
            wos_test_client(client_comm_engine=client_comm_engine,
                            game_state=pub_data.get_enum_game_state(),
                            round_count=pub_data.game_round)
            last_round_count = pub_data.game_round
        else:
            print("Waiting for other players")
            time.sleep(5)

        pub_data = client_comm_engine.recv_from_publisher()

    # Teardown
    client_comm_engine.stop()
    print("exit  : wos_fake_player ---------------")


# # ---------------------------------------------------------------------------
# def load_server_setting(filename):
#     game_setting = None
#     try:
#         with open(filename) as infile:
#             game_setting = json.load(infile, cls=SvrCfgJsonDecoder)
#     except:
#         print("Unable to load server setting")
#
#     return game_setting


# ---------------------------------------------------------------------------
if __name__ == '__main__':
    print("*** %s (%s)" % (__file__, time.ctime(time.time())))
    is_running = True

    wos_fake_player(2)

    print("*** END (%s)" % (time.ctime(time.time())))
