import json

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
a = cCommonGame.GameConfig(0, cCommonGame.Action.FWD)
b = MsgJsonEncoder().encode(a)
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
a = cMessages.MsgRepGameConfig(True, cCommonGame.GameConfig(5, True, True))
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
