import json


class UwParams:
    def __init__(self,
                 civ_sr=[8, 4, 3, 2, 1],
                 civ_br=[3, 4, 3, 4, 1],
                 mil_sr=[12, 10, 8, 7, 1],
                 mil_br=[5, 6, 7, 4, 1],
                 snr=[15, 25],
                 snr_decay=[1, 1.5],
                 snr_br=[1, 2],
                 vector_len=100,
                 p_ml=0.1):
        self.civ_sr = civ_sr
        self.civ_br = civ_br
        self.mil_sr = mil_sr
        self.mil_br = mil_br
        self.snr = snr
        self.snr_decay = snr_decay
        self.snr_br = snr_br
        self.vector_len = vector_len
        self.p_ml = p_ml

    def __repr__(self):
        return str(vars(self))


# ----------------------------------------------------------
class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        result = None
        if isinstance(obj, UwParams):
            result = {
                "__class__": "uw_params",
                "civ_sr": obj.civ_sr,
                "civ_br": obj.civ_br,
                "mil_sr": obj.mil_sr,
                "mil_br": obj.mil_br,
                "snr": obj.snr,
                "snr_decay": obj.snr_decay,
                "snr_br": obj.snr_br,
                "vector_len": obj.vector_len,
                "p_ml": obj.p_ml
            }
        else:
            print(type(obj))
            result = super().default(obj)

        return result


class JsonDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        result = None
        if '__class__' not in obj:
            result = obj
        else:
            class_type = obj['__class__']
            if class_type == 'uw_params':
                result = self.parse_uw_params(obj)
            else:
                print("Unsupported class type")
        return result

    @staticmethod
    def parse_uw_params(obj):
        return UwParams(
            obj['civ_sr'],
            obj['civ_br'],
            obj['mil_sr'],
            obj['mil_br'],
            obj['snr'],
            obj['snr_decay'],
            obj['snr_br'],
            obj['vector_len'],
            obj['p_ml']
        )
