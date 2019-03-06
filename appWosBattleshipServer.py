import time
import json
import numpy as np
import threading
import logging
import collections
import copy
import signal

from cServerCommEngine import ServerCommEngine
from wosBattleshipServer.cCmdCommEngineSvr import CmdServerCommEngine

from cCommonGame import MapData
from cCommonGame import Position
from cCommonGame import Size
from cCommonGame import Boundary
from cCommonGame import GameState
from cCommonGame import GameStatus
from cCommonGame import GameConfig
from cCommonGame import ShipInfo
from cCommonGame import ShipMovementInfo
from cCommonGame import FireInfo
from cCommonGame import SatcomInfo
from cCommonGame import Action
from cCommonGame import ShipType

from wosBattleshipServer.funcIslandGeneration import island_generation
from wosBattleshipServer.funcCloudGeneration import cloud_generation
from wosBattleshipServer.funcCloudGeneration import cloud_change
from wosBattleshipServer.funcCivilianShipsGeneration import civilian_ship_generation
from wosBattleshipServer.funcCivilianShipsMovement import civilian_ship_movement
from wosBattleshipServer.funcSatcomScan import satcom_scan

from wosBattleshipServer.cCommon import PlayerStatus
from wosBattleshipServer.cCommon import PlayerTurnActionCount
from wosBattleshipServer.cCommon import GameTurnStatus
from wosBattleshipServer.cCommon import ServerGameConfig
from wosBattleshipServer.cCommon import SvrCfgJsonDecoder
from wosBattleshipServer.cCommon import SvrCfgJsonEncoder
from wosBattleshipServer.cCommon import check_collision
from wosBattleshipServer.cCommon import ServerFireInfo

from wosBattleshipServer.cTtsCommEngineSvr import TtsServerCommEngine

import cMessages


# Global Variable  ---------------------------------------------------------
flag_quit_game = False


# Global Function  ---------------------------------------------------------
def signal_handler(sig, frame):
    global flag_quit_game
    flag_quit_game = True


# --------------------------------------------------------------------------
class WosBattleshipServer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        # Lock for the comm_engine
        self.comm_engine_lock = threading.RLock()

        # Thread Setup --------------------------------------------------------------
        # load the game setting
        self.game_setting = self.load_server_setting("game_server.cfg")
        # setup the communication engine
        self.comm_engine = ServerCommEngine(self.game_setting.req_rep_conn,
                                            self.game_setting.pub_sub_conn,
                                            self.game_setting.polling_rate,
                                            self.game_setting.bc_rate)
        self.tts_comm_engine = TtsServerCommEngine()
        self.is_running = False
        self.flag_end_game = False
        self.flag_restart_game = False

        # Added by ttl, 2019-01-13
        self.turn_timestamp = 0
        self.flag_turn_timeout = False
        # end of modification

        num_move_act = self.game_setting.num_move_act
        num_fire_act = self.game_setting.num_fire_act
        num_satcom_act = self.game_setting.num_satcom_act
        if not self.game_setting.en_satellite:
            num_satcom_act = 0
        self.game_status = GameTurnStatus(GameState.INIT, num_move_act, num_fire_act, num_satcom_act)

        ## Added by ttl, 2019-01-31
        self.player_remaining_action_dict = dict()
        ## End of modification

        # Players data
        # player_status_list is a dictionary of PlayerStatus class
        # dict: {'<player_id>': PlayerStatus}
        self.player_status_dict = dict()
        # # player_curr_fire_cmd_dict & player_prev_fire_cmd_dict are a dictionary of
        # # 	FireInfo class
        # # dict: {'<player_id>': FireInfo}
        # self.player_curr_fire_cmd_dict = dict()
        # self.player_prev_fire_cmd_dict = dict()
        # player_curr_fire_cmd_list & player_prev_fire_cmd_list are a list of
        # 	ServerFireInfo class
        # list: {ServerFireInfo}
        self.player_curr_fire_cmd_list = list()
        self.player_prev_fire_cmd_list = list()
        # player_mask_layer is a dictionary of 2D list
        # dict: {'<player_id>': [[<row 1 mask list>],[<row 2 mask list>], ...]}
        self.player_boundary_layer = dict()
        # player_fog_layer is a dictionary of 2D list
        # dict: {'<player_id>': [[<row 1 mask list>],[<row 2 mask list>], ...]}
        self.player_fog_layer = dict()
        # player_boundary_dict is a dictionary of 2D list
        # dict: {'<player_id>': [[<min_x>, <max_x>],[<min_y>,<max_y>]]}
        self.player_boundary_dict = dict()

        # turn_map_fog is a dictionary of 2D list
        # dict: {'<player_id>': np.array of type:np.int}
        self.turn_map_fog = dict()

        # Dictionary to store the satcom mask and option for each user
        self.last_satcom_mask = dict()
        self.last_satcom_enable = dict()

        # Dictionary to store the history informaiton of the enemy ship list
        self.hist_enemy_data_dict = dict()

        # Game Setup --------------------------------------------------------------
        # Generate the array required
        self.island_layer = np.zeros((self.game_setting.map_size.x, self.game_setting.map_size.y), dtype=np.int)
        self.cloud_layer = np.zeros((self.game_setting.map_size.x, self.game_setting.map_size.y), dtype=np.int)
        self.civilian_ship_list = list()
        self.civilian_ship_layer = np.zeros((self.game_setting.map_size.x, self.game_setting.map_size.y), dtype=np.int)

        # Generate the round state for each player
        for i in range(self.game_setting.num_of_player):
            self.player_remaining_action_dict[i + 1] = PlayerTurnActionCount(0, 0, 0)

        # Generate Player mask
        self.generate_player_mask(self.player_boundary_layer, self.player_boundary_dict)
        print("Player mask: ---------------------------------------------")
        for mask_key in self.player_boundary_layer.keys():
            print("Player mask: %s" % mask_key)
            print(self.player_boundary_layer[mask_key].T)

        # Generate the players' fog
        for key in self.player_boundary_layer.keys():
            value = np.where(self.player_boundary_layer[key] > 0, 0, int(MapData.FOG_OF_WAR))
            value = value.astype(np.int)
            self.player_fog_layer[key] = value

        for key in self.player_fog_layer.keys():
            print("Player Fog: %s" % key)
            print(self.player_fog_layer[key].T)

        # Generate the island on the map
        for key in self.player_boundary_dict:
            player_boundary_dict = self.player_boundary_dict[key]
            player_map_portion = self.island_layer[
                                 player_boundary_dict.min_x:player_boundary_dict.max_x,
                                 player_boundary_dict.min_y:player_boundary_dict.max_y]
            island_generation(player_map_portion, self.game_setting.island_coverage)
        self.island_layer = self.island_layer.astype(np.int)
        self.island_layer = self.island_layer * MapData.ISLAND
        print("Island data: ---------------------------------------------")
        print(self.island_layer.T)

        # Generate the cloud
        cloud_generation(self.cloud_layer,
                         self.game_setting.cloud_coverage,
                         self.game_setting.cloud_seed_cnt)
        self.cloud_layer = self.cloud_layer.astype(np.int)
        print("Cloud data: ---------------------------------------------")
        print(self.cloud_layer.T)

        # Generate the civilian ships
        for key in self.player_boundary_dict:
            player_boundary_dict = self.player_boundary_dict[key]
            civilian_ship_generation(self.civilian_ship_list,
                                     self.island_layer,
                                     player_boundary_dict,
                                     self.game_setting.civilian_ship_count)

        # Update the ship layer
        for civilian_ship in self.civilian_ship_list:
            if isinstance(civilian_ship, ShipInfo) and (civilian_ship.is_sunken == False):
                for pos in civilian_ship.area:
                    self.civilian_ship_layer[int(pos[0]),int(pos[1])] = 1

        print("Civilian data: ---------------------------------------------")
        print(self.civilian_ship_list)
        print(self.civilian_ship_layer.T)

    def stop(self):
        self.is_running = False

    def end_game(self):
        self.flag_end_game = True

    def restart_game(self):
        self.flag_restart_game = True

    def clear_user(self):
        if self.game_status.game_state == GameState.INIT:
            self.player_status_dict.clear()
            # self.player_curr_fire_cmd_dict.clear()
            # self.player_prev_fire_cmd_dict.clear()
            self.player_curr_fire_cmd_list.clear()
            self.player_prev_fire_cmd_list.clear()
        else:
            print("Unable to clear users as the game has started")

    def run(self):
        self.is_running = True

        # start the communication engine
        self.comm_engine.start()
        self.tts_comm_engine.start()

        while self.is_running:
            # Wait for data from the client
            msg = self.comm_engine.recv()

            # Update the remaining time for the turn
            self.update_countdown_time()

            state_changed = self.state_get_next()
            if state_changed:
                print("State Change to %s" % self.game_status.game_state)
                self.state_setup()
                state_changed = False

            # self.state_exec(msg)
            # Perform the state exec as a thread
            if msg is not None:
                # Get the address and data
                if len(msg) >= 2:
                    msg_addr = msg[0]
                    msg_data = msg[1]

                    thread = threading.Thread(target=self.state_exec, args=(msg_addr, msg_data))
                    thread.start()

            # Bugfix: Update the remaining time of the game state if we are in play input state
            #         This has occurred as we now check if we have message before we perform execute
            if self.game_status.game_state == GameState.PLAY_INPUT:
                # Update the publisher on the game status
                bc_game_status = GameStatus(self.game_status.game_state,
                                            self.game_status.game_round,
                                            0,
                                            self.game_status.time_remaining)
                self.comm_engine.set_game_status(bc_game_status)

        # stop the communication engine
        self.tts_comm_engine.stop()
        self.comm_engine.stop()

    def update_countdown_time(self):
        self.flag_turn_timeout = False
        if self.game_status.game_state == GameState.PLAY_INPUT:
            diff = time.time() - self.turn_timestamp
            if diff < 0:
                # we went back in time
                self.turn_timestamp = time.time()
            elif diff >= self.game_setting.countdown_duration:
                self.game_status.time_remaining = 0
                self.flag_turn_timeout = True
            else:
                self.game_status.time_remaining = self.game_setting.countdown_duration - diff
        else:
            self.game_status.time_remaining = 0

    # ---------------------------------------------------------------------------
    # State machine for the server...
    def state_get_next(self):
        state_changed = False
        if self.game_status.game_state == GameState.INIT:
            state_changed = self.state_get_next_init()
        elif self.game_status.game_state == GameState.PLAY_INPUT:
            state_changed = self.state_get_next_play_input()
        elif self.game_status.game_state == GameState.PLAY_COMPUTE:
            state_changed = self.state_get_next_play_compute()
        elif self.game_status.game_state == GameState.STOP:
            state_changed = self.state_get_next_stop()
        else:
            print("Unsupported state")

        # Just reset the "restart flag"
        self.flag_restart_game = False

        return state_changed

    def state_get_next_init(self):
        state_changed = False
        # check if all the player has registered
        # print("********** %s %s" % (len(self.player_status_list), self.game_setting.num_of_player))
        if len(self.player_status_dict) >= self.game_setting.num_of_player:
            self.game_status.game_state = GameState.PLAY_INPUT
            state_changed = True
        else:
            print("Waiting for %s remaining player registeration" % (
                    self.game_setting.num_of_player - len(self.player_status_dict)))
        return state_changed

    def state_get_next_play_input(self):
        state_changed = False

        total_remaining_action = 0
        for player_id in self.player_remaining_action_dict.keys():
            remaining_action = self.player_remaining_action_dict.get(player_id)
            if isinstance(remaining_action, PlayerTurnActionCount):
                total_remaining_action += (remaining_action.remain_move + remaining_action.remain_fire + remaining_action.remain_satcom)
                print("********** Player %s remaining action %s = %s + %s + %s" % (
                    player_id, remaining_action, remaining_action.remain_move, remaining_action.remain_fire,
                    remaining_action.remain_satcom))

        print("********** Remaining total action %s | Timeout: %s [Remaining: %s]" %
              (total_remaining_action,
               self.flag_turn_timeout,
               self.game_status.time_remaining))

        if (total_remaining_action <= 0) or self.flag_turn_timeout:
            self.game_status.game_state = GameState.PLAY_COMPUTE
            state_changed = True

        return state_changed

    def state_get_next_play_compute(self):
        state_changed = True

        # set the default next state to PLAY_INPUT
        self.game_status.game_state = GameState.PLAY_INPUT

        # check if we have reach the end of the game
        if (self.game_status.game_round == self.game_setting.num_of_rounds) or self.flag_end_game:
            # time to end the game...
            self.game_status.game_state = GameState.STOP

        return state_changed

    def state_get_next_stop(self):
        state_changed = False
        if self.flag_restart_game:
            self.game_status.game_state == GameState.INIT
            state_changed = True

        return state_changed

    # ---------------------------------------------------------------------------
    def state_setup(self):
        if self.game_status.game_state == GameState.INIT:
            self.state_setup_init()
        elif self.game_status.game_state == GameState.PLAY_INPUT:
            self.state_setup_play_input()
        elif self.game_status.game_state == GameState.PLAY_COMPUTE:
            self.state_setup_play_compute()
        elif self.game_status.game_state == GameState.STOP:
            self.state_setup_stop()
        else:
            print("Unsupport game state")

    def state_setup_init(self):
        self.flag_end_game = False
        self.flag_restart_game = False
        self.game_status.player_turn = 0                    # Not used
        self.game_status.game_round = 0
        self.game_status.clear_turn_remaining_action()
        bc_game_status = GameStatus(self.game_status.game_state, self.game_status.game_round, 0)
        self.comm_engine.set_game_status(bc_game_status)

    def state_setup_play_input(self):
        # self.game_status.player_turn = (self.game_status.player_turn % self.game_setting.num_of_player) + 1
        self.game_status.player_turn = 0                    # Not used
        # self.game_status.reset_turn_remaining_action()
        # Reset the remaining action
        for player_id in self.player_remaining_action_dict.keys():
            self.player_remaining_action_dict[player_id].remain_satcom = self.game_status.allowed_action.remain_satcom
            self.player_remaining_action_dict[player_id].remain_fire = self.game_status.allowed_action.remain_fire
            self.player_remaining_action_dict[player_id].remain_move = self.game_status.allowed_action.remain_move


        # initial the mask required for this turn; for all the players
        for key in self.player_fog_layer.keys():
            self.turn_map_fog[key] = self.player_fog_layer[key]

        # Update the game round count
        self.game_status.game_round = self.game_status.game_round + 1

        # generate the cloud to be used for this round
        cloud_change(self.cloud_layer,
                     self.game_setting.cloud_coverage)
        self.cloud_layer = self.cloud_layer.astype(np.int)

        # generate new position of the civilian ships
        civilian_ship_movement(self.civilian_ship_list,
                               self.island_layer,
                               self.player_status_dict,
                               self.player_boundary_dict,
                               self.game_setting.civilian_ship_move_probility)

        # update the layer for the civilian ship
        self.civilian_ship_layer.fill(0)
        for civilian_ship in self.civilian_ship_list:
            if isinstance(civilian_ship, ShipInfo) and (civilian_ship.is_sunken == False):
                for pos in civilian_ship.area:
                    self.civilian_ship_layer[int(pos[0]), int(pos[1])] = 1

        # reset the current user satcom mask and its option
        for player_id in self.last_satcom_mask.keys():
            self.last_satcom_mask[player_id] = np.zeros((self.game_setting.map_size.x, self.game_setting.map_size.y), dtype=np.int)
            self.last_satcom_enable[player_id] = False

        # Added by ttl, 2019-01-14
        # make a copy of the enemy data list so that the data remain the same until it is the
        # players turn again
        # Update the enemy data list of the current player
        for player_id in self.player_status_dict.keys():
            enemy_data_list = [value for key, value in self.player_status_dict.items() if
                               key is not player_id]
            self.hist_enemy_data_dict[player_id] = copy.deepcopy(enemy_data_list)
        # end of modification

        # Update the position the player is hitting
        self.player_prev_fire_cmd_list.clear()
        self.player_prev_fire_cmd_list.extend(self.player_curr_fire_cmd_list)
        self.player_curr_fire_cmd_list.clear()
        # for player_id in self.player_curr_fire_cmd_dict.keys():
        #     self.player_prev_fire_cmd_dict[player_id] = self.player_curr_fire_cmd_dict.get(player_id)
        #     self.player_curr_fire_cmd_dict[player_id] = None

        # Added by ttl, 2019-01-13
        self.turn_timestamp = time.time()
        self.flag_turn_timeout = False
        self.game_status.time_remaining = self.game_setting.countdown_duration
        # end of modification

        # Update the publisher on the game status
        bc_game_status = GameStatus(self.game_status.game_state,
                                    self.game_status.game_round,
                                    0)
        self.comm_engine.set_game_status(bc_game_status)

    def state_setup_play_compute(self):
        # sort the player_prev_fire_cmd_list
        if len(self.player_prev_fire_cmd_list) > 0:
            self.player_prev_fire_cmd_list.sort(key=lambda x: x.timestamp)

        # Check if its previous fire hit any ships; if so, update the score and ship status
        for fire_cmd in self.player_prev_fire_cmd_list:
            if isinstance(fire_cmd, ServerFireInfo):
                player_status = self.player_status_dict[fire_cmd.player_id]
                self.state_setup_play_compute_fire(fire_cmd.player_id, fire_cmd.pos, player_status)

        # for player_id in self.player_status_dict.keys():
        #     player_status = self.player_status_dict[player_id]
        #
        #     # Perform the fire operation
        #     fire_cmds = self.player_prev_fire_cmd_dict.get(player_id)
        #     if isinstance(fire_cmds, collections.Iterable):
        #         for fire_cmd in fire_cmds:
        #             self.state_setup_play_compute_fire(player_id, fire_cmd, player_status)
        #     else:
        #         self.state_setup_play_compute_fire(player_id, fire_cmds, player_status)
        # bc_game_status = GameStatus(self.game_status.game_state, self.game_status.game_round, 0)
        # self.comm_engine.set_game_status(bc_game_status)

    def state_setup_play_compute_fire(self, player_id, pos, player_status):
        fire_pos = [pos.x, pos.y]
        player_radar_cross_table_index = player_id - 1
        for other_player_id, other_player_info in self.player_status_dict.items():
            if other_player_id is not player_id:
                for other_player_ship_info in other_player_info.ship_list:
                    if (not other_player_ship_info.is_sunken) and (fire_pos in other_player_ship_info.area):
                        # Compute if the ship has been hit
                        if self.compute_if_ship_sunk(
                                self.game_setting.radar_cross_table[player_radar_cross_table_index]):
                            other_player_ship_info.is_sunken = True
                            player_status.hit_enemy_count += 1
                            print("HIT SUCC: Player %s did hit %s:%s [%s] @ [%s, %s]" % (
                                player_id,
                                other_player_id,
                                other_player_ship_info.ship_id,
                                other_player_ship_info.area,
                                pos.x,
                                pos.y))
                            self.tts_comm_engine.send("Player %s sunk the Player %s ship" %
                                                      (player_id, other_player_id))
                        else:
                            print("HIT FAIL: Player %s is unable to sink the ship %s:%s [%s] @ [%s, %s]" % (
                                player_id,
                                other_player_id,
                                other_player_ship_info.ship_id,
                                other_player_ship_info.area,
                                pos.x,
                                pos.y))
                            self.tts_comm_engine.send("Player %s missed the Player %s ship" %
                                                      (player_id, other_player_id))
                    # Else the other player ship is not within the fire area
                    else:
                        print("MISSED  : Player %s did not hit %s:%s [%s] @ [%s, %s] [is sunken: %s]" % (
                            player_id,
                            other_player_id,
                            other_player_ship_info.ship_id,
                            other_player_ship_info.area,
                            pos.x,
                            pos.y,
                            other_player_ship_info.is_sunken))
                # end of for..loop player_ship_list
            # end of Check to skip self
        # end of for..loop player_status_list

        # Check if the player hit any civilian ship
        for civilian_ship_info in self.civilian_ship_list:
            if (not civilian_ship_info.is_sunken) and (fire_pos in civilian_ship_info.area):
                # Compute if the ship has been hit
                if self.compute_if_ship_sunk(self.game_setting.radar_cross_table[player_radar_cross_table_index]):
                    civilian_ship_info.is_sunken = True
                    player_status.hit_civilian_count += 1
                    print("HIT SUCC: Player %s did hit civilian:%s [%s] @ [%s, %s]" % (
                        player_id,
                        civilian_ship_info.ship_id,
                        civilian_ship_info.area,
                        pos.x,
                        pos.y))
                    self.tts_comm_engine.send("Player %s sunk the target" % player_id)
                else:
                    print("HIT FAIL: Player %s did not sink the civilian:%s [%s] @ [%s, %s]" % (
                        player_id,
                        civilian_ship_info.ship_id,
                        civilian_ship_info.area,
                        pos.x,
                        pos.y))
                    self.tts_comm_engine.send("Player %s missed the target" % player_id)
            # Else the civilian is not within the fire area
        # Else Do nothing
        bc_game_status = GameStatus(self.game_status.game_state, self.game_status.game_round, 0)
        self.comm_engine.set_game_status(bc_game_status)

    # def state_setup_play_compute_fire(self, player_id, fire_cmd, player_status):
    #     # if isinstance(fire_cmd, FireInfo):
    #     if isinstance(fire_cmd, ServerFireInfo):
    #         fire_pos = [fire_cmd.pos.x, fire_cmd.pos.y]
    #         player_radar_cross_table_index = player_id - 1
    #         for other_player_id, other_player_info in self.player_status_dict.items():
    #             if other_player_id is not player_id:
    #                 for other_player_ship_info in other_player_info.ship_list:
    #                     if (not other_player_ship_info.is_sunken) and (fire_pos in other_player_ship_info.area):
    #                         # Compute if the ship has been hit
    #                         if self.compute_if_ship_sunk(
    #                                 self.game_setting.radar_cross_table[player_radar_cross_table_index]):
    #                             other_player_ship_info.is_sunken = True
    #                             player_status.hit_enemy_count += 1
    #                             print("HIT SUCC: Player %s did hit %s:%s [%s] @ [%s, %s]" % (
    #                                 player_id,
    #                                 other_player_id,
    #                                 other_player_ship_info.ship_id,
    #                                 other_player_ship_info.area,
    #                                 fire_cmd.pos.x,
    #                                 fire_cmd.pos.y))
    #                             self.tts_comm_engine.send("Player %s sunk the Player %s ship" %
    #                                                       (player_id, other_player_id))
    #                         else:
    #                             print("HIT FAIL: Player %s is unable to sink the ship %s:%s [%s] @ [%s, %s]" % (
    #                                 player_id,
    #                                 other_player_id,
    #                                 other_player_ship_info.ship_id,
    #                                 other_player_ship_info.area,
    #                                 fire_cmd.pos.x,
    #                                 fire_cmd.pos.y))
    #                             self.tts_comm_engine.send("Player %s missed the Player %s ship" %
    #                                                       (player_id, other_player_id))
    #                     # Else the other player ship is not within the fire area
    #                     else:
    #                         print("MISSED  : Player %s did not hit %s:%s [%s] @ [%s, %s] [is sunken: %s]" % (
    #                             player_id,
    #                             other_player_id,
    #                             other_player_ship_info.ship_id,
    #                             other_player_ship_info.area,
    #                             fire_cmd.pos.x,
    #                             fire_cmd.pos.y,
    #                             other_player_ship_info.is_sunken))
    #                 # end of for..loop player_ship_list
    #             # end of Check to skip self
    #         # end of for..loop player_status_list
    #
    #         # Check if the player hit any civilian ship
    #         for civilian_ship_info in self.civilian_ship_list:
    #             if (not civilian_ship_info.is_sunken) and (fire_pos in civilian_ship_info.area):
    #                 # Compute if the ship has been hit
    #                 if self.compute_if_ship_sunk(self.game_setting.radar_cross_table[player_radar_cross_table_index]):
    #                     civilian_ship_info.is_sunken = True
    #                     player_status.hit_civilian_count += 1
    #                     print("HIT SUCC: Player %s did hit civilian:%s [%s] @ [%s, %s]" % (
    #                         player_id,
    #                         civilian_ship_info.ship_id,
    #                         civilian_ship_info.area,
    #                         fire_cmd.pos.x,
    #                         fire_cmd.pos.y))
    #                     self.tts_comm_engine.send("Player %s sunk the target" % player_id)
    #                 else:
    #                     print("HIT FAIL: Player %s did not sink the civilian:%s [%s] @ [%s, %s]" % (
    #                         player_id,
    #                         civilian_ship_info.ship_id,
    #                         civilian_ship_info.area,
    #                         fire_cmd.pos.x,
    #                         fire_cmd.pos.y))
    #                     self.tts_comm_engine.send("Player %s missed the target" % player_id)
    #             # Else the civilian is not within the fire area
    #     # Else Do nothing
    #     bc_game_status = GameStatus(self.game_status.game_state, self.game_status.game_round, 0)
    #     self.comm_engine.set_game_status(bc_game_status)

    def compute_if_ship_sunk(self, hit_possibility):
        is_sunk = False
        if np.random.rand() < hit_possibility:
            is_sunk = True
        return is_sunk

    def state_setup_stop(self):
        bc_game_status = GameStatus(self.game_status.game_state,
                                    self.game_status.game_round,
                                    0)
        self.comm_engine.set_game_status(bc_game_status)
        # Display the score of the game
        print("** Game end ------------------------------------")
        print(self.get_player_score())
        print("** ---------------------------------------------")
        self.tts_comm_engine.send("Game Ended")

    # ---------------------------------------------------------------------------
    def state_exec(self, msg_addr, msg_data):
    # def state_exec(self, msg):
        # Reply message
        reply = None
        # msg_data = None
        # msg_addr = None
        # if isinstance(msg, collections.Iterable) and len(msg) >= 2:
        #     msg_addr = msg[0]
        #     msg_data = msg[1]

        if self.game_status.game_state == GameState.INIT:
            reply = self.state_exec_init(msg_data)
        elif self.game_status.game_state == GameState.PLAY_INPUT:
            reply = self.state_exec_play_input(msg_data)
        elif self.game_status.game_state == GameState.PLAY_COMPUTE:
            reply = self.state_exec_play_compute(msg_data)
        elif self.game_status.game_state == GameState.STOP:
            reply = self.state_exec_stop(msg_data)
        else:
            print("Unsupported game state")
        # Send the reply if any
        if reply is not None:
            self.comm_engine_lock.acquire()
            try:
                print("REPLY: %s" % vars(reply))
                self.comm_engine.send(msg_addr, reply)
            finally:
                self.comm_engine_lock.release()

    def state_exec_init(self, msg_data):
        # process the reply for any input message
        reply = None
        #
        if msg_data is not None:
            # Check if message is MsgReqRegister
            if isinstance(msg_data, cMessages.MsgReqRegister):
                map_dat = np.array([])
                ack = False
                if msg_data.player_id not in self.player_status_dict:
                    map_dat = np.bitwise_or(self.island_layer, self.civilian_ship_layer)
                    map_dat = np.bitwise_or(map_dat, self.player_fog_layer[msg_data.player_id])
                    # map_dat = np.bitwise_or(self.island_layer, self.player_fog_layer[msg_data.player_id])
                    ack = True
                reply = cMessages.MsgRepAckMap(ack, map_dat.tolist())

            # Check if message is MsgReqRegShips
            elif isinstance(msg_data, cMessages.MsgReqRegShips):
                ack = False
                if msg_data.player_id not in self.player_status_dict:
                    # add the new player to the list
                    player_status = PlayerStatus()
                    player_status.ship_list.clear()

                    for ship_info_dat in msg_data.ship_list:
                        if isinstance(ship_info_dat, ShipInfo):
                            # clone the ship_info data
                            ship_info = ShipInfo(ship_id=ship_info_dat.ship_id,
                                                 ship_type=ShipType.MIL,
                                                 position=Position(ship_info_dat.position.x, ship_info_dat.position.y),
                                                 heading=ship_info_dat.heading,
                                                 size=ship_info_dat.size,
                                                 is_sunken=ship_info_dat.is_sunken)
                            player_status.ship_list.append(ship_info)
                            print(ship_info)

                    # check if the placement of the ships are ok before adding them to the list
                    is_ok = self.check_ship_placement(msg_data.player_id, player_status.ship_list)
                    if is_ok:
                        self.player_status_dict[msg_data.player_id] = player_status
                        ack = True
                reply = cMessages.MsgRepAck(ack)

            # Check if message is MsgReqConfig
            elif isinstance(msg_data, cMessages.MsgReqConfig):
                game_config = GameConfig(self.game_setting.num_of_player,
                                         self.game_setting.num_of_rounds,
                                         self.game_setting.num_fire_act,
                                         self.game_setting.num_move_act,
                                         self.game_setting.num_satcom_act,
                                         self.game_setting.num_of_row,
                                         self.game_setting.polling_rate,
                                         Size(self.game_setting.map_size.x,
                                              self.game_setting.map_size.y),
                                         self.player_boundary_dict,
                                         self.game_setting.en_satellite,
                                         self.game_setting.en_satellite_func2,
                                         self.game_setting.en_submarine)
                reply = cMessages.MsgRepGameConfig(True, game_config)
            else:
                reply = cMessages.MsgRepAck(False)

        return reply

    def state_exec_play_input(self, msg_data):
        # process the reply for any input message
        reply = None
        # process the reply for any input message
        if (msg_data is not None) and isinstance(msg_data, cMessages.MsgReq):
            # Check if message is MsgReqTurnInfo
            if isinstance(msg_data, cMessages.MsgReqTurnInfo):
                reply = self.state_exec_play_input_turn(msg_data)

            # Check if message is MsgReqTurnMoveAct
            elif isinstance(msg_data, cMessages.MsgReqTurnMoveAct):
                reply = self.state_exec_play_input_move(msg_data)

            # Check if message is MsgReqTurnFireAct
            elif isinstance(msg_data, cMessages.MsgReqTurnFireAct):
                reply = self.state_exec_play_input_fire(msg_data)

            # Check if message is MsgReqTurnSatAct
            elif isinstance(msg_data, cMessages.MsgReqTurnSatAct):
                reply = self.state_exec_play_input_satcom(msg_data)

            # Check if message is MsgReqConfig
            elif isinstance(msg_data, cMessages.MsgReqConfig):
                game_config = GameConfig(self.game_setting.num_of_player,
                                         self.game_setting.num_of_rounds,
                                         self.game_setting.num_fire_act,
                                         self.game_setting.num_move_act,
                                         self.game_setting.num_satcom_act,
                                         self.game_setting.num_of_row,
                                         self.game_setting.polling_rate,
                                         Size(self.game_setting.map_size.x,
                                              self.game_setting.map_size.y),
                                         self.player_boundary_dict,
                                         self.game_setting.en_satellite,
                                         self.game_setting.en_satellite_func2,
                                         self.game_setting.en_submarine)
                reply = cMessages.MsgRepGameConfig(True, game_config)

            else:
                # Unsupport message type
                print("Receive wrong message from player %s, for the wrong state..." % msg_data.player_id)
                reply = cMessages.MsgRepAck(False)

        # Bugfix: The following is moved out of the state_exec state; into the common run exec
        # # Update the publisher on the game status
        # bc_game_status = GameStatus(self.game_status.game_state,
        #                             self.game_status.game_round,
        #                             0,
        #                             self.game_status.time_remaining)
        # self.comm_engine.set_game_status(bc_game_status)

        return reply

    # Operation to generate the turn-info for the request
    def state_exec_play_input_turn(self, msg_data):

        self_ship_list = list()
        enemy_ship_list = list()
        other_ship_list = list()

        for ship_info in self.player_status_dict[msg_data.player_id].ship_list:
            if isinstance(ship_info, ShipInfo):
                # Clone the player ship information
                ship_info_dat = ShipInfo(ship_id=ship_info.ship_id,
                                         ship_type=ship_info.ship_type,
                                         position=Position(ship_info.position.x, ship_info.position.y),
                                         heading=ship_info.heading,
                                         size=ship_info.size,
                                         is_sunken=ship_info.is_sunken)
                self_ship_list.append(ship_info_dat)

        # Get the list of civilian ships
        for ship_info in self.civilian_ship_list:
            if isinstance(ship_info, ShipInfo):
                # Clone the civilian ship information
                ship_info_dat = ShipInfo(ship_id=ship_info.ship_id,
                                         ship_type=ship_info.ship_type,
                                         position=Position(ship_info.position.x, ship_info.position.y),
                                         heading=ship_info.heading,
                                         size=ship_info.size,
                                         is_sunken=ship_info.is_sunken)
                other_ship_list.append(ship_info_dat)

        # Get the list of enemy ships
        enemy_data_list = self.hist_enemy_data_dict.get(msg_data.player_id)
        print("****** Player %s: Enemy Data:\r\n%s" % (msg_data.player_id, enemy_data_list))
        if isinstance(enemy_data_list, collections.Iterable):
            for enemy_data in enemy_data_list:
                print("****** %s" % enemy_data)
                for ship_info in enemy_data.ship_list:
                    if isinstance(ship_info, ShipInfo):
                        # Clone the enemy ship information
                        ship_info_dat = ShipInfo(ship_id=ship_info.ship_id,
                                                 ship_type=ship_info.ship_type,
                                                 position=Position(ship_info.position.x, ship_info.position.y),
                                                 heading=ship_info.heading,
                                                 size=ship_info.size,
                                                 is_sunken=ship_info.is_sunken)
                        # TODO: Do we need to differ the enemy and civilian ship? if so, how???
                        if True:
                            other_ship_list.append(ship_info_dat)
                        else:
                            enemy_ship_list.append(ship_info_dat)

        # print("****** Player %s: other_ship_list:\r\n%s" % (msg_data.player_id, other_ship_list))
        # print("****** Player %s: enemy_ship_list:\r\n%s" % (msg_data.player_id, enemy_ship_list))

        other_ship_list = self.get_visible_ship_list(msg_data.player_id, other_ship_list)
        enemy_ship_list = self.get_visible_ship_list(msg_data.player_id, enemy_ship_list)

        # else:
        #     # Remove all the ship as the player is not suppose to see them yet
        #     other_ship_list.clear()
        print("****** Player %s: other_ship_list:\r\n%s" % (msg_data.player_id, other_ship_list))
        print("****** Player %s: enemy_ship_list:\r\n%s" % (msg_data.player_id, enemy_ship_list))

        # bombardment_data = [value for key, value in self.player_curr_fire_cmd_dict.items() if
        #                     key is not msg_data.player_id]
        # bombardment_data = [value for value in self.player_curr_fire_cmd_list if
        #                     value.player_id is not msg_data.player_id]
        bombardment_data = []
        for value in self.player_curr_fire_cmd_list:
            if value.player_id is not msg_data.player_id:
                bombardment_data.append(FireInfo(value.pos))


        # compute the map data
        map_data = self.generate_map_data(msg_data.player_id)
        print("****** Player %s: Map Data :\r\n%s" % (msg_data.player_id, map_data.T))

        # Generate the reply
        reply = cMessages.MsgRepTurnInfo(True,
                                         self_ship_list,
                                         enemy_ship_list,
                                         other_ship_list,
                                         bombardment_data,
                                         map_data.tolist())
        return reply

    # Operation to perform the move operation
    def state_exec_play_input_move(self, msg_data):
        ack = False
        remaining_action = self.player_remaining_action_dict.get(msg_data.player_id)
        if isinstance(remaining_action, PlayerTurnActionCount):
            if (remaining_action.remain_move >= len(msg_data.move)):
                for action in msg_data.move:
                    if isinstance(action, ShipMovementInfo):
                        ship = self.player_status_dict[msg_data.player_id].ship_list[action.ship_id]
                        if isinstance(ship, ShipInfo):
                            if action.get_enum_action() == Action.FWD:
                                # Check if the selected ship can move forward
                                if self.check_forward_action(ship, msg_data.player_id):
                                    ship.move_forward()
                                    self.tts_comm_engine.send("Player %s move ship forward")
                                else:
                                    print("!!! Unable to move forward")
                            elif action.get_enum_action() == Action.CW:
                                # Check if the selected ship can turn clockwise
                                if self.check_turn_cw_action(ship, msg_data.player_id):
                                    ship.turn_clockwise()
                                    self.tts_comm_engine.send("Player %s turn ship clockwise")
                                else:
                                    print("!!! Unable to turn CW")
                            elif action.get_enum_action() == Action.CCW:
                                # Check if the selected ship can turn counter-clockwise
                                if self.check_turn_ccw_action(ship, msg_data.player_id):
                                    ship.turn_counter_clockwise()
                                    self.tts_comm_engine.send("Player %s turn ship counter clockwise")
                                else:
                                    print("!!! Unable to turn CCW")
                # Update on the number of remaining move operation
                # self.game_status.remaining_action.remain_move -= len(msg_data.move)
                remaining_action.remain_move -= len(msg_data.move)
                ack = True
            else:
                print("Player %s is out of move action" % msg_data.player_id)
        else:
            print("Received unknown player id : %s" % msg_data.player_id)

        reply = cMessages.MsgRepAck(ack)
        return reply

    # Operation to perform the fire operation from the user
    def state_exec_play_input_fire(self, msg_data):
        ack = False
        remaining_action = self.player_remaining_action_dict.get(msg_data.player_id)
        if isinstance(remaining_action, PlayerTurnActionCount):
            if remaining_action.remain_fire >= len(msg_data.fire):
                # # Modified by ttl, 2019-01-13
                # # Update the position the player is hitting
                # self.player_prev_fire_cmd_list[msg_data.player_id] = self.player_curr_fire_cmd_list.get(msg_data.player_id)
                # self.player_curr_fire_cmd_list[msg_data.player_id] = msg_data.fire
                #
                # # Update the position the player is hitting
                # self.player_curr_fire_cmd_dict[msg_data.player_id] = msg_data.fire
                # # end of modification

                # Modified by ttl, 2019-02-07
                # To take time into consideration when computing the fire operation
                if isinstance(msg_data.fire, FireInfo):
                    self.player_curr_fire_cmd_list.append(ServerFireInfo(msg_data.player_id, msg_data.fire.pos))
                elif isinstance(msg_data.fire, collections.Iterable):
                    for fire in msg_data.fire:
                        if isinstance(fire, FireInfo):
                            self.player_curr_fire_cmd_list.append(ServerFireInfo(msg_data.player_id, fire.pos))
                # end of modification



                if isinstance(msg_data.fire, FireInfo):
                    self.state_exec_play_input_fire_send(msg_data.player_id, msg_data.fire.pos)
                    remaining_action.remain_fire -= 1
                elif isinstance(msg_data.fire, collections.Iterable):
                    for fire in msg_data.fire:
                        if isinstance(fire, FireInfo):
                            self.state_exec_play_input_fire_send(msg_data.player_id, fire.pos)

                remaining_action.remain_fire -= len(msg_data.fire)

                ack = True
            else:
                print("Player %s is out of fire action" % msg_data.player_id)
        else:
            print("Received unknown player id : %s" % msg_data.player_id)
        reply = cMessages.MsgRepAck(ack)
        return reply

    # send the fire command to the tts server
    def state_exec_play_input_fire_send(self, player_id, position):
        if isinstance(position, Position):
            self.tts_comm_engine.send("Player %s bombing %s %s" %
                                      (player_id,
                                       position.x,
                                       position.y))

    # Operation to perform the satcom action
    def state_exec_play_input_satcom(self, msg_data):
        ack = False
        # ship_list = self.player_status_list[msg_data.player_id].ship_list
        # bombardment_data = [value for key, value in self.player_curr_fire_cmd_list.items() if
        # 					key is not msg_data.player_id]
        map_data = []
        remaining_action = self.player_remaining_action_dict.get(msg_data.player_id)
        if isinstance(remaining_action, PlayerTurnActionCount):
            if remaining_action.remain_satcom > 0:

                # self.last_satcom_mask[msg_data.player_id] = np.ones((self.game_setting.map_size.x, self.game_setting.map_size.y))
                self.last_satcom_mask[msg_data.player_id] = satcom_scan(self.game_setting.map_size,
                                                                        msg_data.satcom)
                if self.game_setting.en_satellite_func2 is True:
                    self.last_satcom_enable[msg_data.player_id] = msg_data.satcom.is_enable
                else:
                    self.last_satcom_enable[msg_data.player_id] = False
                remaining_action.remain_satcom -= 1
                ack = True

            else:
                print("Receive message from player %s, but their do not have anymore satcom action..." % msg_data.player_id)

        # Compute the map data for the user
        map_data = self.generate_map_data(msg_data.player_id)
        print("****** SATCOM Data :\r\n%s" % map_data.T)

        # Create the result
        reply = cMessages.MsgRepAckMap(ack, map_data.tolist())
        return reply

    # Compute the necessary computation at the end of each turn
    def state_exec_play_compute(self, msg_data):
        # We are not expected to receive any message at this state
        # Hence, we shall reply a negative acknowledgement for any message received
        reply = None
        if msg_data is not None:
            reply = cMessages.MsgRepAck(False)
        return reply

    def state_exec_stop(self, msg_data):
        # We are not expected to receive any message at this state
        # Hence, we shall reply a negative acknowledgement for any message received
        reply = None
        if msg_data is not None:
            reply = cMessages.MsgRepAck(False)
        return reply

    # ---------------------------------------------------------------------------
    def generate_map_data(self, player_id):

        # Get the current map mask of the given user
        player_map_mask = self.player_boundary_layer[player_id]

        # Get the cloud data
        cloud_friendly = self.cloud_layer * player_map_mask * MapData.CLOUD_FRIENDLY
        cloud_hostile = self.cloud_layer * np.invert(player_map_mask) * MapData.CLOUD_HOSTILE

        # Update the fog of war and and hostile cloud
        satcom_mask = self.last_satcom_mask.get(player_id)
        if isinstance(satcom_mask, np.ndarray) and \
                (satcom_mask.shape == self.cloud_layer.shape):
            self.turn_map_fog[player_id] = self.turn_map_fog[player_id] * np.invert(satcom_mask.astype(np.bool))
            if self.last_satcom_enable[player_id]:
                cloud_hostile = cloud_hostile * (self.turn_map_fog[player_id] == MapData.FOG_OF_WAR)
        elif satcom_mask is None:
            print("!!! Player [%s] SATCOM MASK is NONE !!!" % (player_id))

        # Generate the empty map data
        map_data = np.zeros((self.game_setting.map_size.x, self.game_setting.map_size.y), dtype=int)

        # Add the island onto the map
        map_data = np.bitwise_or(map_data, self.island_layer)

        # Add the cloud to map
        map_data = np.bitwise_or(map_data, cloud_friendly)      # Add the cloud in friendly area
        map_data = np.maximum(map_data, cloud_hostile)          # Add the cloud in enemy area

        # Add the Fog Of War
        # map_data = np.bitwise_or(map_data, self.turn_map_fog)
        map_data = np.maximum(map_data, self.turn_map_fog[player_id])

        return map_data

    # ---------------------------------------------------------------------------
    def get_visible_ship_list(self, player_id, ship_list):
        outp_ship_list = list()
        # Get mask of the giving player
        player_map_fog = self.turn_map_fog[player_id]
        if isinstance(player_map_fog, np.ndarray):
            player_map_fog = player_map_fog.astype(np.bool)
            for ship in ship_list:
                if isinstance(ship, ShipInfo):
                    for pos in ship.area:
                        # print("map pos: %s" % player_map_fog[int(pos[0]),int(pos[1])])
                        if not player_map_fog[int(pos[0]),int(pos[1])]:
                            outp_ship_list.append(copy.deepcopy(ship))
                            break
                    # end of position for..loop
            # end of ship_list for..loop
        return  outp_ship_list




    # ---------------------------------------------------------------------------
    # Check if the placement of the ship are valid
    def check_ship_placement(self, player_id, ship_list):

        is_ok = True
        obstacle_dict = dict()

        if isinstance(ship_list, collections.Iterable):
            # add the boundary
            boundary = self.player_boundary_layer.get(player_id)
            if isinstance(boundary, np.ndarray):
                boundary = np.invert(boundary)
                obstacle_dict["Boundary"] = boundary

            # # add the island
            # if isinstance(self.island_layer, np.ndarray):
            #     obstacle_dict["Island"] = self.island_layer
            #
            # # add the civilian ship
            # if isinstance(self.civilian_ship_layer, np.ndarray):
            #     obstacle_dict["civilian_ship"] = self.civilian_ship_layer

            for ship_info in ship_list:
                if isinstance(ship_info, ShipInfo):
                    is_ok = is_ok and check_collision(ship_info, obstacle_dict)
                else:
                    print("!!! SHIP [NEW]: Incorrect type [not ShipInfo] [playerid=%s]" % player_id)
                    is_ok = False
            # end of for..loop
        else:
            print("!!! SHIP [NEW]: Incorrect type [not Iterable] [playerid=%s]" % player_id)
            is_ok = False

        return is_ok

    # Check if the given ship can move forward
    def check_forward_action(self, ship_info, player_id):

        is_ok = True
        obstacle_dict = dict()
        test_ship = copy.deepcopy(ship_info)
        test_ship.move_forward()

        # add the boundary
        boundary = self.player_boundary_layer.get(player_id)
        if isinstance(boundary, np.ndarray):
            boundary = np.invert(boundary)
            obstacle_dict["Boundary"] = boundary

        # # add the island
        # if isinstance(self.island_layer, np.ndarray):
        #     obstacle_dict["Island"] = self.island_layer
        #
        # # add the civilian ship
        # if isinstance(self.civilian_ship_layer, np.ndarray):
        #     obstacle_dict["civilian_ship"] = self.civilian_ship_layer

        is_ok = check_collision(test_ship, obstacle_dict)

        return is_ok

    # Check if the given ship can perform a clockwise turn
    def check_turn_cw_action(self, ship_info, player_id):

        is_ok = True
        obstacle_dict = dict()
        test_ship = copy.deepcopy(ship_info)
        test_ship.turn_clockwise()

        # add the boundary
        boundary = self.player_boundary_layer.get(player_id)
        if isinstance(boundary, np.ndarray):
            boundary = np.invert(boundary)
            obstacle_dict["Boundary"] = boundary

        # # add the island
        # if isinstance(self.island_layer, np.ndarray):
        #     obstacle_dict["Island"] = self.island_layer
        #
        # # add the civilian ship
        # if isinstance(self.civilian_ship_layer, np.ndarray):
        #     obstacle_dict["civilian_ship"] = self.civilian_ship_layer

        is_ok = check_collision(test_ship, obstacle_dict)

        return is_ok

    # Check if the given ship can perform a counter-clockwise turn
    def check_turn_ccw_action(self, ship_info, player_id):
        is_ok = True
        obstacle_dict = dict()
        test_ship = copy.deepcopy(ship_info)
        test_ship.turn_counter_clockwise()

        # add the boundary
        boundary = self.player_boundary_layer.get(player_id)
        if isinstance(boundary, np.ndarray):
            boundary = np.invert(boundary)
            obstacle_dict["Boundary"] = boundary

        # # add the island
        # if isinstance(self.island_layer, np.ndarray):
        #     obstacle_dict["Island"] = self.island_layer
        #
        # # add the civilian ship
        # if isinstance(self.civilian_ship_layer, np.ndarray):
        #     obstacle_dict["civilian_ship"] = self.civilian_ship_layer

        is_ok = check_collision(test_ship, obstacle_dict)

        return is_ok

    # ---------------------------------------------------------------------------
    def load_server_setting(self, filename):
        write_config = False
        game_setting = None
        try:
            with open(filename) as infile:
                game_setting = json.load(infile, cls=SvrCfgJsonDecoder)
        except:
            print("Unable to load server setting")
            write_config = True

        if write_config:
            try:
                game_setting = ServerGameConfig()
                with open(filename, 'w') as outfile:
                    json.dump(game_setting, outfile, cls=SvrCfgJsonEncoder, indent=4)
            except:
                print("Unable to write server setting")

        return game_setting

    # ---------------------------------------------------------------------------
    def generate_player_mask(self, player_mask_dict, player_boundary_dict):
        if isinstance(player_mask_dict, dict) and isinstance(player_boundary_dict, dict):
            col_count = int(np.ceil(self.game_setting.num_of_player / self.game_setting.num_of_row))
            row_count = self.game_setting.num_of_row

            player_x_sz = int(self.game_setting.map_size.x / col_count)
            player_y_sz = int(self.game_setting.map_size.y / row_count)

            for i in range(self.game_setting.num_of_player):
                x1 = int((i % col_count) * player_x_sz)
                x2 = x1 + player_x_sz
                y1 = int((i // col_count) * player_y_sz)
                y2 = y1 + player_y_sz
                # print(i, x1, x2, y1, y2)

                mask = np.zeros((self.game_setting.map_size.x, self.game_setting.map_size.y), dtype=np.bool)
                mask[x1:x2, y1:y2] = True
                player_mask_dict[i + 1] = mask
                # player_boundary_dict[i+1] = [[x1, x2], [y1, y2]]
                player_boundary_dict[i + 1] = Boundary(x1, x2, y1, y2)
                # player_mask_list.append(mask)
                # print("player %s" % (i+1))
                # print(mask)

    def get_player_score(self):
        reply = ""
        for key, player in self.player_status_dict.items():
            sunken_count = 0
            for ship_info in player.ship_list:
                if ship_info.is_sunken:
                    sunken_count += 1
            score = (player.hit_enemy_count * 1.0) - (player.hit_civilian_count * 0.0) - (sunken_count * 0.5)
            if len(reply) > 0:
                reply += "\r\n"
            reply += "** \tPlayer %2s : score:%6.1f | hit:%2d - %2d | sunken:%2d" % \
                     (key, score, player.hit_enemy_count, player.hit_civilian_count, sunken_count)

        return reply


def main():
    global flag_quit_game
    flag_quit_game = False

    signal.signal(signal.SIGINT, signal_handler)

    print("WOS Battlership Server -- started")
    wosServer = WosBattleshipServer()
    wosServer.start()

    # start the user-input command server
    cmdServer = CmdServerCommEngine()
    cmdServer.start()
    while not cmdServer.is_ready:
        time.sleep(1)
    print("WOS Battlership Server -- Cmd Server Ready")

    # Game Main exec --------------------------------------------------------------
    while flag_quit_game is not True:
        inp = cmdServer.recv()
        if inp is not None:
            inp = inp.strip()
            inp = inp.upper()

            print("RECV CMD: %s" % inp)

            reply = "OK"
            if inp == 'QUIT':
                flag_quit_game = True
            elif inp == 'END':
                wosServer.end_game()
            elif inp == "RESTART":
                wosServer.restart_game()
            elif inp == 'RESET':
                # TODO: RESET THE wosServer
                pass
            elif inp == 'CLEAR':
                wosServer.clear_user()
            elif inp == 'SCORE':
                reply = "SCORE\r\n"
                reply += "-------------------------\r\n"
                reply += wosServer.get_player_score()
                reply += "-------------------------\r\n"
            else:
                print("Invalid command : %s" % inp)
                reply = "NOK"

            cmdServer.send(reply)

    # Server Teardown --------------------------------------------------------------
    # Stop the user-input command server
    cmdServer.stop()

    # Stop the communication engine and wait for it to stop
    wosServer.stop()
    wosServer.join()

    print("WOS Battlership Server -- end")


if __name__ == '__main__':
    print("*** %s (%s)" % (__file__, time.ctime(time.time())))
    main()
