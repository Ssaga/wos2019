import json

from cCommonCommEngine import ConnInfo
from cCommonGame import Size
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
				 num_of_rounds=0,
				 num_of_player=4,
				 num_of_row=2,
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
		self.num_of_rounds = int(num_of_rounds)
		self.num_of_player = int(num_of_player)
		self.num_of_row = int(num_of_row)
		self.radar_cross_table = []
		self.radar_cross_table.extend(radar_cross_table)
		self.en_satillite = bool(en_satillite)
		self.en_submarine = bool(en_submarine)


class PlayerStatus:
	def __init__(self):
		self.ship_list = []
		self.hit_count = 0


class PlayerTurnActionCount:
	def __init__(self, remain_move, remain_fire, remain_satcom):
		self.remain_move = remain_move
		self.remain_fire = remain_fire
		self.remain_satcom = remain_satcom


class GameTurnStatus:

	def __init__(self,
				 game_state=GameState.INIT,
				 game_round=0,
				 player_turn=0,
				 default_move=0,
				 default_fire = 0,
				 default_satcom=0
				 ):
		self.game_state = game_state
		self.game_round = game_round
		self.player_turn = player_turn
		self.allowed_action = PlayerTurnActionCount(default_move, default_fire, default_satcom)
		self.remaining_action = PlayerTurnActionCount(0, 0, 0)
		self.clear_turn_remaining_action()

	def reset_turn_remaining_action(self):
		self.remaining_action.move = self.allowed_action.move
		self.remaining_action.fire = self.allowed_action.fire
		self.remaining_action.satcom = self.allowed_action.satcom

	def clear_turn_remaining_action(self):
		self.remaining_action.move = 0
		self.remaining_action.fire = 0
		self.remaining_action.satcom = 0


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
				"num_of_rounds": obj.num_of_rounds,
				"num_of_player": obj.num_of_player,
				"num_of_row": obj.num_of_row,
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
			obj['num_of_rounds'],
			obj['num_of_player'],
			obj['num_of_row'],
			obj['radar_cross_table'],
			obj['en_satillite'],
			obj['en_submarine']
		)
