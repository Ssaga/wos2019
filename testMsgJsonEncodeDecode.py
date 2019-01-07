import json
import numpy as np

import cMessages
import cCommonGame

from cMessages import MsgJsonEncoder, MsgJsonDecoder
from cMessages import MsgJsonDecoder

print("Position:")
a = cCommonGame.Position(1,2)
b = MsgJsonEncoder().encode(a)
c = json.dumps(a, cls=cMessages.MsgJsonEncoder)
print("Encoder: %s" % b)
print("JSON  : %s" % c)
print("Decoder: %s" % MsgJsonDecoder().decode(b).__dict__)


print("Size:")
a = cCommonGame.Size(1,2)
b = MsgJsonEncoder().encode(a)
c = json.dumps(a, cls=cMessages.MsgJsonEncoder)
print("Encoder: %s" % b)
print("JSON  : %s" % c)
print("Decoder: %s" % MsgJsonDecoder().decode(b).__dict__)

print("Boundary:")
a = cCommonGame.Boundary(0,12,12,24)
b = MsgJsonEncoder().encode(a)
c = json.dumps(a, cls=cMessages.MsgJsonEncoder)
print("Encoder: %s" % b)
print("JSON  : %s" % c)
print("Decoder: %s" % MsgJsonDecoder().decode(b).__dict__)


print("ShipInfo:")
a = cCommonGame.ShipInfo(0, cCommonGame.Position(0,0))
b = MsgJsonEncoder().encode(a)
c = json.dumps(a, cls=cMessages.MsgJsonEncoder)
print("Encoder: %s" % b)
print("JSON  : %s" % c)
print("Decoder: %s" % MsgJsonDecoder().decode(b).__dict__)


print("ShipMovementInfo:")
a = cCommonGame.ShipMovementInfo(0, cCommonGame.Action.FWD)
b = MsgJsonEncoder().encode(a)
c = json.dumps(a, cls=cMessages.MsgJsonEncoder)
print("Encoder: %s" % b)
print("JSON  : %s" % c)
print("Decoder: %s" % MsgJsonDecoder().decode(b).__dict__)


print("FireInfo:")
a = cCommonGame.FireInfo(cCommonGame.Position(5, 6))
b = MsgJsonEncoder().encode(a)
c = json.dumps(a, cls=cMessages.MsgJsonEncoder)
print("Encoder: %s" % b)
print("JSON  : %s" % c)
print("Decoder: %s" % MsgJsonDecoder().decode(b).__dict__)


print("SatcomInfo:")
a = cCommonGame.SatcomInfo(0, cCommonGame.SatcomInfo(1,2,3,4,5,6,False,False))
b = MsgJsonEncoder().encode(a)
c = json.dumps(a, cls=cMessages.MsgJsonEncoder)
print("Encoder: %s" % b)
print("JSON  : %s" % c)
print("Decoder: %s" % MsgJsonDecoder().decode(b).__dict__)


print("GameConfig:")
num_of_players = 4
num_of_rounds = 2
num_of_fire_act = 2
num_of_move_act = 1
num_of_satc_act = 1
num_of_rows = 2
polling_rate = 500
map_size = cCommonGame.Size(12, 12)
boundary = dict()
col_count = int(np.ceil(num_of_players / num_of_rows))
row_count = num_of_rows
player_x_sz = int(map_size.x / col_count)
player_y_sz = int(map_size.y / row_count)
for i in range(num_of_players):
    x1 = int((i % col_count) * player_x_sz)
    x2 = x1 + player_x_sz
    y1 = int((i // col_count) * player_y_sz)
    y2 = y1 + player_y_sz
    boundary[i+1] = [[x1, x2], [y1, y2]]
en_satillite=True
en_submarine=False
a = cCommonGame.GameConfig(num_of_players,
                           num_of_rounds,
                           num_of_fire_act,
                           num_of_move_act,
                           num_of_satc_act,
                           num_of_rows,
                           polling_rate,
                           map_size,
                           boundary,
                           en_satillite,
                           en_submarine)
c = json.dumps(a, cls=cMessages.MsgJsonEncoder)
print("Encoder: %s" % b)
print("JSON  : %s" % c)
print("Decoder: %s" % MsgJsonDecoder().decode(b).__dict__)


print("GameStatus:")
a = cCommonGame.GameStatus(cCommonGame.GameState.PLAY_INPUT, 10, 3)
b = MsgJsonEncoder().encode(a)
c = json.dumps(a, cls=cMessages.MsgJsonEncoder)
print("Encoder: %s" % b)
print("JSON  : %s" % c)
print("Decoder: %s" % MsgJsonDecoder().decode(b).__dict__)


print("MsgReqRegisters:")
a = cMessages.MsgReqRegister(1)
b = MsgJsonEncoder().encode(a)
c = json.dumps(a, cls=cMessages.MsgJsonEncoder)
print("Encoder: %s" % b)
print("JSON  : %s" % c)
print("Decoder: %s" % MsgJsonDecoder().decode(b).__dict__)


print("MsgReqRegShips:")
a = cMessages.MsgReqRegShips(1,
                             list({cCommonGame.ShipInfo(0, cCommonGame.Position(0,0)),
                                  cCommonGame.ShipInfo(1, cCommonGame.Position(1,1))}))
b = MsgJsonEncoder().encode(a)
c = json.dumps(a, cls=cMessages.MsgJsonEncoder)
print("Encoder: %s" % b)
print("JSON  : %s" % c)
print("Decoder: %s" % MsgJsonDecoder().decode(b).__dict__)


print("MsgReqConfig:")
a = cMessages.MsgReqConfig(1)
b = MsgJsonEncoder().encode(a)
c = json.dumps(a, cls=cMessages.MsgJsonEncoder)
print("Encoder: %s" % b)
print("JSON  : %s" % c)
print("Decoder: %s" % MsgJsonDecoder().decode(b).__dict__)


print("MsgReqTurnInfo:")
a = cMessages.MsgReqTurnInfo(1)
b = MsgJsonEncoder().encode(a)
c = json.dumps(a, cls=cMessages.MsgJsonEncoder)
print("Encoder: %s" % b)
print("JSON  : %s" % c)
print("Decoder: %s" % MsgJsonDecoder().decode(b).__dict__)


print("MsgReqTurnMoveAct:")
a = cMessages.MsgReqTurnMoveAct(1,
                             list({
                                 cCommonGame.ShipMovementInfo(1, cCommonGame.Action.FWD),
                                 cCommonGame.ShipMovementInfo(2, cCommonGame.Action.CW),
                                 cCommonGame.ShipMovementInfo(3, cCommonGame.Action.CCW)
                             }))
b = MsgJsonEncoder().encode(a)
c = json.dumps(a, cls=cMessages.MsgJsonEncoder)
print("Encoder: %s" % b)
print("JSON  : %s" % c)
print("Decoder: %s" % MsgJsonDecoder().decode(b).__dict__)


print("MsgReqTurnFireAct:")
a = cMessages.MsgReqTurnFireAct(1,
                             list({
                                 cCommonGame.FireInfo(
                                     cCommonGame.Position(1,2)),
                                 cCommonGame.FireInfo(
                                     cCommonGame.Position(3, 4)),
                                 cCommonGame.FireInfo(
                                     cCommonGame.Position(5, 6))
                             }))
b = MsgJsonEncoder().encode(a)
c = json.dumps(a, cls=cMessages.MsgJsonEncoder)
print("Encoder: %s" % b)
print("JSON  : %s" % c)
print("Decoder: %s" % MsgJsonDecoder().decode(b).__dict__)


print("MsgReqTurnSatAct:")
a = cMessages.MsgReqTurnSatAct(1, cCommonGame.SatcomInfo(1,2,3,4,5,6,False,False))
b = MsgJsonEncoder().encode(a)
c = json.dumps(a, cls=cMessages.MsgJsonEncoder)
print("Encoder: %s" % b)
print("JSON  : %s" % c)
print("Decoder: %s" % MsgJsonDecoder().decode(b).__dict__)


print("MsgRepAck:")
a = cMessages.MsgRepAck(True)
b = MsgJsonEncoder().encode(a)
c = json.dumps(a, cls=cMessages.MsgJsonEncoder)
print("Encoder: %s" % b)
print("JSON  : %s" % c)
print("Decoder: %s" % MsgJsonDecoder().decode(b).__dict__)


print("MsgRepAckMap:")
a = cMessages.MsgRepAckMap(True, [[1,1,1,1],[1,1,1,0],[1,1,0,0],[1,0,0,0]])
b = MsgJsonEncoder().encode(a)
c = json.dumps(a, cls=cMessages.MsgJsonEncoder)
print("Encoder: %s" % b)
print("JSON  : %s" % c)
print("Decoder: %s" % MsgJsonDecoder().decode(b).__dict__)



print("MsgRepGameConfig:")
a = cMessages.MsgRepGameConfig(True, cCommonGame.GameConfig())
b = MsgJsonEncoder().encode(a)
c = json.dumps(a, cls=cMessages.MsgJsonEncoder)
print("Encoder: %s" % b)
print("JSON  : %s" % c)
print("Decoder: %s" % MsgJsonDecoder().decode(b).__dict__)



print("MsgRepTurnInfo:")
a = cMessages.MsgRepTurnInfo(True,
                             list({
                                 cCommonGame.ShipInfo(1, cCommonGame.Position(1, 1), 0, 1, False),
                                 cCommonGame.ShipInfo(2, cCommonGame.Position(2, 2), 90, 2, False),
                                 cCommonGame.ShipInfo(3, cCommonGame.Position(2, 2), 180, 2, False)
                             }),
                             list({
                                 cCommonGame.Position(1, 1),
                                 cCommonGame.Position(2, 2),
                                 cCommonGame.Position(3, 3)

                             }),
                             [[1,1,1,1],[1,1,1,0],[1,1,0,0],[1,0,0,0]]
                             )
b = MsgJsonEncoder().encode(a)
c = json.dumps(a, cls=cMessages.MsgJsonEncoder)
print("Encoder: %s" % b)
print("JSON  : %s" % c)
print("Decoder: %s" % MsgJsonDecoder().decode(b).__dict__)
