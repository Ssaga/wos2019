import time
import collections
import numpy as np

from wosBattleshipServer.cCommon import ShipInfo
from cCommonGame import Position

def civilian_ship_movement(civilian_ship_list, move_possibility=0.25):
	if isinstance(civilian_ship_list, collections.Iterable):
		for ship_info in civilian_ship_list:
			if isinstance(ship_info, ShipInfo) and (not ship_info.is_sunken):
				# todo: Generate the civilian ship data
				pass
			# else do nothing as the ship has sunk
		# end of for..loop for the list of civilian ships
	else:
		print("input data is not np.array type")


if __name__ == '__main__':
	print("*** %s (%s)" % (__file__, time.ctime(time.time())))
	civilian_ship_list=[]
	for i in range(10):
		head = np.random.random_integers(0, 4) * 90
		size = np.random.random_integers(2, 5)
		pos = Position(np.random.random_integers(0, 20), np.random.random_integers(0, 20))
		ship = ShipInfo(i, pos, head, 3)
		civilian_ship_list.append(ship)

	print([vars(ship) for ship in civilian_ship_list])
	civilian_ship_movement(civilian_ship_list, 1)
	print([vars(ship) for ship in civilian_ship_list])
