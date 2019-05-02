import json
import numpy as np
import time
import math
import collections
import copy

from cCommonGame import ShipType
from cCommonCommEngine import ConnInfo
from cCommonGame import Size
from cCommonGame import Position
from cCommonGame import GameState
from cCommonGame import ShipInfo
from cCommonGame import UwShipInfo as CommonUwShipInfo
from cCommonGame import UwActionMoveScan
# from cCommonGame import UwActionScan
from cCommonGame import UwCollectedData


class ServerGameConfig:
    def __init__(self,
                 req_rep_conn=ConnInfo('127.0.0.1', 5556),
                 pub_sub_conn=ConnInfo('127.0.0.1', 5557),
                 polling_rate=1000,  # Unit in milliseconds
                 bc_rate=1000,  # Unit in milliseconds
                 map_size=Size(120, 120),
                 countdown_duration=30,  # Unit in seconds
                 island_coverage=0,
                 cloud_coverage_min=0,
                 cloud_coverage_max=0,
                 cloud_seed_cnt=0,
                 civilian_ship_count=0,
                 civilian_ship_move_probility=0.25,
                 num_of_rounds=0,
                 num_of_player=4,
                 num_of_row=2,
                 num_move_act=2,
                 num_fire_act=1,
                 num_satcom_act=1,
                 num_uw_action=1,
                 radar_cross_table=[1.0, 1.0, 1.0, 1.0],
                 en_satellite=False,
                 en_satellite_func2=False,
                 en_uw_action=False):
        self.req_rep_conn = req_rep_conn
        self.pub_sub_conn = pub_sub_conn
        self.polling_rate = polling_rate
        self.bc_rate = bc_rate
        self.map_size = map_size
        self.countdown_duration = countdown_duration
        self.island_coverage = island_coverage
        self.cloud_coverage_min = cloud_coverage_min
        self.cloud_coverage_max = cloud_coverage_max
        self.cloud_seed_cnt = cloud_seed_cnt
        self.civilian_ship_count = civilian_ship_count
        self.civilian_ship_move_probility = civilian_ship_move_probility
        self.num_of_rounds = int(num_of_rounds)
        self.num_of_player = int(num_of_player)
        self.num_of_row = int(num_of_row)
        self.num_move_act = int(num_move_act)
        self.num_fire_act = int(num_fire_act)
        self.num_satcom_act = int(num_satcom_act)
        self.num_uw_action = int(num_uw_action)
        self.radar_cross_table = []
        self.radar_cross_table.extend(radar_cross_table)
        self.en_satellite = bool(en_satellite)
        self.en_satellite_func2 = bool(en_satellite_func2)
        self.en_uw_action = bool(en_uw_action)

    def __repr__(self):
        return str(vars(self))


class PlayerStatus:
    def __init__(self):
        self.ship_list = []
        self.uw_ship_dict = dict()
        self.hit_enemy_count = 0
        self.hit_civilian_count = 0

    def __repr__(self):
        return str(vars(self))


class PlayerTurnActionCount:
    def __init__(self,
                 remain_move,
                 remain_fire,
                 remain_satcom,
                 remain_uw_action):
        self.remain_move = remain_move
        self.remain_fire = remain_fire
        self.remain_satcom = remain_satcom
        self.remain_uw_action = remain_uw_action

    def __repr__(self):
        return str(vars(self))


class GameTurnStatus:
    def __init__(self,
                 game_state=GameState.INIT,
                 default_move=0,
                 default_fire=0,
                 default_satcom=0,
                 default_uw_action=0,
                 game_round=0,
                 player_turn=0,
                 time_remaining=0
                 ):
        self.game_state = game_state
        # game round start count from 1
        self.game_round = game_round
        # player turn start count from 1
        self.player_turn = player_turn  # Not used
        # added by ttl, 2019-01-13
        self.time_remaining = time_remaining
        # end of modification
        self.allowed_action = PlayerTurnActionCount(default_move,
                                                    default_fire,
                                                    default_satcom,
                                                    default_uw_action)
        # self.remaining_action = PlayerTurnActionCount(0, 0, 0)
        # self.clear_turn_remaining_action()

    def __repr__(self):
        return str(vars(self))


class ServerFireInfo:
    def __init__(self, player_id=None, pos=Position()):
        self.timestamp = time.time()
        self.player_id = player_id
        self.pos = pos

    def __repr__(self):
        return str(vars(self))

    def to_string(self):
        return "Player %s Fire @ (%s, %s) on %s" % \
               (self.player_id, self.pos.x, self.pos.y, self.timestamp)


class UwShipInfo(CommonUwShipInfo):
    def __init__(self,
                 ship_id=0,
                 position=Position(0, 0),
                 size=1,
                 is_sunken=False,
                 ship_type=ShipType.MIL,
                 mov_speed=1,
                 scan_size=3):
        CommonUwShipInfo.__init__(self=self,
                                  ship_id=ship_id,
                                  position=position,
                                  size=size,
                                  is_sunken=is_sunken,
                                  ship_type=ship_type)
        self.mov_speed = mov_speed
        self.scan_size = scan_size
        self.src_pos = position
        self.dst_pos = None
        self.remain_move_ops = 0
        self.remain_scan_ops = 0
        self.total_move_ops = 0
        self.reset_report = False
        self.orders = list()
        self.report = list()

    def set_ops_order(self, orders=[]):
        """
        Set the list of orders to be fulfilled
        :param orders: List of UwAction to be carried out
        :return: None
        """
        self.orders = orders
        self.reset_report = True

    def set_cmd(self, pos=None, scan_dur=0):
        """
        Set the current set of operation to be carried out
        :param pos: Position to goto
        :param scan_dur: Number of turn to perform the scan operation
        :return: None
        """
        self.set_cmd_goto(pos)
        self.remain_scan_ops = scan_dur

    def set_cmd_goto(self, pos=Position):
        """
        Set the position for the vehicle to move to
        :param pos: Destination position
        :return: None
        """
        if isinstance(pos, Position):
            self.dst_pos = pos
            self.src_pos = self.position

            move_cnt = math.sqrt(((self.dst_pos.x - self.src_pos.x) ** 2) +
                                 ((self.dst_pos.y - self.src_pos.y) ** 2))
            move_cnt = move_cnt / self.mov_speed
            move_cnt = math.ceil(move_cnt)
            self.remain_move_ops = move_cnt
            self.total_move_ops = move_cnt
        else:
            self.remain_move_ops = 0
            self.total_move_ops = 0

    def execute(self, ship_list=[]):
        """
        Execute the list of orders if available
        :param ship_list: List of ships in the game
        :return:
        """
        # Check if we need to reset the report
        if self.reset_report:
            self.report.clear()
            self.reset_report = False

        data = copy.deepcopy(UwCollectedData())
        if self.remain_move_ops > 0:
            self.execute_move()
        elif self.remain_scan_ops > 0:
            self.execute_scan(data=data, ship_list=ship_list)

        if ((len(self.orders) > 0)
                and (self.remain_move_ops == 0)
                and (self.remain_scan_ops == 0)):
            order = self.orders.pop(0)
            if isinstance(order, UwActionMoveScan):
                self.set_cmd(pos=order.goto_pos,
                             scan_dur=order.scan_dur)
            # elif isinstance(order, UwActionScan):
            #     self.set_cmd(scan_dur=order.scan_dur)

        if not self.is_idle():
            self.report.append(data)

            print("-----------------------------------------------")
            for report_data in self.report:
                print(report_data)

    def execute_move(self):
        """
        Compute the position of the ship
        :return: None
        """
        if self.remain_move_ops > 0:
            self.remain_move_ops -= 1
            curr_move_cnt = self.total_move_ops - self.remain_move_ops
            self.set_position(
                x=self.src_pos.x + math.floor((self.dst_pos.x - self.src_pos.x) / self.total_move_ops * curr_move_cnt),
                y=self.src_pos.y + math.floor((self.dst_pos.y - self.src_pos.y) / self.total_move_ops * curr_move_cnt))
        else:
            self.set_position(x=self.dst_pos.x,
                              y=self.dst_pos.y)

    def execute_scan(self, data, ship_list=[]):
        """
        Perform data gathering operation
        :param ship_list: list of ships in the game
        :return: None
        """
        if (self.remain_scan_ops > 0) and (self.remain_move_ops == 0):
            self.remain_scan_ops -= 1
            # Add the ship within scan area to report
            if isinstance(ship_list, collections.Iterable) and \
                    isinstance(data, UwCollectedData):
                for ship_info in ship_list:
                    if isinstance(ship_info, ShipInfo):
                        for area_placement in ship_info.area:
                            dist = math.sqrt(((area_placement[0] - self.position.x) ** 2) +
                                             ((area_placement[1] - self.position.y) ** 2))
                            if (dist <= self.scan_size) and (dist > 0):
                                # heading = math.atan((area_placement[0] - self.position.x) / (area_placement[1] - self.position.y))
                                # heading = get_heading([self.position.x, self.position.y], area_placement)
                                heading = get_heading([self.position.x, self.position.y],
                                                      [ship_info.position.x, ship_info.position.y])
                                print("Pos1 [%s, %s]  Pos2 [%s, %s] Heading %s" % (
                                    self.position.x, self.position.y,
                                    ship_info.position.x, ship_info.position.y,
                                    heading))

                                if heading < 22.5:
                                    data.N.append(ship_info)
                                elif heading < 67.5:
                                    data.NE.append(ship_info)
                                elif heading < 112.5:
                                    data.E.append(ship_info)
                                elif heading < 157.5:
                                    data.SE.append(ship_info)
                                elif heading < 202.5:
                                    data.S.append(ship_info)
                                elif heading < 247.5:
                                    data.SW.append(ship_info)
                                elif heading < 292.5:
                                    data.W.append(ship_info)
                                elif heading < 337.5:
                                    data.NW.append(ship_info)
                                else:
                                    data.N.append(ship_info)
                                break
                            # else do nothing as ship is not within range
                    # else data is not shipinfo, cannot proceed
            # else shipinfo list is not provided. cannot proceed
        # else do nothing

    def get_report(self):
        """
        Get the report gathered at the end of the order executed
        :return:
        """
        out_report = None
        if ((len(self.orders) == 0)
                and (self.remain_move_ops == 0)
                and (self.remain_scan_ops == 0)):
            out_report = self.report
        return out_report

    def is_idle(self):
        is_idle = True
        if ((len(self.orders) is not 0)
                or (self.remain_move_ops is not 0)
                or (self.remain_scan_ops is not 0)):
            is_idle = False
        return is_idle


# -----------------------------------------------------------------------
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
                "cloud_coverage_min": obj.cloud_coverage_min,
                "cloud_coverage_max": obj.cloud_coverage_max,
                "cloud_seed_cnt": obj.cloud_seed_cnt,
                "civilian_ship_count": obj.civilian_ship_count,
                "civilian_ship_move_probility": obj.civilian_ship_move_probility,
                "num_of_rounds": obj.num_of_rounds,
                "num_of_player": obj.num_of_player,
                "num_of_row": obj.num_of_row,
                "num_move_act": obj.num_move_act,
                "num_fire_act": obj.num_fire_act,
                "num_satcom_act": obj.num_satcom_act,
                "num_uw_action": obj.num_uw_action,
                "radar_cross_table": obj.radar_cross_table,
                "en_satellite": obj.en_satellite,
                "en_satellite_func2": obj.en_satellite_func2,
                "en_uw_action": obj.en_uw_action
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
            req_rep_conn=obj['req_rep_conn'],
            pub_sub_conn=obj['pub_sub_conn'],
            polling_rate=obj['polling_rate'],
            bc_rate=obj['bc_rate'],
            map_size=obj['map_size'],
            countdown_duration=obj['countdown_duration'],
            island_coverage=obj['island_coverage'],
            cloud_coverage_min=obj['cloud_coverage_min'],
            cloud_coverage_max=obj['cloud_coverage_max'],
            cloud_seed_cnt=obj['cloud_seed_cnt'],
            civilian_ship_count=obj['civilian_ship_count'],
            civilian_ship_move_probility=obj['civilian_ship_move_probility'],
            num_of_rounds=obj['num_of_rounds'],
            num_of_player=obj['num_of_player'],
            num_of_row=obj['num_of_row'],
            num_move_act=obj["num_move_act"],
            num_fire_act=obj["num_fire_act"],
            num_satcom_act=obj["num_satcom_act"],
            num_uw_action=obj["num_uw_action"],
            radar_cross_table=obj['radar_cross_table'],
            en_satellite=obj['en_satellite'],
            en_satellite_func2=obj['en_satellite_func2'],
            en_uw_action=obj['en_uw_action']
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


def get_heading(pos_1, pos_2):
    """
    Get the heading (based on true-north) of pos_2 from pos_1
    :param pos_1: Vehicle position
    :param pos_2: Dst position to compute the heading
    :return: heading; unit in degree (0 to 360)
    """
    heading = 0
    if isinstance(pos_1, collections.Iterable) and isinstance(pos_2, collections.Iterable):
        vec_a = [0, 1]
        vec_b = [(pos_2[0] - pos_1[0]), (pos_2[1] - pos_1[1])]
        mag_a = math.sqrt((vec_a[0] * vec_a[0]) + (vec_a[1] * vec_a[1]))
        mag_b = math.sqrt((vec_b[0] * vec_b[0]) + (vec_b[1] * vec_b[1]))

        dot_product = np.dot(vec_a, vec_b)
        heading = math.acos(dot_product / (mag_a * mag_b))

        if (pos_2[0] - pos_1[0]) < 0:
            # pos_2 is in the 3rd or 4th quadant; hence invert the sign
            heading = -heading

        heading = heading / math.pi * 180.0
        heading = ((heading + 180.0) % 360) - 180.0
        while heading < 0:
            heading += 360

    return heading
