# from enum import Enum
from enum import IntEnum
import numpy as np
import collections


class MapData(IntEnum):
    WATER = 0                   # Sea / Uncovered
    ISLAND = 1
    CLOUD_FRIENDLY = 2          # Cloud in friendly area
    CLOUD_HOSTILE = 4           # Cloud in hostile area
    BLACK = 64                  # Disable Color
    FOG_OF_WAR = 128


class ShipType(IntEnum):
    MIL = 0
    CIV = 1


class Action(IntEnum):
    NOP = 0
    FWD = 1
    CW = 2
    CCW = 3


class GameState(IntEnum):
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


# class ShipInfo(QObject):
#     moved = pyqtSignal(int, int)
#     rotated = pyqtSignal(float)
class ShipInfo:
    def __init__(self,
                 ship_id=0,
                 position=Position(0, 0),
                 heading=0,
                 size=0,
                 is_sunken=False,
                 ship_type=ShipType.MIL,
                 player_id=-1):
        self.ship_id = ship_id
        self.ship_type = ship_type
        # Position of of the ship head
        self.position = position
        self.heading = heading
        self.size = size
        self.is_sunken = is_sunken
        self.player_id = player_id
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

    def set_heading(self, heading):
        self.heading = heading
        self.area = self.get_placement()

    def set_position(self, x, y):
        self.position.x = x
        self.position.y = y
        self.area = self.get_placement()

    def turn_clockwise(self):
        self.heading += 90
        self.heading = self.wrap(self.heading)
        self.area = self.get_placement()

    def turn_counter_clockwise(self):
        self.heading -= 90
        self.heading = self.wrap(self.heading)
        self.area = self.get_placement()

    def get_placement(self):
        # get the upper half size of the ship
        half_size = (self.size - 1) // 2

        # Get the index of the ship
        placement = np.array([np.zeros(self.size),
                              np.arange(-half_size, (self.size - half_size)),
                              np.ones(self.size)])
        placement = np.transpose(placement)

        # Get the kinematic matrix
        head_rad = self.heading * np.pi / 180.0
        kin_mat = np.array([[np.cos(head_rad),  np.sin(head_rad),   0],
                            [-np.sin(head_rad), np.cos(head_rad),   0],
                            [self.position.x,   self.position.y,    1]])

        # compute the ship placement
        placement = np.dot(placement, kin_mat)

        # remove the last column
        placement = np.delete(placement, -1, 1)

        placement = np.round(placement)
        # remove the negative 0
        placement += 0.
        placement = placement.astype(int)

        return placement.tolist()

    @staticmethod
    def wrap(degree):
        result = ((degree + 180.0) % 360) - 180.0
        return result


class UwShipInfo:
    def __init__(self,
                 ship_id=0,
                 position=Position(0, 0),
                 size=1,
                 is_sunken=False,
                 ship_type=ShipType.MIL):
        self.ship_id = ship_id
        self.ship_type = ship_type
        # Position of of the ship head
        self.position = position
        self.size = size
        self.is_sunken = is_sunken
        # list of position occupied by the vehicle
        # first position is the bow of the ship
        self.area = position

    def __repr__(self):
        return str(vars(self))

    def set_position(self, pos=Position(0, 0)):
        self.set_position(pos.x, pos.y)

    def set_position(self, x, y):
        self.position.x = x
        self.position.y = y
        self.area.x = x
        self.area.y = y

    def get_placement(self):
        return [[self.position.x, self.position.y]]


class UwDetectInfo:
    def __init__(self, ship_info, dist):
        self.ship_info = ship_info
        self.dist = dist


class ShipMovementInfo:
    def __init__(self, ship_id, action=Action.NOP):
        self.ship_id = ship_id
        self.action_str = action.name

    def __repr__(self):
        return str(vars(self))

    def get_enum_action(self):
        return Action[self.action_str]

    def to_string(self):
        if self.action_str == Action.NOP:
            return "Hold movement for ship id %s" % self.ship_id
        else:
            return "Move ship (Id: %s) %s" % (self.ship_id, self.action_str)


class UwShipMovementInfo:
    def __init__(self, ship_id, actions=[]):
        self.ship_id = ship_id
        is_ok = True
        if isinstance(actions, collections.Iterable):
            for uw_action in actions:
                if isinstance(uw_action, UwAction) is False:
                    is_ok = False
        else:
            is_ok = False

        self.uw_actions = list()
        if is_ok:
            self.uw_actions.extend(actions)

    def __repr__(self):
        return str(vars(self))


class FireInfo:
    def __init__(self, pos=Position()):
        self.pos = pos

    def __repr__(self):
        return str(vars(self))

    def to_string(self):
        return "Fire position: (%s, %s)" % (self.pos.x, self.pos.y)


class SatcomInfo:
    def __init__(self, a=0, e=0, i=0, om=0, Om=0, M=0, is_enable=False, is_rhs=False):
        self.a = a
        self.e = e
        self.i = i
        self.om = om
        self.Om = Om
        self.M = M
        self.is_enable = bool(is_enable)
        self.is_rhs = bool(is_rhs)

    def __repr__(self):
        return str(vars(self))


# Created by ttl on 2019-02-23
class UwAction:
    def __init__(self):
        # Do nothing
        pass


# class to represent the move and scan action
class UwActionMoveScan(UwAction):
    def __init__(self, goto_pos=None, scan_dur=0):
        """
        :param goto_pos: Position of the destination / None
        :param scan_dur: Duration of the scan operation. Unit in number of turns
        """
        self.goto_pos = goto_pos
        self.scan_dur = scan_dur

    def __repr__(self):
        return str(vars(self))


# # class to represent scan only action
# class UwActionScan(UwAction):
#     def __init__(self, scan_dur):
#         self.scan_dur = scan_dur
#
#     def __repr__(self):
#         return str(vars(self))
#
#
# #
# class UwActionNop(UwAction):
#     def __init__(self):
#         # Do nothing
#         pass
#
#     def __repr__(self):
#         return str(vars(self))


class UwCollectedData:
    def __init__(self, N=[], NE=[], E=[], SE=[], S=[], SW=[], W=[], NW=[]):
        self.N = N
        self.NE = NE
        self.E = E
        self.SE = SE
        self.S = S
        self.SW = SW
        self.W = W
        self.NW = NW

    def __repr__(self):
        return str(vars(self))


# #
# class UwReport:
#     def __init__(self):
#         pass


class GameConfig:
    def __init__(self,
                 num_of_players=0,
                 num_of_rounds=0,
                 num_of_fire_act=0,
                 num_of_move_act=0,
                 num_of_satc_act=0,
                 num_of_rows=2,
                 polling_rate=1000,
                 map_size=Size(150, 150),
                 boundary=dict(),
                 en_satellite=False,
                 en_satellite_func2=False,
                 en_submarine=False):

        if not isinstance(boundary, dict) or not isinstance(map_size, Size):
            raise ValueError("Invalid input parameter")

        self.num_of_players = int(num_of_players)
        self.num_of_rounds = int(num_of_rounds)
        self.num_of_fire_act = int(num_of_fire_act)
        self.num_of_move_act = int(num_of_move_act)
        self.num_of_satc_act = int(num_of_satc_act)
        self.num_of_rows = int(num_of_rows)
        self.polling_rate = float(polling_rate)
        self.map_size = Size(map_size.x, map_size.y)
        self.boundary = boundary
        self.en_satellite = bool(en_satellite)
        self.en_satellite_func2 = bool(en_satellite_func2)
        self.en_submarine = bool(en_submarine)

    def __repr__(self):
        return str(vars(self))


class GameStatus:
    def __init__(self,
                 game_state=GameState.INIT,
                 game_round=0,
                 player_turn=0,
                 time_remain=0):
        self.game_state_str = game_state.name
        self.game_round = game_round
        self.player_turn = player_turn          # Not used; Removed due to remove of turn-based gameplay
        self.time_remain = time_remain

    def __repr__(self):
        return str(vars(self))

    def get_enum_game_state(self):
        return GameState[self.game_state_str]


class LogType(IntEnum):
    GAME = 1
    DEBUG = 2
    ALL = 3
