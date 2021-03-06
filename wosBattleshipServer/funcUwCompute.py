import time
import numpy as np
import collections
import matplotlib.pyplot as plt
import copy

from cCommonGame import ShipType
from cCommonGame import ShipInfo
from cCommonGame import Position
from cCommonGame import UwCollectedData
from cCommonGame import UwDetectInfo
from wosBattleshipServer.uw_scan.cUwParams import UwParams


def uw_compute(uw_data, env_noise_flag=True, verbose=False):
    """
    Generate the display data based on the provided ships' information
    :param uw_data: list of UwCollectedData containing the ships' information
    :return: list of generated data in the following order
                [[north data in time domain],
                 [north-east data in time domain],
                 [east data in time domain],
                 [south-east data in time domain],
                 [south data in time domain],
                 [south-west data in time domain],
                 [west data in time domain],
                 [north-west data in time domain]]
    """
    if verbose:
        print("input uw_data:")
        if isinstance(uw_data, collections.Iterable):
            for data in uw_data:
                print(data)
        else:
            print(uw_data)

    if not uw_data:
        return list()

    uw_params = UwParams()
    outp = list()
    tmp_buf = list()

    for i in range(len(uw_data)):

        # Generate background noise
        if env_noise_flag:
            env_noise = np.random.randn(uw_params.vector_len)
        else:
            env_noise = np.zeros(uw_params.vector_len)

        ship_noise_dict = dict()

        # Check N
        sect_noise = generate_result(uw_data[i].N, ship_noise_dict, env_noise, uw_params)
        tmp_buf.append(sect_noise.tolist())

        # Check NE
        sect_noise = generate_result(uw_data[i].NE, ship_noise_dict, env_noise, uw_params)
        tmp_buf.append(sect_noise.tolist())

        # Check E
        sect_noise = generate_result(uw_data[i].E, ship_noise_dict, env_noise, uw_params)
        tmp_buf.append(sect_noise.tolist())

        # Check SE
        sect_noise = generate_result(uw_data[i].SE, ship_noise_dict, env_noise, uw_params)
        tmp_buf.append(sect_noise.tolist())

        # Check S
        sect_noise = generate_result(uw_data[i].S, ship_noise_dict, env_noise, uw_params)
        tmp_buf.append(sect_noise.tolist())

        # Check SW
        sect_noise = generate_result(uw_data[i].SW, ship_noise_dict, env_noise, uw_params)
        tmp_buf.append(sect_noise.tolist())

        # Check W
        sect_noise = generate_result(uw_data[i].W, ship_noise_dict, env_noise, uw_params)
        tmp_buf.append(sect_noise.tolist())

        # Check NW
        sect_noise = generate_result(uw_data[i].NW, ship_noise_dict, env_noise, uw_params)
        tmp_buf.append(sect_noise.tolist())

    for i in range(8):
        # Covert the data into time-domain for each direction
        data = tmp_buf[i::8]
        data = np.real(np.fft.ifft(data[:]))
        data = data.ravel()

        outp.append(data.tolist())

    if verbose:
        for tmp_buf in outp:
            print("%s" % tmp_buf)

    return outp


# def uw_compute(uw_data, env_noise=True, verbose=False):
#     """
#     Generate the display data based on the provided ships' information
#     :param uw_data: list of UwCollectedData containing the ships' information
#     :return: list of generated data in the following order
#                 [[turn 1 north data],
#                  [turn 1 north-east data],
#                  [turn 1 east data],
#                  [turn 1 south-east data],
#                  [turn 1 south data],
#                  [turn 1 south-west data],
#                  [turn 1 west data],
#                  [turn 1 north-west data],
#                  [turn 2 north data],
#                  [turn 2 north-east data],
#                  ...
#                  [turn n north-west data]]
#     """
#     if verbose:
#         print("input uw_data:")
#         if isinstance(uw_data, collections.Iterable):
#             for data in uw_data:
#                 print(data)
#         else:
#             print(uw_data)
#
#     uw_params = UwParams()
#     outp = list()
#
#     for i in range(len(uw_data)):
#
#         # Generate background noise
#         if env_noise:
#             noise = np.random.randn(uw_params.vector_len)
#         else:
#             noise = np.zeros(uw_params.vector_len)
#
#         # Check N
#         sect_noise = generate_result(uw_data[i].N, noise, uw_params)
#         outp.append(sect_noise.tolist())
#
#         # Check NE
#         sect_noise = generate_result(uw_data[i].NE, noise, uw_params)
#         outp.append(sect_noise.tolist())
#
#         # Check E
#         sect_noise = generate_result(uw_data[i].E, noise, uw_params)
#         outp.append(sect_noise.tolist())
#
#         # Check SE
#         sect_noise = generate_result(uw_data[i].SE, noise, uw_params)
#         outp.append(sect_noise.tolist())
#
#         # Check S
#         sect_noise = generate_result(uw_data[i].S, noise, uw_params)
#         outp.append(sect_noise.tolist())
#
#         # Check SW
#         sect_noise = generate_result(uw_data[i].SW, noise, uw_params)
#         outp.append(sect_noise.tolist())
#
#         # Check W
#         sect_noise = generate_result(uw_data[i].W, noise, uw_params)
#         outp.append(sect_noise.tolist())
#
#         # Check NW
#         sect_noise = generate_result(uw_data[i].NW, noise, uw_params)
#         outp.append(sect_noise.tolist())
#
#     if verbose:
#         for tmp_buf in outp:
#             print("%s" % tmp_buf)
#
#     return outp


def generate_result(ship_info_list, ship_noise_dict, env_noise, uw_params):
    """
    Generate the requested data based on the provided data
    :param ship_info_list:
    :param ship_noise_dict: dictionary containing the generated ship noise in numpy.ndarray
    :param env_noise: data representing environmental noise in numpy.ndarray
    :param uw_params: parameters for the uw operation
    :return: requested data as numpy.ndarray
    """
    sect_noise = copy.deepcopy(env_noise)
    if isinstance(ship_info_list, collections.Iterable):
        for j in range(len(ship_info_list)):
            # if isinstance(ship_info_list[j], ShipInfo):
            if isinstance(ship_info_list[j], UwDetectInfo):
                # Check type and size
                ship_type = ship_info_list[j].ship_info.ship_type
                ship_size = ship_info_list[j].ship_info.size

                # Generate ship noise if necessary
                ship_noise_ref = ship_noise_dict.get(ship_info_list[j].ship_info.ship_id)
                if ship_noise_ref is None:
                    ship_noise_ref = generate_shipnoise(ship_type, ship_size, uw_params)
                    ship_noise_dict[ship_info_list[j].ship_info.ship_id] = ship_noise_ref

                ship_noise = ship_noise_ref
                ship_noise = ship_noise / (ship_info_list[j].dist ** 2)

                # Add ship noise to background noise
                sect_noise += ship_noise
    return sect_noise


def obtain_params(ship_type, ship_size, uw_param):
    # Obtain sr and br
    if ship_type == 0:
        # Military
        sr = uw_param.mil_sr[ship_size - 1]
        br = uw_param.mil_br[ship_size - 1]
    else:
        sr = uw_param.civ_sr[ship_size - 1]
        br = uw_param.civ_br[ship_size - 1]
    return sr, br


def generate_shipnoise(ship_type, ship_size, uw_params):
    ship_noise = np.zeros(uw_params.vector_len)

    # Obtain params
    sr, br = obtain_params(ship_type, ship_size, uw_params)
    # Init shaft rate value and blade rate value
    snr = random_range(uw_params.snr)
    snr_br = snr - random_range(uw_params.snr_br)
    freq = sr
    count = 1
    count_br = 1
    # Create all lines
    while freq < uw_params.vector_len:
        if count > 1:
            if np.mod(count, br) == 0:
                # If its the blade rate
                if count_br > 1:
                    # If its the harmonic
                    snr_br = snr_br - random_range(uw_params.snr_decay)
                snr_value = snr_br
                count_br = count_br + 1
            else:
                snr = snr - random_range(uw_params.snr_decay)
                snr_value = snr
        else:
            snr_value = snr

        if np.random.rand(1) < uw_params.p_ml:
            # probability of missing lines
            snr_value = 0
        if snr_value < 0:
            break
        ship_noise[freq - 1] = snr_value
        freq = freq + sr
        count = count + 1

    return ship_noise


def random_range(in_data):
    # Produces a number that lies within the range defined by input
    outp = (in_data[1] - in_data[0]) * np.random.rand(1) + in_data[0]
    return outp


#
if __name__ == '__main__':
    print("*** %s (%s)" % (__file__, time.ctime(time.time())))

    def display_generated_uw_data(in_data, print_text=False):
        elements_per_iteration = 8
        for i in range(elements_per_iteration):
            data = in_data[i::elements_per_iteration]
            disp_data = np.array(data)

            if print_text:
                print("%s" % i)
                for print_data in data:
                    print("%s" % print_data)

            plt.subplot(4, 2, i + 1)
            if i is 0:
                plt.title("N")
            elif i is 1:
                plt.title("NE")
            elif i is 2:
                plt.title("E")
            elif i is 3:
                plt.title("SE")
            elif i is 4:
                plt.title("S")
            elif i is 5:
                plt.title("SW")
            elif i is 6:
                plt.title("W")
            elif i is 7:
                plt.title("NW")
            else:
                plt.title("???")
            plt.imshow(disp_data)
            plt.gca().invert_yaxis()
        plt.show()


    print("Test u/w ops")
    print("Sample data")
    collected_uw_data = list()
    # collected_uw_data.append(UwCollectedData(N=[ShipInfo(ship_id=0,
    #                                                      ship_type=ShipType.MIL,
    #                                                      position=Position(0, 0),
    #                                                      heading=0,
    #                                                      size=3,
    #                                                      is_sunken=False),
    #                                             ShipInfo(ship_id=1,
    #                                                      ship_type=ShipType.CIV,
    #                                                      position=Position(1, 2),
    #                                                      heading=180,
    #                                                      size=3,
    #                                                      is_sunken=False)]))
    collected_uw_data.append(UwCollectedData(N=[ShipInfo(ship_id=0,
                                                         ship_type=ShipType.MIL,
                                                         position=Position(0, 0),
                                                         heading=0,
                                                         size=3,
                                                         is_sunken=False)],
                                             S=[ShipInfo(ship_id=1,
                                                         ship_type=ShipType.CIV,
                                                         position=Position(1, 2),
                                                         heading=180,
                                                         size=3,
                                                         is_sunken=False)]))
    collected_uw_data.append(UwCollectedData(N=[ShipInfo(ship_id=0,
                                                         ship_type=ShipType.MIL,
                                                         position=Position(0, 0),
                                                         heading=0,
                                                         size=3,
                                                         is_sunken=False),
                                                ShipInfo(ship_id=1,
                                                         ship_type=ShipType.CIV,
                                                         position=Position(1, 2),
                                                         heading=180,
                                                         size=3,
                                                         is_sunken=False)],
                                             S=[ShipInfo(ship_id=0,
                                                         ship_type=ShipType.MIL,
                                                         position=Position(0, 0),
                                                         heading=0,
                                                         size=3,
                                                         is_sunken=False),
                                                ShipInfo(ship_id=1,
                                                         ship_type=ShipType.CIV,
                                                         position=Position(1, 2),
                                                         heading=180,
                                                         size=3,
                                                         is_sunken=False)]))
    collected_uw_data.append(UwCollectedData(N=[ShipInfo(ship_id=0,
                                                         ship_type=ShipType.MIL,
                                                         position=Position(0, 0),
                                                         heading=0,
                                                         size=3,
                                                         is_sunken=False),
                                                ShipInfo(ship_id=1,
                                                         ship_type=ShipType.CIV,
                                                         position=Position(1, 2),
                                                         heading=180,
                                                         size=3,
                                                         is_sunken=False)],
                                             S=[ShipInfo(ship_id=0,
                                                         ship_type=ShipType.MIL,
                                                         position=Position(0, 0),
                                                         heading=0,
                                                         size=3,
                                                         is_sunken=False),
                                                ShipInfo(ship_id=1,
                                                         ship_type=ShipType.CIV,
                                                         position=Position(1, 2),
                                                         heading=180,
                                                         size=3,
                                                         is_sunken=False)]))
    collected_uw_data.append(UwCollectedData())
    collected_uw_data.append(UwCollectedData())
    collected_uw_data.append(UwCollectedData(E=[ShipInfo(ship_id=0,
                                                         ship_type=ShipType.MIL,
                                                         position=Position(0, 0),
                                                         heading=0,
                                                         size=1,
                                                         is_sunken=False)],
                                             W=[ShipInfo(ship_id=1,
                                                         ship_type=ShipType.CIV,
                                                         position=Position(1, 2),
                                                         heading=180,
                                                         size=1,
                                                         is_sunken=False)]))
    collected_uw_data.append(UwCollectedData())
    collected_uw_data.append(UwCollectedData(NE=[ShipInfo(ship_id=0,
                                                          ship_type=ShipType.MIL,
                                                          position=Position(0, 0),
                                                          heading=0,
                                                          size=2,
                                                          is_sunken=False)],
                                             NW=[ShipInfo(ship_id=1,
                                                          ship_type=ShipType.CIV,
                                                          position=Position(1, 2),
                                                          heading=180,
                                                          size=2,
                                                          is_sunken=False)]))
    collected_uw_data.append(UwCollectedData())
    collected_uw_data.append(UwCollectedData(SE=[ShipInfo(ship_id=0,
                                                          ship_type=ShipType.MIL,
                                                          position=Position(0, 0),
                                                          heading=0,
                                                          size=4,
                                                          is_sunken=False)],
                                             SW=[ShipInfo(ship_id=1,
                                                          ship_type=ShipType.CIV,
                                                          position=Position(1, 2),
                                                          heading=180,
                                                          size=4,
                                                          is_sunken=False)]))
    collected_uw_data.append(UwCollectedData())
    collected_uw_data.append(UwCollectedData())
    collected_uw_data.append(UwCollectedData())
    collected_uw_data.append(UwCollectedData())
    collected_uw_data.append(UwCollectedData())
    collected_uw_data.append(UwCollectedData())
    collected_uw_data.append(UwCollectedData(S=[ShipInfo(ship_id=0,
                                                         ship_type=ShipType.MIL,
                                                         position=Position(0, 0),
                                                         heading=0,
                                                         size=3,
                                                         is_sunken=False),
                                                ShipInfo(ship_id=1,
                                                         ship_type=ShipType.CIV,
                                                         position=Position(1, 2),
                                                         heading=180,
                                                         size=3,
                                                         is_sunken=False)]))
    collected_uw_data.append(UwCollectedData())
    collected_uw_data.append(UwCollectedData())

    # Perform computation
    outp = uw_compute(collected_uw_data)

    if isinstance(outp, collections.Iterable):
        # Display the data as image
        display_generated_uw_data(outp)

    else:
        print("Data is not available or incorrect")

    print("*** END (%s)" % time.ctime(time.time()))
