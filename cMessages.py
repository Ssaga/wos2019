import cCommonGame
import collections
import numpy as np
import json

from copy import deepcopy

class Msg:
	def __init__(self,type_id):
		self.type_id = type_id


class MsgReq(Msg):
	def __init__(self, player_id, type_id):
		Msg.__init__(self, type_id)
		self.player_id = player_id


class MsgRep(Msg):
	def __init__(self, type_id):
		Msg.__init__(self, type_id)


#----------------------------------------------------------

class MsgReqRegister(MsgReq):
	def __init__(self, player_id):
		MsgReq.__init__(self, player_id, 0)


class MsgReqRegShips(MsgReq):
	def __init__(self, player_id, ship_list=[]):
		MsgReq.__init__(self, player_id, 1)
		self.ship_list = []
		if isinstance(ship_list, collections.Iterable):
			self.ship_list.extend(ship_list)
		else:
			self.ship_list.append(ship_list)


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


# class MsgReqTurnAction(MsgReq):
# 	def __init__(self, player_id):
# 		MsgReq.__init__(self, player_id, 7)
# 		self.action = []

#----------------------------------------------------------

class MsgRepGameConfig(MsgRep):
	def __init__(self, ack=False, config=cCommonGame.GameConfig()):
		MsgRep.__init__(self, 131)
		self.ack = ack
		self.config = config


class MsgRepTurnInfo(MsgRep):
	def __init__(self,
				 ack=False,
				 self_ship_list=[],
				 enemy_ship_list=[],
				 other_ship_list=[],
				 bombardment_list=[],
				 map_data=[]):
		MsgRep.__init__(self, 130)
		self.ack = ack
		self.self_ship_list = self_ship_list
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


#----------------------------------------------------------


class MsgPubGameStatus(MsgRep):
	def __init__(self,
				 game_state = cCommonGame.GameState.INIT,
				 player_turn = 0,
				 game_round = 0):
		MsgRep.__init__(self, 255)
		self.game_state = game_state
		self.player_turn = player_turn
		self.game_round =  game_round


#----------------------------------------------------------


class MsgJsonEncoder(json.JSONEncoder):
	def default(self, obj):
		result = None
		if isinstance(obj, cCommonGame.Position):
			result = {
				"__class__":"Position",
				"x":obj.x,
				"y":obj.y
			}

		elif isinstance(obj, cCommonGame.Size):
			result = {
				"__class__": "Size",
				"x":obj.x,
				"y":obj.y
			}

		elif isinstance(obj, cCommonGame.ShipInfo):
			result = {
				"__class__": "ShipInfo",
				"ship_id": obj.ship_id,
				"position": obj.position,
				"heading": obj.heading,
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
				"b": obj.b,
				"c": obj.c,
				"d": obj.d,
				"e": obj.e,
				"f": obj.f,
				"is_sar": obj.is_sar,
				"is_rhs": obj.is_rhs
			}

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
				"en_satillite": obj.en_satillite,
				"en_submarine": obj.en_submarine
			}

		elif isinstance(obj, cCommonGame.GameStatus):
			result = {
				"__class__": "GameStatus",
				"game_state_str": obj.game_state_str,
				"game_round": obj.game_round,
				"player_turn": obj.player_turn
			}

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
				"ship_list": obj.ship_list
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
				"enemy_ship_list": obj.enemy_ship_list,
				"other_ship_list": obj.other_ship_list,
				"bombardment_list": obj.bombardment_list,
				"map_data": obj.map_data
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
			elif class_type == 'ShipInfo':
				 result = self.parse_ship_info(obj)
			elif class_type == 'ShipMovementInfo':
				 result = self.parse_ship_move_info(obj)
			elif class_type == 'FireInfo':
				 result = self.parse_fire_info(obj)
			elif class_type == 'SatcomInfo':
				 result = self.parse_satcom_info(obj)
			elif class_type == 'GameConfig':
				 result = self.parse_game_config(obj)
			elif class_type == 'GameStatus':
				 result = self.parse_game_status(obj)
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
			elif class_type == 'MsgRepAck':
				 result = self.parse_ack(obj)
			elif class_type == 'MsgRepAckMap':
				 result = self.parse_ack_map(obj)
			elif class_type == 'MsgRepGameConfig':
				 result = self.parse_ack_game_config(obj)
			elif class_type == 'MsgRepTurnInfo':
				 result = self.parse_ack_turn_info(obj)
			else:
				print("Unsupported class type")

		return result

	def parse_position(self, obj):
		return cCommonGame.Position(obj['x'], obj['y'])

	def parse_size(self, obj):
		return cCommonGame.Size(obj['x'], obj['y'])

	def parse_ship_info(self, obj):
		return cCommonGame.ShipInfo(
			obj['ship_id'],
			obj['position'],
			obj['heading'],
			obj['size'],
			obj['is_sunken']
		)

	def parse_ship_move_info(self, obj):
		return cCommonGame.ShipMovementInfo(
			obj['ship_id'],
			cCommonGame.Action[obj['action_str']]
		)

	def parse_fire_info(self, obj):
		return cCommonGame.FireInfo(
			obj['pos']
		)

	def parse_satcom_info(self, obj):
		return cCommonGame.SatcomInfo(
			obj['a'],
			obj['b'],
			obj['c'],
			obj['d'],
			obj['e'],
			obj['f'],
			obj['is_sar'],
			obj['is_rhs']
		)

	def parse_game_config(self, obj):
		return cCommonGame.GameConfig(
			obj['num_of_players'],
			obj['num_of_rounds'],
			obj['num_of_fire_act'],
			obj['num_of_move_act'],
			obj['num_of_satc_act'],
			obj['num_of_rows'],
			obj['polling_rate'],
			obj['map_size'],
			obj['en_satillite'],
			obj['en_submarine']
		)

	def parse_game_status(self, obj):
		return cCommonGame.GameStatus(
			cCommonGame.GameState[obj['game_state_str']],
			obj['game_round'],
			obj['player_turn']
		)

	def parse_req_client_register(self, obj):
		return MsgReqRegister(
			obj['player_id']
		)

	def parse_req_ships_placement(self, obj):
		return MsgReqRegShips(
			obj['player_id'],
			obj['ship_list']
		)

	def parse_req_game_config(self, obj):
		return MsgReqConfig(
			obj['player_id']
		)

	def parse_req_turn_info(self, obj):
		return MsgReqTurnInfo(
			obj['player_id']
		)

	def parse_req_turn_move_act(self, obj):
		return MsgReqTurnMoveAct(
			obj['player_id'],
			obj['move']
		)

	def parse_req_turn_fire_act(self, obj):
		return MsgReqTurnFireAct(
			obj['player_id'],
			obj['fire']
		)

	def parse_req_turn_sat_act(self, obj):
		return MsgReqTurnSatAct(
			obj['player_id'],
			obj['satcom']
		)

	def parse_ack(self, obj):
		return MsgRepAck(
			obj['ack']
		)

	def parse_ack_map(self, obj):
		return MsgRepAckMap(
			obj['ack'],
			obj['map_data']
		)

	def parse_ack_game_config(self, obj):
		return MsgRepGameConfig(
			obj['ack'],
			obj['config']
		)

	def parse_ack_turn_info(self, obj):
		return MsgRepTurnInfo(
			obj['ack'],
			obj['self_ship_list'],
			obj['enemy_ship_list'],
			obj['other_ship_list'],
			obj['bombardment_list'],
			obj['map_data']
		)
