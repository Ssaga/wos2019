import json
import numpy as np
import time

from cCommonCommEngine import ConnInfo
from cCommonGame import Size
from cCommonGame import Position
from cCommonGame import GameState
from cCommonGame import ShipInfo


class ServerGameConfig:
    def __init__(self,
                 req_rep_conn=ConnInfo('127.0.0.1', 5556),
                 pub_sub_conn=ConnInfo('127.0.0.1', 5557),
                 polling_rate=1000,                             # Unit in milliseconds
                 bc_rate=1000,                                  # Unit in milliseconds
                 map_size=Size(120, 120),
                 countdown_duration=30,                         # Unit in seconds
                 island_coverage=0,
                 cloud_coverage=0,
                 cloud_seed_cnt=0,
                 civilian_ship_count=0,
                 civilian_ship_move_probility=0.25,
                 num_of_rounds=0,
                 num_of_player=4,
                 num_of_row=2,
                 num_move_act=2,
                 num_fire_act=1,
                 num_satcom_act=1,
                 radar_cross_table=[1.0, 1.0, 1.0, 1.0],
                 en_satellite=False,
                 en_satellite_func2=False,
                 en_submarine=False):
        self.req_rep_conn = req_rep_conn
        self.pub_sub_conn = pub_sub_conn
        self.polling_rate = polling_rate
        self.bc_rate = bc_rate
        self.map_size = map_size
        self.countdown_duration = countdown_duration
        self.island_coverage = island_coverage
        self.cloud_coverage = cloud_coverage
        self.cloud_seed_cnt = cloud_seed_cnt
        self.civilian_ship_count = civilian_ship_count
        self.civilian_ship_move_probility = civilian_ship_move_probility
        self.num_of_rounds = int(num_of_rounds)
        self.num_of_player = int(num_of_player)
        self.num_of_row = int(num_of_row)
        self.num_move_act = int(num_move_act)
        self.num_fire_act = int(num_fire_act)
        self.num_satcom_act = int(num_satcom_act)
        self.radar_cross_table = []
        self.radar_cross_table.extend(radar_cross_table)
        self.en_satellite = bool(en_satellite)
        self.en_satellite_func2 = bool(en_satellite_func2)
        self.en_submarine = bool(en_submarine)

    def __repr__(self):
        return str(vars(self))


class PlayerStatus:
    def __init__(self):
        self.ship_list = []
        self.hit_enemy_count = 0
        self.hit_civilian_count = 0

    def __repr__(self):
        return str(vars(self))


class PlayerTurnActionCount:
    def __init__(self, remain_move, remain_fire, remain_satcom):
        self.remain_move = remain_move
        self.remain_fire = remain_fire
        self.remain_satcom = remain_satcom

    def __repr__(self):
        return str(vars(self))


class GameTurnStatus:
    def __init__(self,
                 game_state=GameState.INIT,
                 default_move=0,
                 default_fire = 0,
                 default_satcom=0,
                 game_round=0,
                 player_turn=0,
                 time_remaining=0
                 ):
        self.game_state = game_state
        # game round start count from 1
        self.game_round = game_round
        # player turn start count from 1
        self.player_turn = player_turn                              # Not used
        # added by ttl, 2019-01-13
        self.time_remaining = time_remaining
        # end of modification
        self.allowed_action = PlayerTurnActionCount(default_move, default_fire, default_satcom)
        # self.remaining_action = PlayerTurnActionCount(0, 0, 0)
        # self.clear_turn_remaining_action()

    def __repr__(self):
        return str(vars(self))

    # def reset_turn_remaining_action(self):
    #     self.remaining_action.remain_move = self.allowed_action.remain_move
    #     self.remaining_action.remain_fire = self.allowed_action.remain_fire
    #     self.remaining_action.remain_satcom = self.allowed_action.remain_satcom

    # def clear_turn_remaining_action(self):
    #     self.remaining_action.remain_move = 0
    #     self.remaining_action.remain_fire = 0
    #     self.remaining_action.remain_satcom = 0


class ServerFireInfo:
    def __init__(self, player_id = None, pos=Position()):
        self.timestamp = time.time()
        self.player_id = player_id
        self.pos = pos

    def __repr__(self):
        return str(vars(self))

    def to_string(self):
        return "Player %s Fire @ (%s, %s) on %s" % \
               (self.player_id, self.pos.x, self.pos.y, self.timestamp)

#-----------------------------------------------------------------------
class SvrCfgJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        result = None
        if isinstance(obj, ConnInfo):
            result = {
                "__class__": "ConnInfo",
                "addr": obj.addr,
                "port": obj.port
            }
        elif isinstance(obj, Size):
            result = {
                "__class__": "Size",
                "x": obj.x,
                "y": obj.y
            }
        elif isinstance(obj, ServerGameConfig):
            result = {
                "__class__": "ServerGameConfig",
                "req_rep_conn": obj.req_rep_conn,
                "pub_sub_conn": obj.pub_sub_conn,
                "polling_rate": obj.polling_rate,
                "bc_rate": obj.bc_rate,
                "map_size": obj.map_size,
                "countdown_duration": obj.countdown_duration,
                "island_coverage": obj.island_coverage,
                "cloud_coverage": obj.cloud_coverage,
                "cloud_seed_cnt": obj.cloud_seed_cnt,
                "civilian_ship_count": obj.civilian_ship_count,
                "civilian_ship_move_probility": obj.civilian_ship_move_probility,
                "num_of_rounds": obj.num_of_rounds,
                "num_of_player": obj.num_of_player,
                "num_of_row": obj.num_of_row,
                "num_move_act": obj.num_move_act,
                "num_fire_act": obj.num_fire_act,
                "num_satcom_act": obj.num_satcom_act,
                "radar_cross_table": obj.radar_cross_table,
                "en_satellite": obj.en_satellite,
                "en_satellite_func2": obj.en_satellite_func2,
                "en_submarine": obj.en_submarine
            }
        else:
            result = super().default(self, obj)

        return result


class SvrCfgJsonDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        result = None
        if '__class__' not in obj:
            result = obj
        else:
            class_type = obj['__class__']
            if class_type == 'ConnInfo':
                result = self.parse_conn_info(obj)
            elif class_type == 'Size':
                result = self.parse_size(obj)
            elif class_type == 'ServerGameConfig':
                result = self.parse_svr_game_cfg(obj)
            else:
                print("Unsupported class type")

        return result

    @staticmethod
    def parse_conn_info(obj):
        return ConnInfo(
            obj['addr'],
            obj['port']
        )

    @staticmethod
    def parse_size(obj):
        return Size(
            obj['x'],
            obj['y']
        )

    @staticmethod
    def parse_svr_game_cfg(obj):
        return ServerGameConfig(
            obj['req_rep_conn'],
            obj['pub_sub_conn'],
            obj['polling_rate'],
            obj['bc_rate'],
            obj['map_size'],
            obj['countdown_duration'],
            obj['island_coverage'],
            obj['cloud_coverage'],
            obj['cloud_seed_cnt'],
            obj['civilian_ship_count'],
            obj['civilian_ship_move_probility'],
            obj['num_of_rounds'],
            obj['num_of_player'],
            obj['num_of_row'],
            obj["num_move_act"],
            obj["num_fire_act"],
            obj["num_satcom_act"],
            obj['radar_cross_table'],
            obj['en_satellite'],
            obj['en_satellite_func2'],
            obj['en_submarine']
        )


# -----------------------------------------------------------------------
# Check if the given ship hit any obstacle mask
def check_collision(test_ship, obstacle_mask_dict):
    is_ok = True
    if isinstance(test_ship, ShipInfo) and \
            isinstance(obstacle_mask_dict, dict):
        # check if test ship hit any obstacle
        for obstacle_mask_key in obstacle_mask_dict.keys():
            obstacle_mask = obstacle_mask_dict[obstacle_mask_key]
            if isinstance(obstacle_mask, np.ndarray):
                for pos in test_ship.area:
                    if pos[0] >= obstacle_mask.shape[0] or \
                            pos[1] >= obstacle_mask.shape[1] or \
                            pos[0] < 0 or pos[1] < 0:
                        is_ok = False
                        print("!!! SHIP: %s \r\n!!!Out of boundary - %s:%s" % (
                            test_ship, obstacle_mask_key, obstacle_mask.shape))
                        break
                    elif obstacle_mask[pos[0], pos[1]] > 0:
                        is_ok = False
                        print("!!! SHIP: %s \r\n!!!Collision with %s" % (test_ship, obstacle_mask_key))
                        # print(obstacle_mask.T)
                        break
                    # Else the ship is safe to move to the required position
                # end of for..loop
            else:
                # Unsupported obstacle mask type
                is_ok = False
                raise ValueError("Unsupported obstacle mask type")
        # end of for..loop
    else:
        is_ok = False
        raise ValueError("Incorrect input parameters")

    return is_ok
