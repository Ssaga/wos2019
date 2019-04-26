from client.wos import ItemType


class WosItemDepthManager(object):
    __instance = None
    __init_flag = False

    # Singleton pattern
    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(WosItemDepthManager, cls).__new__(cls, *args, **kwargs)
        return cls.__instance

    def __init__(self):
        if self.__init_flag:
            return
        self.__init_flag = True
        self.depths = dict()
        # Smaller value at background, larger value at foreground
        self.depths[ItemType.UNKNOWN] = 0
        self.depths[ItemType.TERRAIN_LAND] = 1
        self.depths[ItemType.TERRAIN_ON_HOVER] = 2
        self.depths[ItemType.SHIP] = 3
        self.depths[ItemType.TERRAIN_AIR] = 4
        self.depths[ItemType.ANNOTATION] = 5
        self.depths[ItemType.BOUNDARY] = 6

    def get_depth(self, obj):
        try:
            return self.depths.get(obj.get_type(), ItemType.UNKNOWN)
        except:
            return self.depths[ItemType.UNKNOWN]

    def get_depths_by_item(self, item_type):
        try:
            return self.depths[item_type]
        except:
            return self.depths[ItemType.UNKNOWN]

    def set_depth(self, obj):
        try:
            obj.setZValue(self.get_depth(obj))
        except:
            pass
