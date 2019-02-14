import json
import numpy as np


class SatcomScanConfig:
    def __init__(self,
                 ifov_radians=np.deg2rad(1),
                 game_divisor=(6 * 60),
                 lookang_degree=20,
                 tl=[4.472, 102.00],
                 tr=[4.472, 105.00],
                 bl=[-1, 102.00],
                 br=[-1, 105.00]):
        self.ifov_radians = ifov_radians
        self.game_divisor = game_divisor
        self.lookang_degree = lookang_degree
        self.tl = tl
        self.tr = tr
        self.bl = bl
        self.br = br

    def __repr__(self):
        return str(vars(self))


#----------------------------------------------------------

class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        result = None
        if isinstance(obj, SatcomScanConfig):
            result = {
                "__class__": "satcom_scan_configuration",
                "ifov_radians": obj.ifov_radians,
                "game_divisor": obj.game_divisor,
                "lookang_degree": obj.lookang_degree,
                "tl": obj.tl,
                "tr": obj.tr,
                "bl": obj.bl,
                "br": obj.br
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
            if class_type == 'satcom_scan_configuration':
                result = self.parse_satcom_scan_configuration(obj)
            else:
                print("Unsupported class type")

        return result

    @staticmethod
    def parse_satcom_scan_configuration(obj):
        return SatcomScanConfig(
            obj['ifov_radians'],
            obj['game_divisor'],
            obj['lookang_degree'],
            obj['tl'],
            obj['tr'],
            obj['bl'],
            obj['br']
        )