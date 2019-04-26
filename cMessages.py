import cCommonGame
import collections
import numpy as np
import json


class Msg:
    def __init__(self, type_id):
        self.type_id = type_id


class MsgReq(Msg):
    def __init__(self, player_id, type_id):
        Msg.__init__(self, type_id)
        self.player_id = player_id


class MsgRep(Msg):
    def __init__(self, type_id):
        Msg.__init__(self, type_id)


# ----------------------------------------------------------

class MsgReqRegister(MsgReq):
    def __init__(self, player_id):
        MsgReq.__init__(self, player_id, 0)


class MsgReqRegShips(MsgReq):
    def __init__(self, player_id, ship_list=[], uw_ship_list=[]):
        MsgReq.__init__(self, player_id, 1)

        self.ship_list = []
        if isinstance(ship_list, collections.Iterable):
            self.ship_list.extend(ship_list)
        else:
            self.ship_list.append(ship_list)

        self.uw_ship_list = []
        if isinstance(uw_ship_list, collections.Iterable):
            self.uw_ship_list.extend(uw_ship_list)
        else:
            self.uw_ship_list.append(uw_ship_list)


class MsgReqConfig(MsgReq):
    def __init__(self, player_id):
        MsgReq.__init__(self, player_id, 2)


class MsgReqTurnInfo(MsgReq):
    def __init__(self, player_id):
        MsgReq.__init__(self, player_id, 3)


class MsgReqTurnMoveAct(MsgReq):
    def __init__(self, player_id, move=[]):
        MsgReq.__init__(self, player_id, 4)
        self.move = []
        if isinstance(move, collections.Iterable):
            self.move.extend(move)
        else:
            self.move.append(move)


class MsgReqTurnFireAct(MsgReq):
    def __init__(self, player_id, fire=[]):
        MsgReq.__init__(self, player_id, 5)
        self.fire = []
        if isinstance(fire, collections.Iterable):
            self.fire.extend(fire)
        else:
            self.fire.append(fire)


class MsgReqTurnSatAct(MsgReq):
    def __init__(self, player_id, satcom=cCommonGame.SatcomInfo()):
        MsgReq.__init__(self, player_id, 6)
        self.satcom = satcom

    def __repr__(self):
        return str(vars(self))


class MsgReqUwAction(MsgReq):
    def __init__(self, player_id, uw_ship_mov_inf_list=[]):
        """
        Constructor for the MsgReqUwAction
        :param player_id: id of the given player
        :param uw_ship_mov_inf_list: list of cCommonGame.UwShipMovementInfo
        """
        MsgReq.__init__(self, player_id, 7)
        is_ok = True
        if isinstance(uw_ship_mov_inf_list, collections.Iterable):
            for uw_ship_mov_inf in uw_ship_mov_inf_list:
                if isinstance(uw_ship_mov_inf, cCommonGame.UwShipMovementInfo) is False:
                    is_ok = False
        else:
            is_ok = False

        self.uw_ship_mov_inf = list()
        if is_ok:
            self.uw_ship_mov_inf.extend(uw_ship_mov_inf_list)


class MsgReqUwReport(MsgReq):
    def __init__(self, player_id, ship_id):
        MsgReq.__init__(self, player_id, 8)
        self.ship_id = ship_id


# ----------------------------------------------------------

class MsgRepUwReport(MsgRep):
    def __init__(self, ack=False, report=[]):
        MsgRep.__init__(self, 132)
        self.ack = ack
        self.report = report


class MsgRepGameConfig(MsgRep):
    def __init__(self, ack=False, config=cCommonGame.GameConfig()):
        MsgRep.__init__(self, 131)
        self.ack = ack
        self.config = config


class MsgRepTurnInfo(MsgRep):
    def __init__(self,
                 ack=False,
                 self_ship_list=[],
                 self_uw_ship_list=[],
                 enemy_ship_list=[],
                 other_ship_list=[],
                 bombardment_list=[],
                 map_data=[]):
        MsgRep.__init__(self, 130)
        self.ack = ack
        self.self_ship_list = self_ship_list
        self.self_uw_ship_list = self_uw_ship_list
        self.enemy_ship_list = enemy_ship_list
        self.other_ship_list = other_ship_list
        self.bombardment_list = bombardment_list
        self.map_data = map_data


class MsgRepAckMap(MsgRep):
    def __init__(self, ack=False, map_data=[]):
        MsgRep.__init__(self, 129)
        self.ack = ack
        self.map_data = map_data


class MsgRepAck(MsgRep):
    def __init__(self, ack=False):
        MsgRep.__init__(self, 128)
        self.ack = ack


# ----------------------------------------------------------


class MsgPubGameStatus(Msg):
    def __init__(self,
                 game_state=cCommonGame.GameState.INIT,
                 game_round=0,
                 player_turn=0,
                 time_remain=0):
        Msg.__init__(self, 255)
        self.game_state = game_state
        self.game_round = game_round
        self.player_turn = player_turn
        self.time_remain = time_remain

    def to_string(self):
        return "Round: %s, Turn: %s, Time Remain: %s" % (self.game_round, self.player_turn, self.time_remain)


# ----------------------------------------------------------


class MsgJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        result = None
        if isinstance(obj, cCommonGame.Position):
            result = {
                "__class__": "Position",
                "x": obj.x,
                "y": obj.y
            }

        elif isinstance(obj, cCommonGame.Size):
            result = {
                "__class__": "Size",
                "x": obj.x,
                "y": obj.y
            }

        elif isinstance(obj, cCommonGame.Boundary):
            result = {
                "__class__": "Boundary",
                "min_x": obj.min_x,
                "max_x": obj.max_x,
                "min_y": obj.min_y,
                "max_y": obj.max_y
            }

        elif isinstance(obj, cCommonGame.ShipInfo):
            result = {
                "__class__": "ShipInfo",
                "ship_id": obj.ship_id,
                "ship_type": obj.ship_type,
                "position": obj.position,
                "heading": obj.heading,
                "size": obj.size,
                "is_sunken": obj.is_sunken
            }

        elif isinstance(obj, cCommonGame.UwShipInfo):
            result = {
                "__class__": "UwShipInfo",
                "ship_id": obj.ship_id,
                "ship_type": obj.ship_type,
                "position": obj.position,
                "size": obj.size,
                "is_sunken": obj.is_sunken
            }

        elif isinstance(obj, cCommonGame.ShipMovementInfo):
            result = {
                "__class__": "ShipMovementInfo",
                "ship_id": obj.ship_id,
                "action_str": obj.action_str
            }

        elif isinstance(obj, cCommonGame.FireInfo):
            result = {
                "__class__": "FireInfo",
                "pos": obj.pos
            }

        elif isinstance(obj, cCommonGame.SatcomInfo):
            result = {
                "__class__": "SatcomInfo",
                "a": obj.a,
                "e": obj.e,
                "i": obj.i,
                "om": obj.om,
                "Om": obj.Om,
                "M": obj.M,
                "is_enable": obj.is_enable,
                "is_rhs": obj.is_rhs
            }

        elif isinstance(obj, cCommonGame.UwActionMoveScan):
            result = {
                "__class__": "UwActionMoveScan",
                "goto_pos": obj.goto_pos,
                "scan_dur": obj.scan_dur
            }

        elif isinstance(obj , cCommonGame.UwShipMovementInfo):
            result = {
                "__class__": "UwShipMovementInfo",
                "ship_id": obj.ship_id,
                "uw_actions": obj.uw_actions
            }

        # elif isinstance(obj, cCommonGame.UwActionScan):
        #     result = {
        #         "__class__": "UwActionScan",
        #         "scan_dur": obj.scan_dur
        #     }
        #
        # elif isinstance(obj, cCommonGame.UwActionNop):
        #     result = {
        #         "__class__": "UwActionNop"
        #     }

        elif isinstance(obj, cCommonGame.GameConfig):
            result = {
                "__class__": "GameConfig",
                "num_of_players": obj.num_of_players,
                "num_of_rounds": obj.num_of_rounds,
                "num_of_fire_act": obj.num_of_fire_act,
                "num_of_move_act": obj.num_of_move_act,
                "num_of_satc_act": obj.num_of_satc_act,
                "num_of_rows": obj.num_of_rows,
                "polling_rate": obj.polling_rate,
                "map_size": obj.map_size,
                "boundary": obj.boundary,
                "en_satellite": obj.en_satellite,
                "en_satellite_func2": obj.en_satellite_func2,
                "en_submarine": obj.en_submarine
            }

        # elif isinstance(obj, cCommonGame.GameStatus):
        #     result = {
        #         "__class__": "GameStatus",
        #         "game_state": obj.game_state,
        #         "game_round": obj.game_round,
        #         "player_turn": obj.player_turn,
        #         "time_remain": obj.time_remain
        #     }

        elif isinstance(obj, MsgReqRegister):
            result = {
                "__class__": "MsgReqRegister",
                "type_id": obj.type_id,
                "player_id": obj.player_id
            }
        elif isinstance(obj, MsgReqRegShips):
            result = {
                "__class__": "MsgReqRegShips",
                "type_id": obj.type_id,
                "player_id": obj.player_id,
                "ship_list": obj.ship_list,
                "uw_ship_list": obj.uw_ship_list
            }
        elif isinstance(obj, MsgReqConfig):
            result = {
                "__class__": "MsgReqConfig",
                "type_id": obj.type_id,
                "player_id": obj.player_id
            }
        elif isinstance(obj, MsgReqTurnInfo):
            result = {
                "__class__": "MsgReqTurnInfo",
                "type_id": obj.type_id,
                "player_id": obj.player_id
            }
        elif isinstance(obj, MsgReqTurnMoveAct):
            result = {
                "__class__": "MsgReqTurnMoveAct",
                "type_id": obj.type_id,
                "player_id": obj.player_id,
                "move": obj.move
            }
        elif isinstance(obj, MsgReqTurnFireAct):
            result = {
                "__class__": "MsgReqTurnFireAct",
                "type_id": obj.type_id,
                "player_id": obj.player_id,
                "fire": obj.fire
            }
        elif isinstance(obj, MsgReqTurnSatAct):
            result = {
                "__class__": "MsgReqTurnSatAct",
                "type_id": obj.type_id,
                "player_id": obj.player_id,
                "satcom": obj.satcom
            }
        elif isinstance(obj, MsgReqUwAction):
            result = {
                "__class__": "MsgReqUwAction",
                "type_id": obj.type_id,
                "player_id": obj.player_id,
                "uw_ship_mov_inf": obj.uw_ship_mov_inf
            }
        elif isinstance(obj, MsgReqUwReport):
            result = {
                "__class__": "MsgReqUwReport",
                "type_id": obj.type_id,
                "player_id": obj.player_id,
                "ship_id": obj.ship_id
            }
        elif isinstance(obj, MsgRepAck):
            result = {
                "__class__": "MsgRepAck",
                "type_id": obj.type_id,
                "ack": obj.ack
            }
        elif isinstance(obj, MsgRepAckMap):
            result = {
                "__class__": "MsgRepAckMap",
                "type_id": obj.type_id,
                "ack": obj.ack,
                "map_data": obj.map_data
            }
        elif isinstance(obj, MsgRepGameConfig):
            result = {
                "__class__": "MsgRepGameConfig",
                "type_id": obj.type_id,
                "ack": obj.ack,
                "config": obj.config
            }
        elif isinstance(obj, MsgRepTurnInfo):
            result = {
                "__class__": "MsgRepTurnInfo",
                "type_id": obj.type_id,
                "ack": obj.ack,
                "self_ship_list": obj.self_ship_list,
                "self_uw_ship_list": obj.self_uw_ship_list,
                "enemy_ship_list": obj.enemy_ship_list,
                "other_ship_list": obj.other_ship_list,
                "bombardment_list": obj.bombardment_list,
                "map_data": obj.map_data
            }
        elif isinstance(obj, MsgRepUwReport):
            result = {
                "__class__": "MsgRepUwReport",
                "type_id": obj.type_id,
                "ack": obj.ack,
                "report": obj.report
            }
        elif isinstance(obj, MsgPubGameStatus):
            result = {
                "__class__": "MsgPubGameStatus",
                "type_id": obj.type_id,
                "game_state": obj.game_state.name,
                "game_round": obj.game_round,
                "player_turn": obj.player_turn,
                "time_remain": obj.time_remain
            }

        # TODO: remove the following numpy conversion by checking for
        #  		the cause of the numpy integer if time permit
        elif isinstance(obj, np.integer):
            result = int(obj)

        elif isinstance(obj, np.floating):
            result = float(obj)

        elif isinstance(obj, np.ndarray):
            result = obj.tolist()

        else:
            print(type(obj))
            result = super().default(obj)

        return result


class MsgJsonDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        result = None
        if '__class__' not in obj:
            result = obj
        else:
            class_type = obj['__class__']
            if class_type == 'Position':
                result = self.parse_position(obj)
            elif class_type == 'Size':
                result = self.parse_size(obj)
            elif class_type == 'Boundary':
                result = self.parse_boundary(obj)
            elif class_type == 'ShipInfo':
                result = self.parse_ship_info(obj)
            elif class_type == 'UwShipInfo':
                result = self.parse_uw_ship_info(obj)
            elif class_type == 'ShipMovementInfo':
                result = self.parse_ship_move_info(obj)
            elif class_type == 'FireInfo':
                result = self.parse_fire_info(obj)
            elif class_type == 'SatcomInfo':
                result = self.parse_satcom_info(obj)
            elif class_type == 'UwActionMoveScan':
                result = self.parse_uw_move_scan(obj)
            elif class_type == 'UwShipMovementInfo':
                result = self.parse_uw_movement_info(obj)
            # elif class_type == 'UwActionScan':
            #     result = self.parse_uw_scan(obj)
            # elif class_type == 'UwActionNop':
            #     result = self.parse_uw_nop(obj)
            elif class_type == 'GameConfig':
                result = self.parse_game_config(obj)
            # elif class_type == 'GameStatus':
            #      result = self.parse_game_status(obj)
            elif class_type == 'MsgReqRegister':
                result = self.parse_req_client_register(obj)
            elif class_type == 'MsgReqRegShips':
                result = self.parse_req_ships_placement(obj)
            elif class_type == 'MsgReqConfig':
                result = self.parse_req_game_config(obj)
            elif class_type == 'MsgReqTurnInfo':
                result = self.parse_req_turn_info(obj)
            elif class_type == 'MsgReqTurnMoveAct':
                result = self.parse_req_turn_move_act(obj)
            elif class_type == 'MsgReqTurnFireAct':
                result = self.parse_req_turn_fire_act(obj)
            elif class_type == 'MsgReqTurnSatAct':
                result = self.parse_req_turn_sat_act(obj)
            elif class_type == 'MsgReqUwAction':
                result = self.parse_req_uw_action(obj)
            elif class_type == 'MsgReqUwReport':
                result = self.parse_req_uw_report(obj)
            elif class_type == 'MsgRepAck':
                result = self.parse_ack(obj)
            elif class_type == 'MsgRepAckMap':
                result = self.parse_ack_map(obj)
            elif class_type == 'MsgRepGameConfig':
                result = self.parse_ack_game_config(obj)
            elif class_type == 'MsgRepTurnInfo':
                result = self.parse_ack_turn_info(obj)
            elif class_type == 'MsgRepUwReport':
                result = self.parse_ack_uw_report(obj)
            elif class_type == 'MsgPubGameStatus':
                result = self.parse_pub_game_status(obj)
            else:
                print("Unsupported class type")

        return result

    @staticmethod
    def parse_position(obj):
        return cCommonGame.Position(
            obj['x'],
            obj['y']
        )

    @staticmethod
    def parse_size(obj):
        return cCommonGame.Size(
            obj['x'],
            obj['y']
        )

    @staticmethod
    def parse_boundary(obj):
        return cCommonGame.Boundary(
            obj['min_x'],
            obj['max_x'],
            obj['min_y'],
            obj['max_y']
        )

    @staticmethod
    def parse_ship_info(obj):
        return cCommonGame.ShipInfo(
            obj['ship_id'],
            obj['position'],
            obj['heading'],
            obj['size'],
            obj['is_sunken'],
            obj['ship_type']
        )

    @staticmethod
    def parse_uw_ship_info(obj):
        return cCommonGame.UwShipInfo(
            obj['ship_id'],
            obj['position'],
            obj['size'],
            obj['is_sunken'],
            obj['ship_type']
        )

    @staticmethod
    def parse_ship_move_info(obj):
        return cCommonGame.ShipMovementInfo(
            obj['ship_id'],
            cCommonGame.Action[obj['action_str']]
        )

    @staticmethod
    def parse_fire_info(obj):
        return cCommonGame.FireInfo(
            obj['pos']
        )

    @staticmethod
    def parse_satcom_info(obj):
        return cCommonGame.SatcomInfo(
            obj['a'],
            obj['e'],
            obj['i'],
            obj['om'],
            obj['Om'],
            obj['M'],
            obj['is_enable'],
            obj['is_rhs']
        )

    @staticmethod
    def parse_uw_move_scan(obj):
        return cCommonGame.UwActionMoveScan(
            obj['goto_pos'],
            obj['scan_dur']
        )

    @staticmethod
    def parse_uw_movement_info(obj):
        return cCommonGame.UwShipMovementInfo(
            ship_id=obj['ship_id'],
            actions=obj['uw_actions']
        )

    # @staticmethod
    # def parse_uw_scan(obj):
    #     return cCommonGame.UwActionScan(
    #         obj['scan_dur']
    #     )

    # @staticmethod
    # def parse_uw_nop(obj):
    #     return cCommonGame.UwActionNop()

    @staticmethod
    def parse_game_config(obj):
        return cCommonGame.GameConfig(
            obj['num_of_players'],
            obj['num_of_rounds'],
            obj['num_of_fire_act'],
            obj['num_of_move_act'],
            obj['num_of_satc_act'],
            obj['num_of_rows'],
            obj['polling_rate'],
            obj['map_size'],
            obj['boundary'],
            obj['en_satellite'],
            obj['en_satellite_func2'],
            obj['en_submarine']
        )

    @staticmethod
    def parse_req_client_register(obj):
        return MsgReqRegister(
            obj['player_id']
        )

    @staticmethod
    def parse_req_ships_placement(obj):
        return MsgReqRegShips(
            obj['player_id'],
            obj['ship_list'],
            obj['uw_ship_list'],
        )

    @staticmethod
    def parse_req_game_config(obj):
        return MsgReqConfig(
            obj['player_id']
        )

    @staticmethod
    def parse_req_turn_info(obj):
        return MsgReqTurnInfo(
            obj['player_id']
        )

    @staticmethod
    def parse_req_turn_move_act(obj):
        return MsgReqTurnMoveAct(
            obj['player_id'],
            obj['move']
        )

    @staticmethod
    def parse_req_turn_fire_act(obj):
        return MsgReqTurnFireAct(
            obj['player_id'],
            obj['fire']
        )

    @staticmethod
    def parse_req_turn_sat_act(obj):
        return MsgReqTurnSatAct(
            obj['player_id'],
            obj['satcom']
        )

    @staticmethod
    def parse_req_uw_action(obj):
        return MsgReqUwAction(
            obj['player_id'],
            obj['uw_ship_mov_inf']
        )

    @staticmethod
    def parse_req_uw_report(obj):
        return MsgReqUwReport(
            obj['player_id'],
            obj['ship_id']
        )

    @staticmethod
    def parse_ack(obj):
        return MsgRepAck(
            obj['ack']
        )

    @staticmethod
    def parse_ack_map(obj):
        return MsgRepAckMap(
            obj['ack'],
            obj['map_data']
        )

    @staticmethod
    def parse_ack_game_config(obj):
        return MsgRepGameConfig(
            obj['ack'],
            obj['config']
        )

    @staticmethod
    def parse_ack_turn_info(obj):
        return MsgRepTurnInfo(
            obj['ack'],
            obj['self_ship_list'],
            obj['self_uw_ship_list'],
            obj['enemy_ship_list'],
            obj['other_ship_list'],
            obj['bombardment_list'],
            obj['map_data']
        )

    @staticmethod
    def parse_ack_uw_report(obj):
        return MsgRepUwReport(
            obj['ack'],
            obj['report']
        )


    @staticmethod
    def parse_pub_game_status(obj):
        return MsgPubGameStatus(
            cCommonGame.GameState[obj['game_state']],
            obj['game_round'],
            obj['player_turn'],
            obj['time_remain']
        )
