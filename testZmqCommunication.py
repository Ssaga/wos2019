import threading
import time
import collections
import numpy as np

from cClientCommEngine import ClientCommEngine
from cServerCommEngine import ServerCommEngine
from cCommonCommEngine import ConnInfo
from cCommonGame import Position, UwActionMoveScan
from cCommonGame import Action
from cCommonGame import GameStatus
from cCommonGame import GameState
from cCommonGame import ShipInfo
from cCommonGame import FireInfo
from cCommonGame import ShipMovementInfo
from cCommonGame import SatcomInfo
from cCommonGame import ShipType
from cCommonGame import UwShipInfo
from cCommonGame import UwActionMoveScan
# from cCommonGame import UwActionScan
# from cCommonGame import UwActionNop
import cMessages

run_count = 0
total_turn_cnt = 4
total_round_cnt = 1
total_exec_cnt = (total_round_cnt * total_turn_cnt) + total_turn_cnt
bc_rate = 500  # unit in milliseconds
polling_rate = 500  # unit in milliseconds


# ---------------------------------------------------------------------
#
def server_thread(commEngine=ServerCommEngine()):
    print("*** server commEngine thread start ***")
    global is_running
    global run_count
    commEngine.start()
    while (is_running == True):
        perform_server_task(commEngine, run_count)
    commEngine.stop()
    print("*** server commEngine thread exit ***")


def perform_server_task(server_comm_engine, cnt):
    if cnt < total_turn_cnt:
        ### when the game status is in init
        game_status = GameStatus(GameState.INIT)
    elif cnt < total_exec_cnt:
        ### when the game status is in play
        # Set the broadcast message
        game_status = GameStatus(GameState.PLAY_COMPUTE,
                                 ((cnt - total_turn_cnt) // total_turn_cnt + 1),
                                 ((cnt - total_turn_cnt) % total_turn_cnt + 1))
    else:
        ### when the game status is in end
        game_status = GameStatus(GameState.STOP)

    # Update the publisher
    server_comm_engine.set_game_status(game_status)

    # Receive the request from the client and send a reply
    msg = server_comm_engine.recv()

    # TODO: Process and generate the reply
    if isinstance(msg, collections.Iterable):
        msg_addr = None
        msg_req = None
        if len(msg) > 1:
            msg_addr = msg[0]
            msg_req = msg[1]

        if (msg_req is not None) and issubclass(type(msg_req), cMessages.MsgReq):
            msg_rep = None
            if msg_req.type_id == 0:
                print("\tServer: RECV: Request Register")
                map_data = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
                msg_rep = cMessages.MsgRepAckMap(True, map_data)
            elif msg_req.type_id == 2:
                print("\tServer: RECV: Request Game Configure")
                msg_rep = cMessages.MsgRepAck(True)
            elif msg_req.type_id == 3:
                print("\tServer: RECV: Request Turn Info")
                self_ship_list = list()
                self_ship_list.append(ShipInfo(1, Position(1, 1), 0, 1, False))
                self_ship_list.append(ShipInfo(2, Position(2, 2), 90, 2, False))
                self_ship_list.append(ShipInfo(3, Position(3, 3), 180, 2, False))

                enemy_ship_list = list()
                enemy_ship_list.append(ShipInfo(1, Position(1, 1), 180, 1, False))
                enemy_ship_list.append(ShipInfo(2, Position(2, 2), 270, 2, False))
                enemy_ship_list.append(ShipInfo(3, Position(3, 3), 0, 2, False))

                other_ship_list = list()
                other_ship_list.append(ShipInfo(ship_id=1,
                                                position=Position(1, 1),
                                                heading=0,
                                                size=1,
                                                is_sunken=False,
                                                ship_type=ShipType.CIV))
                other_ship_list.append(ShipInfo(ship_id=2,
                                                position=Position(2, 2),
                                                heading=90,
                                                size=2,
                                                is_sunken=False,
                                                ship_type=ShipType.CIV))
                other_ship_list.append(ShipInfo(ship_id=3,
                                                position=Position(3, 3),
                                                heading=180,
                                                size=2,
                                                is_sunken=False,
                                                ship_type=ShipType.CIV))
                self_uw_ship_list = list()
                self_uw_ship_list.append(UwShipInfo(1, Position(1, 1)))
                self_uw_ship_list.append(UwShipInfo(2, Position(2, 2)))

                bombardment_list = list()
                bombardment_list.append(Position(0, 0))
                bombardment_list.append(Position(1, 1))

                msg_rep = cMessages.MsgRepTurnInfo(True,
                                                   self_ship_list,
                                                   self_uw_ship_list,
                                                   enemy_ship_list,
                                                   other_ship_list,
                                                   bombardment_list,
                                                   [[1, 1, 1, 1],
                                                    [1, 0, 0, 1],
                                                    [1, 0, 0, 1],
                                                    [1, 1, 1, 1]])
            elif msg_req.type_id == 6:
                print("\tServer: RECV: Request satcom action")
                map_data = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
                msg_rep = cMessages.MsgRepAckMap(True, map_data)

            elif msg_req.type_id == 7:
                print("\tServer: RECV: Request UW report")
                report = list()
                for i in range(8):
                    data = list()
                    for j in range(8):
                        data.append(np.ones(50).tolist())
                    report.append(data)
                msg_rep = cMessages.MsgRepUwReport(True, report)

            else:
                ack = True
                if msg_req.type_id == 1:
                    print("\tServer: RECV: Request Ship registration")
                elif msg_req.type_id == 4:
                    print("\tServer: RECV: Request move action")
                elif msg_req.type_id == 5:
                    print("\tServer: RECV: Request fire action")
                elif msg_req.type_id == 7:
                    print("\tServer: RECV: Request UW action")
                else:
                    ack = False
                msg_rep = cMessages.MsgRepAck(ack)

            # Send reply
            server_comm_engine.send(addr=msg_addr, msg=msg_rep)
        else:
            print("Server did not receive any data")
    else:
        print("Server did not receive incorrect data")


# ---------------------------------------------------------------------
#
def client_thread(commEngine=ClientCommEngine()):
    print("*** client %s commEngine thread start ***" % commEngine.client_id)
    global is_running
    commEngine.start()
    while (is_running == True):
        time.sleep(1)
    commEngine.stop()
    print("*** client %s commEngine thread exit ***" % commEngine.client_id)


# ---------------------------------------------------------------------
#
def perform_client_task(list_client_comm_engine, cnt):
    global total_turn_cnt
    global total_round_cnt
    player_turn = cnt % total_turn_cnt
    round_num = (cnt - total_turn_cnt) // total_turn_cnt + 1
    print("Round %s... Turn %s..." % (round_num, player_turn + 1))

    # Print publisher data
    obj = list_client_comm_engine[player_turn].recv_from_publisher()
    if (obj is not None):
        print("*** Recv Fr Publisher: %s" % obj.__dict__)
    else:
        print("*** Recv Fr Publisher: -- No Publish --")

    # Sending request to the server for reply
    if cnt < total_turn_cnt:
        # when the game status is in init
        rep = list_client_comm_engine[player_turn].req_register()
        if rep is not None:
            print(vars(rep))
        else:
            print("No reply from server")

        ship_list = list()
        ship_list.append(ShipInfo(1, Position(36, 20), 0, 3, False))
        ship_list.append(ShipInfo(2, Position(2, 2), 90, 3, False))

        uw_ship_list = list()
        uw_ship_list.append(UwShipInfo(1, Position(10, 10)))
        uw_ship_list.append(UwShipInfo(1, Position(20, 20)))

        rep = list_client_comm_engine[player_turn].req_register_ships(ship_list,
                                                                      uw_ship_list)
        if rep is not None:
            print(vars(rep))
        else:
            print("No reply from server")

    # elif cnt < (total_round_cnt * total_turn_cnt) + total_turn_cnt:
    elif cnt < total_exec_cnt:
        # when the game status is in play
        # Req turn info
        rep = list_client_comm_engine[player_turn].req_turn_info()
        if rep is None:
            print("No valid reply from server")
        else:
            print(vars(rep))
        # Satcom
        rep = list_client_comm_engine[player_turn].req_action_satcom(
            SatcomInfo(1, 2, 3, 4, 5, 6, False, False))
        if rep is None:
            print("No valid reply from server")
        else:
            print(vars(rep))
        # Move ship
        # move_action = []
        # move_action.append(ShipMovementInfo(1, Action.FWD))
        # move_action.append(ShipMovementInfo(1, Action.CW))
        rep = list_client_comm_engine[player_turn].req_action_move([ShipMovementInfo(1, Action.FWD),
                                                                    ShipMovementInfo(2, Action.CW)])
        if rep is None:
            print("No valid reply from server")
        else:
            print(vars(rep))

        # Fire at the enemy
        # fire_action = []
        # fire_action.append(FireInfo(Position(1, 1)))
        # fire_action.append(FireInfo(Position(2, 2)))
        rep = list_client_comm_engine[player_turn].req_action_fire([FireInfo(Position(1, 1)),
                                                                    FireInfo(Position(2, 2))])
        if rep is None:
            print("No valid reply from server")
        else:
            print(vars(rep))

        # Req UW
        uw_ops = list()
        uw_ops.append(UwActionMoveScan(goto_pos=Position(1, 1),
                                       scan_dur=1))
        uw_ops.append(UwActionMoveScan(scan_dur=1))
        uw_ops.append(UwActionMoveScan())

        rep = list_client_comm_engine[player_turn].req_action_uw_ops(uw_ops)
        if rep is None:
            print("No valid reply from server")
        else:
            print(vars(rep))

        # Req uw report
        rep = list_client_comm_engine[player_turn].req_uw_report()
        if rep is None:
            print("No valid reply from server")
        else:
            print(vars(rep))

        # Req turn info
        rep = list_client_comm_engine[player_turn].req_turn_info()
        if rep is None:
            print("No valid reply from server")
        else:
            print(vars(rep))
    else:
        # when the game status is in end
        pass


# ---------------------------------------------------------------------
if __name__ == '__main__':
    # client_id = 1
    addr_svr = "127.0.0.1"
    port_req = 5556
    port_sub = 5557

    req_rep_if = ConnInfo(addr_svr, port_req)
    pub_sub_if = ConnInfo(addr_svr, port_sub)

    is_running = True

    print("tesing code --------")
    # server
    server_comm_engine = ServerCommEngine(req_rep_if, pub_sub_if, polling_rate, bc_rate)
    thread_server = threading.Thread(name='server-thread',
                                     target=server_thread,
                                     args=(server_comm_engine,))
    thread_server.start()

    # client
    list_thread_client = []
    list_client_comm_engine = []
    for i in range(1, total_turn_cnt + 1):
        print("Creating Client Id: %s" % i)
        client_comm_engine = ClientCommEngine(i, req_rep_if, pub_sub_if, polling_rate)
        thread_client = threading.Thread(name='client-thread',
                                         target=client_thread,
                                         args=(client_comm_engine,))
        thread_client.start()
        list_client_comm_engine.append(client_comm_engine)
        list_thread_client.append(thread_client)

    # wait for the server commEngine to be ready
    while (not server_comm_engine.is_ready):
        print("Waiting for server commEngine")
        time.sleep(1)

    # wait for the client commEngine to be ready
    for client_comm_engine in list_client_comm_engine:
        while (not client_comm_engine.is_ready):
            print("Waiting for client %s commEngine..." % client_comm_engine.client_id)
            time.sleep(1)

    # Waiting execution
    # for i in range(0, (total_round_cnt * total_turn_cnt) + total_turn_cnt):
    sleep_dur = bc_rate / 1000
    for i in range(0, 10):
        time.sleep(sleep_dur)
        print("%s *** count %s..." % (time.ctime(time.time()), i))
        run_count = i
        perform_client_task(list_client_comm_engine, i)

    is_running = False
    for thread_client in list_thread_client:
        thread_client.join()
    thread_server.join()

    print("exit ---------------")
