import json
import numpy as np

from cCommonCommEngine import ConnInfo
from cCommonGame import Size
from cCommonGame import Position
from cCommonGame import GameState

class ServerGameConfig:
	def __init__(self,
				 req_rep_conn=ConnInfo('127.0.0.1', 5556),
				 pub_sub_conn=ConnInfo('127.0.0.1', 5557),
				 polling_rate=1000,
				 bc_rate=1000,
				 map_size=Size(120, 120),
				 island_coverage=0,
				 cloud_coverage=0,
				 civilian_ship_count=0,
				 civilian_ship_move_probility=0.25,
				 num_of_rounds=0,
				 num_of_player=4,
				 num_of_row=2,
				 num_move_act=2,
				 num_fire_act=1,
				 num_satcom_act=1,
				 radar_cross_table=[1.0, 1.0, 1.0, 1.0],
				 en_satillite=False,
				 en_submarine=False):
		self.req_rep_conn = req_rep_conn
		self.pub_sub_conn = pub_sub_conn
		self.polling_rate = polling_rate
		self.bc_rate = bc_rate
		self.map_size = map_size
		self.island_coverage = island_coverage
		self.cloud_coverage = cloud_coverage
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
		self.en_satillite = bool(en_satillite)
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
				 player_turn=0
				 ):
		self.game_state = game_state
		# game round start count from 1
		self.game_round = game_round
		# player turn start count from 1
		self.player_turn = player_turn
		self.allowed_action = PlayerTurnActionCount(default_move, default_fire, default_satcom)
		self.remaining_action = PlayerTurnActionCount(0, 0, 0)
		self.clear_turn_remaining_action()

	def __repr__(self):
		return str(vars(self))

	def reset_turn_remaining_action(self):
		self.remaining_action.remain_move = self.allowed_action.remain_move
		self.remaining_action.remain_fire = self.allowed_action.remain_fire
		self.remaining_action.remain_satcom = self.allowed_action.remain_satcom

	def clear_turn_remaining_action(self):
		self.remaining_action.remain_move = 0
		self.remaining_action.remain_fire = 0
		self.remaining_action.remain_satcom = 0


class ShipInfo:
	def __init__(self,
				 ship_id=0,
				 position=Position(0, 0),
				 heading=0,
				 size=0,
				 is_sunken=False):
		self.ship_id = ship_id
		# Position of of the ship head
		self.position = position
		self.heading = heading
		self.size = size
		self.is_sunken = is_sunken
		# list of position occupied by the vehicle
		# first position is the bow of the ship
		self.area = self.get_placement()

	def __repr__(self):
		return str(vars(self))

	def move_forward(self):
		head_rad = self.heading * np.pi / 180.0
		pos = np.array([0, -1])
		kin_mat = np.array([[np.cos(head_rad), np.sin(head_rad)],
							[-np.sin(head_rad), np.cos(head_rad)]])
		transpose = np.dot(pos, kin_mat)
		transpose = transpose.astype(int)
		self.position.x += transpose[0]
		self.position.y += transpose[1]
		self.area = self.get_placement()

	def turn_clockwise(self):
		self.heading += 90
		self.area = self.get_placement()

	def turn_counter_clockwise(self):
		self.heading -= 90
		self.area = self.get_placement()

	def get_placement(self):
		# Get the index of the ship
		placement = np.array([np.zeros(self.size), np.arange(0, self.size), np.ones(self.size)])
		placement = np.transpose(placement)

		# Get the kinematic matrix
		head_rad = self.heading * np.pi / 180.0
		kin_mat = np.array([[np.cos(head_rad),	np.sin(head_rad),	0],
							[-np.sin(head_rad),	np.cos(head_rad),	0],
							[self.position.x,	self.position.y,	1]])

		# compute the ship placement
		placement = np.dot(placement, kin_mat)
		placement = np.delete(placement, -1, 1)
		placement = np.round(placement)
		# remove the negative 0
		placement += 0.

		return placement.tolist()

#-----------------------------------------------------------------------
class SvrCfgJsonEncoder(json.JSONEncoder):
	def default(self, obj):
		result = None
		if isinstance(obj, ConnInfo):
			result = {
				"__class__":"ConnInfo",
				"addr":obj.addr,
				"port":obj.port
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
				"req_rep_conn":obj.req_rep_conn,
				"pub_sub_conn":obj.pub_sub_conn,
				"polling_rate": obj.polling_rate,
				"bc_rate": obj.bc_rate,
				"map_size": obj.map_size,
				"island_coverage": obj.island_coverage,
				"cloud_coverage": obj.cloud_coverage,
				"civilian_ship_count": obj.civilian_ship_count,
				"civilian_ship_move_probility": obj.civilian_ship_move_probility,
				"num_of_rounds": obj.num_of_rounds,
				"num_of_player": obj.num_of_player,
				"num_of_row": obj.num_of_row,
				"num_move_act": obj.num_move_act,
				"num_fire_act": obj.num_fire_act,
				"num_satcom_act": obj.num_satcom_act,
				"radar_cross_table": obj.radar_cross_table,
				"en_satillite": obj.en_satillite,
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

	def parse_conn_info(self, obj):
		return ConnInfo(
			obj['addr'],
			obj['port']
		)

	def parse_size(self, obj):
		return Size(
			obj['x'],
			obj['y']
		)

	def parse_svr_game_cfg(self, obj):
		return ServerGameConfig(
			obj['req_rep_conn'],
			obj['pub_sub_conn'],
			obj['polling_rate'],
			obj['bc_rate'],
			obj['map_size'],
			obj['island_coverage'],
			obj['cloud_coverage'],
			obj['civilian_ship_count'],
			obj['civilian_ship_move_probility'],
			obj['num_of_rounds'],
			obj['num_of_player'],
			obj['num_of_row'],
			obj["num_move_act"],
			obj["num_fire_act"],
			obj["num_satcom_act"],
			obj['radar_cross_table'],
			obj['en_satillite'],
			obj['en_submarine']
		)
