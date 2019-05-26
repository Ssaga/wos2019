import json


class TtsMsg1:
    def __init__(self, player_id, msg_str):
        self.player_id = player_id
        self.msg_str = msg_str

    def __repr__(self):
        return str(vars(self))

# ----------------------------------------------------------


class MsgJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        result = None
        if isinstance(obj, TtsMsg1):
            result = {
                "__class__": "ttsMsg1",
                "player_id": obj.player_id,
                "msg_str": obj.msg_str
            }

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
            if class_type == 'ttsMsg1':
                result = self.parse_tts_msg_1(obj)
            else:
                print("Unsupported class type")

        return result

    @staticmethod
    def parse_tts_msg_1(obj):
        return TtsMsg1(
            player_id=obj['player_id'],
            msg_str=obj['msg_str']
        )
