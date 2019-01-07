import time
import numpy as np
import scipy.signal
from enum import IntEnum


class CellState(IntEnum):
    EMPTY = 0
    BLOCK = 1


def island_generation(map_data, island_coverage):
    if isinstance(map_data, np.ndarray):
        # Get the size of the map_date
        (x_len, y_len) = np.shape(map_data)
        map_size = np.size(map_data)
        island_coverage = np.minimum(island_coverage, 1.0)

        num_of_spot = max(1, np.random.randint(5))

        # Get the list of seed position
        position = np.array([np.random.randint(x_len, size=num_of_spot),
                             np.random.randint(y_len, size=num_of_spot)])
        position = position.T
        # position = list();
        # for _ in range(num_of_spot):
        #     position.append((np.random.randint(x_len),
        #                      np.random.randint(y_len)))

        island_sz = int(np.floor(map_size * island_coverage / num_of_spot))

        print("--------------------")
        print("ISLAND: NUM : %s" % num_of_spot)
        print("ISLAND: SIZE: %s" % island_sz)
        print("ISLAND: SPOT: \r\n%s" % position)

        # Generate the island
        if island_sz > 0:
            for pos in position:
                generate_island(map_data, tuple(pos), island_sz)

    else:
        print("input data is not np.array type")


# The following code is based on the old WOS island generating
def generate_island(board, seed_pos, island_size):
    adj_def = [[0, 1, 0], [1, 0, 1], [0, 1, 0]]
    if (isinstance(board, np.ndarray) and
            isinstance(seed_pos, tuple) and
            isinstance(island_size, int)):
        all_pos = [seed_pos]
        side_size = island_size * 2 + 1
        board_size = board.shape
        valid_grid = np.zeros([i + island_size * 2 for i in board_size])
        valid_grid[island_size:-island_size, island_size:-island_size] = np.equal(board, CellState.EMPTY)
        valid_grid = valid_grid[seed_pos[0]:seed_pos[0] + side_size, seed_pos[1]:seed_pos[1] + side_size]
        rel_pos_grid = np.zeros((side_size, side_size))
        rel_pos_grid[island_size, island_size] = 1

        # Get the list of position for the island
        for _ in range(island_size - 1):
            adj_grid = np.multiply(
                np.greater(scipy.signal.convolve2d(rel_pos_grid, adj_def, 'same'), 0),
                np.subtract(1, rel_pos_grid))
            valid_and_adj_grid = np.multiply(adj_grid, valid_grid)
            poss_pos = [(i, j) for i in range(side_size) for j in range(side_size) if valid_and_adj_grid[i, j] == 1]
            rel_pos = poss_pos[np.random.randint(len(poss_pos))]
            rel_pos_grid[rel_pos] = 1
            all_pos += [tuple(map(sum, zip(*[seed_pos, [i - island_size for i in rel_pos]])))]

        # Update the board
        for pos in all_pos:
            print(pos)
            board[pos] = CellState.BLOCK

        print("*** %s\r\n%s" % (type(rel_pos_grid), rel_pos_grid))
        print("*** %s\r\n%s" % (type(all_pos), all_pos))
        print("*** %s\r\n%s" % (type(board), board))
    else:
        raise ValueError("Invalid input parameters")


if __name__ == '__main__':
    print("*** %s (%s)" % (__file__, time.ctime(time.time())))
    print("Test generate_island")
    board_size = np.array([20, 20])
    board = np.zeros(board_size.tolist())
    pos = tuple(np.divide(board_size, 2).astype(int).tolist())
    pos = (19, 19)
    generate_island(board, pos, 10)

    print("Test island_generation")
    x_len = 24
    y_len = 24
    map_data=np.zeros((x_len,y_len))
    print("*** map_data:\r\n%s" % map_data)
    island_generation(map_data[0:12, 0:12], 0.1)
    island_generation(map_data[0:12, 12:23], 0.1)
    island_generation(map_data[12:23, 0:12], 0.1)
    island_generation(map_data[12:23, 12:23], 0.1)
    print("*** map_data:\r\n%s" % map_data)
    print("*** END (%s)" % (time.ctime(time.time())))
