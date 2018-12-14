import time
import collections


def civilian_ship_generation(civilian_ship_list, num_of_civilian_ships=0):
    if isinstance(civilian_ship_list, collections.Iterable):
        for i in range(num_of_civilian_ships):
            # todo: Generate the civilian ship data
            pass

    else:
        print("input data is not np.array type")


if __name__ == '__main__':
    print("*** %s (%s)" % (__file__, time.ctime(time.time())))
    civilian_ship_list=[]
    print(civilian_ship_list)
    civilian_ship_generation(civilian_ship_list, 10)
    print(civilian_ship_list)