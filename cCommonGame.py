from enum import Enum
from enum import IntEnum
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
import numpy as np

class MapData(IntEnum):
    WATER = 0				# Sea / Uncovered
    ISLAND = 1
    CLOUD_FRIENDLY = 2		# Cloud in friendly area
    CLOUD_HOSTILE = 4		# Cloud in hostile area
    FOG_OF_WAR = 128

class Action(Enum):
    NOP = 0
    FWD = 1
    CW = 2
    CCW = 3


class GameState(Enum):
    INIT = 0
    PLAY_INPUT = 1
    PLAY_COMPUTE = 2
    STOP = 3


class Position:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __repr__(self):
        return str(vars(self))


class Size:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __repr__(self):
        return str(vars(self))


class Boundary:
    def __init__(self, min_x=0, max_x=0, min_y=0, max_y=0):
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y

    def __repr__(self):
        return str(vars(self))

class Heading(IntEnum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3


class ShipInfo(QObject):
    moved = pyqtSignal(int, int)
    rotated = pyqtSignal(float)

    def __init__(self, ship_id=0, position=Position(0, 0), heading=0, size=0, is_sunken=False, parent=None):
        QObject.__init__(self, parent)

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
        self.moved.emit(self.position.x, self.position.y)

    def set_heading(self, heading):
        self.heading = heading
        self.area = self.get_placement()
        self.rotated.emit(self.heading)

    def set_position(self, x, y):
        self.position.x = x
        self.position.y = y
        self.area = self.get_placement()
        self.moved.emit(self.position.x, self.position.y)

    def turn_clockwise(self):
        self.heading += 90
        self.area = self.get_placement()
        self.area = self.get_placement()
        self.rotated.emit(self.heading)

    def turn_counter_clockwise(self):
        self.heading -= 90
        self.area = self.get_placement()
        self.rotated.emit(self.heading)

    def get_placement(self):
        # Get the index of the ship
        placement = np.array([np.zeros(self.size), np.arange(0, self.size), np.ones(self.size)])
        placement = np.transpose(placement)

        # Get the kinematic matrix
        head_rad = self.heading * np.pi / 180.0
        kin_mat = np.array([[np.cos(head_rad), np.sin(head_rad), 0],
                            [-np.sin(head_rad), np.cos(head_rad), 0],
                            [self.position.x, self.position.y, 1]])

        # compute the ship placement
        placement = np.dot(placement, kin_mat)
        placement = np.delete(placement, -1, 1)
        placement = np.round(placement)
        # remove the negative 0
        placement += 0.

        #TODO: How to convert the items of placement to python type from numpy type???
        #...

        return placement.tolist()


class ShipMovementInfo:
    def __init__(self, ship_id, action=Action.NOP):
        self.ship_id = ship_id
        self.action_str = action.name

    def __repr__(self):
        return str(vars(self))

    def get_enum_action(self):
        return Action[self.action_str]


class FireInfo:
    def __init__(self, pos=Position()):
        self.pos = pos

    def __repr__(self):
        return str(vars(self))


class SatcomInfo:
    def __init__(self, a=0, b=0, c=0, d=0, e=0, f=0, is_sar=False, is_rhs=False):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e
        self.f = f
        self.is_sar = bool(is_sar)
        self.is_rhs = bool(is_rhs)

    def __repr__(self):
        return str(vars(self))


class GameConfig:
    def __init__(self,
                 num_of_players = 0,
                 num_of_rounds = 0,
                 num_of_fire_act = 0,
                 num_of_move_act = 0,
                 num_of_satc_act = 0,
                 num_of_rows = 2,
                 polling_rate = 1000,
                 map_size = Size(150, 150),
                 boundary = Boundary(),
                 en_satillite=False,
                 en_submarine=False):
        self.num_of_players = int(num_of_players)
        self.num_of_rounds = int(num_of_rounds)
        self.num_of_fire_act = int(num_of_fire_act)
        self.num_of_move_act = int(num_of_move_act)
        self.num_of_satc_act = int(num_of_satc_act)
        self.num_of_rows = int(num_of_rows)
        self.polling_rate = float(polling_rate)
        self.map_size = Size(map_size.x, map_size.y)
        self.boundary = boundary
        self.en_satillite = bool(en_satillite)
        self.en_submarine = bool(en_submarine)

    def __repr__(self):
        return str(vars(self))


class GameStatus:
    def __init__(self,
                 game_state=GameState.INIT,
                 game_round=0,
                 player_turn=0):
        self.game_state_str = game_state.name
        self.game_round = game_round
        self.player_turn = player_turn

    def __repr__(self):
        return str(vars(self))

    def get_enum_game_state(self):
        return GameState[self.game_state_str]
