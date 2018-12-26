import time
import numpy as np
import scipy


def island_generation(map_data, island_coverage):
    if isinstance(map_data, np.ndarray):
        # Get the size of the map_date
        (x, y) = np.shape(map_data)
        map_size = np.size(map_data)
        island_coverage = np.minimum(island_coverage, 1.0)
        island_sz = int(np.floor(map_size * island_coverage))

        # Generate the island
        # todo: integrate existing island generation logic
        #       the following is just for testing to see
        #       data is being passed back
        b= np.array([], dtype=int)
        b = np.append(b, np.random.randint(0, x, island_sz))
        b = np.append(b, np.random.randint(0, y, island_sz))
        bb = np.reshape(b, (2, -1))
        bb = np.transpose(bb)
        print("index: [%s]\r\n%s" % (__file__, bb))
        for c in bb:
            map_data[c[1]][c[0]] = 1

    else:
        print("input data is not np.array type")


if __name__ == '__main__':
    print("*** %s (%s)" % (__file__, time.ctime(time.time())))
    map_data=np.zeros((15,15))
    print(map_data)
    island_generation(map_data, 0.1)
    print(map_data)