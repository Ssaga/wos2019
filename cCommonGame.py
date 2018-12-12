from enum import Enum
from enum import IntEnum


class Action(Enum):
	NOP = 0
	FWD = 1
	CW = 2
	CCW = 3


class GameState(Enum):
	INIT = 0
	PLAY = 1
	STOP = 2


class Position :
	def __init__(self, x=0, y=0):
		self.x = x
		self.y = y


class Size :
	def __init__(self, x=0, y=0):
		self.x = x
		self.y = y

class Heading(IntEnum):
	NORTH = 0
	EAST = 1
	SOUTH = 2
	WEST = 3

class TurnDirection(IntEnum):
	CLOCKWISE = 0
	ANTICLOCKWISE = 1

# class ShipInfo :
# 	def __init__(self, ship_id=0, pos=Position(), size=Size(), heading=0):
# 		self.ship_id=ship_id
# 		self.pos=pos
# 		self.size=size
# 		self.heading=heading


class ShipInfo:
	def __init__(self, ship_id=0, position=Position(0, 0), heading=0, size=0, is_sunken=False):
		self.ship_id = ship_id
		# Position of of the ship head
		self.position = position
		self.heading = heading
		self.size = size
		self.is_sunken = is_sunken
		# list of position occupied by the vehicle
		# first position is the bow of the ship
		self.area = self.get_placement()

	def get_placement(self):
		placement = []
		return placement


class ShipMovementInfo :
	def __init__(self, ship_id, action=Action.NOP):
		self.ship_id = ship_id
		self.action_str = action.name


class FireInfo :
	def __init__(self, pos=Position()):
		self.pos=pos

class SatcomInfo:
	def __init__(self, a=0, b=0, c=0, d=0, e=0, f=0, g=0, h=0):
		self.a = a
		self.b = b
		self.c = c
		self.d = d
		self.e = e
		self.f = f
		self.g = g
		self.h = h

class GameConfig:
	def __init__(self, num_of_rounds=0, en_satillite=False, en_submarine=False):
		self.num_of_rounds = int(num_of_rounds)
		self.en_satillite = bool(en_satillite)
		self.en_submarine = bool(en_submarine)
		
class GameStatus:
	def __init__(self,
				 game_state=GameState.INIT,
				 game_round=0,
				 player_turn=0):
		self.game_state_str = game_state.name
		self.game_round = game_round
		self.player_turn = player_turn

	def get_enum_game_state(self):
		return GameState[self.game_state_str]
