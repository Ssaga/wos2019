from client.scene_item.battleship_item import WosBattleShipItem


class WosBattleUtil:

    @staticmethod
    def insert_ship_to_scene(battle_scene, ship_info, ship_type):
        scene = battle_scene.scene()
        field_info = battle_scene.get_field_info()
        ship_item = WosBattleShipItem(field_info, None, ship_info.ship_id, ship_info.size, ship_info.is_sunken)
        ship_item.set_grid_position(ship_info.position.x, ship_info.position.y)
        ship_item.set_heading(ship_info.heading)
        ship_item.set_ship_type(ship_type)
        ship_item.set_is_draggable(False)
        scene.addItem(ship_item)
        return ship_item

    @staticmethod
    def is_in_boundary(self, grid_x, grid_y, min_x, max_x, min_y, max_y):
        return min_x <= grid_x <= max_x and min_y <= grid_y <= max_y