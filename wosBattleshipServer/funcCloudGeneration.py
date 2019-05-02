import numpy as np


class CloudGrid:
    def __init__(self, shape: '(Height, width)',
                 coverage: 'Max and min percentage (between 0 and 1)' = (0.5, 0.1),
                 seed: 'Seed for the random number generator' = None):
        self.shape = shape
        self.max_cov, self.min_cov = coverage
        self.coverage_longterm = 0.5 * (self.max_cov + self.min_cov)
        self.coverage_instant = self.coverage_longterm
        self.coverage_momentum = np.random.normal(scale=0.1)
    #     self.initiate(seed)
    #
    # def initiate(self, seed=None):
        np.random.seed(seed)
        self.grid = np.zeros(self.shape, dtype=np.bool)
        num_seeds = int(max(1,
                            np.random.uniform(0.8, 1.2) * \
                            np.product(self.shape) * self.coverage_instant / 60))
        for i in range(num_seeds):
            self.grid[np.random.randint(self.shape[0]),
                      np.random.randint(self.shape[1])] = 1
        self.step(erode=False)

    def count_neighbors(self, edge_value=0.1):
        implied_weight = np.ones(np.array(self.shape) + 2) * edge_value
        implied_weight[1:-1, 1:-1] = self.grid
        neighbors = np.zeros(self.shape)
        for y in range(self.shape[0]):
            for x in range(self.shape[1]):
                neighbors[y, x] = np.sum(implied_weight[y:y + 3, x:x + 3])
        return neighbors

    def update_coverage(self):
        self.coverage_instant += self.coverage_momentum
        self.coverage_momentum *= np.random.uniform(0.9, 1.1)
        self.coverage_momentum += (self.coverage_longterm - self.coverage_instant) * .05
        self.coverage_instant = max(min(self.coverage_instant, self.max_cov), self.min_cov)

    def erode_clouds(self, end_goal, base_rate=1, edge_value=0.01):
        while np.mean(self.grid) > end_goal:
            neighbors = self.count_neighbors(edge_value=edge_value) + base_rate
            self.grid *= np.random.uniform(size=self.shape) > (1 / (neighbors + 1))

    def step(self, base_rate=.999, edge_value=0.001, erode=True, first_pass=True):
        self.update_coverage()
        if erode:
            self.erode_clouds(end_goal=self.coverage_instant * 0.9)
        while np.mean(self.grid) < self.coverage_instant or first_pass:
            neighbors = self.count_neighbors(edge_value=edge_value) * .1 + 1
            thresh = base_rate
            self.grid[np.where(np.random.uniform(high=neighbors) > thresh)] = True
            first_pass = False
        print(self.coverage_instant, np.mean(self.grid))


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    c = CloudGrid((30, 30))
    plt.imshow(c.grid)
    for _ in range(100):
        plt.imshow(c.grid)
        c.step()
        plt.pause(.3)

# import time
# import numpy as np
# import scipy.signal
# import copy
#
#
# def cloud_generation(map_data, cloud_coverage, cloud_seed_num=1):
#     if isinstance(map_data, np.ndarray):
#         # Get the size of the map_date
#         (x_len, y_len) = np.shape(map_data)
#         map_size = np.size(map_data)
#         cloud_coverage = np.minimum(cloud_coverage, 1.0)
#
#         if cloud_coverage == 0:
#             cloud_seed_num = 0
#             cloud_sz = 0
#         else:
#             cloud_sz = int(np.floor(map_size * cloud_coverage))
#
#         if cloud_seed_num > 0:
#             # Generate the seed position
#             seed_pos = np.array([np.random.randint(x_len, size=cloud_seed_num),
#                             np.random.randint(y_len, size=cloud_seed_num)]).T
#             # Generate the cloud
#             generate_cloud(map_data, seed_pos, cloud_sz)
#         else:
#             print("It is a clear blue sky...")
#     else:
#         print("input data is not np.array type")
#
#
# def cloud_change(map_data, cloud_coverage):
#     if isinstance(map_data, np.ndarray):
#         adj_def = [[0, 1, 0], [1, 0, 1], [0, 1, 0]]
#         # Get the size of the map_date
#         (x_len, y_len) = np.shape(map_data)
#         map_size = np.size(map_data)
#         cloud_coverage = np.minimum(cloud_coverage, 1.0)
#         cloud_sz = int(np.floor(map_size * cloud_coverage))
#
#         tmp_buf = copy.deepcopy(map_data)
#
#         for _ in range(4):
#             tmp_buf = np.multiply(np.minimum(2 * np.random.rand(x_len, y_len), 1).astype(np.int),
#                                   np.multiply(
#                                       np.greater(scipy.signal.convolve2d(tmp_buf, adj_def, 'same', fillvalue=1), 0),
#                                       np.subtract(1, tmp_buf))) + tmp_buf
#             while np.sum(tmp_buf) > cloud_sz:
#                 disap_grid = np.minimum(np.random.rand(x_len, y_len) / .95, 1).astype(np.int)
#                 tmp_buf = np.multiply(1 * np.greater(scipy.signal.convolve2d(tmp_buf, adj_def, 'same', fillvalue=1), 3),
#                                       1 - disap_grid) + np.multiply(tmp_buf, disap_grid)
#
#             while np.sum(tmp_buf) < cloud_sz:
#                 tmp_buf = np.multiply((2 * np.random.rand(x_len, y_len)).astype(np.int16),
#                                       np.multiply(np.greater(scipy.signal.convolve2d(tmp_buf, adj_def, 'same'), 0),
#                                                   np.subtract(1, tmp_buf))) + tmp_buf
#         map_data[:,:] = 0
#         map_data[np.where(tmp_buf > 0)] = 1
#         print("cld_grid: %s\r\n%s" % (tmp_buf.shape, tmp_buf.T))
#         print("num of  : %s/%s" % (np.sum(tmp_buf), cloud_sz))
#
#     else:
#         print("input data is not np.array type")
#
#
# # The following code is based on the old WOS island generating
# def generate_cloud(map_data, seed_pos, cloud_sz):
#     if isinstance(seed_pos, np.ndarray):
#         adj_def = [[0, 1, 0], [1, 0, 1], [0, 1, 0]]
#         num_cloud_seeds = len(seed_pos)
#         (x_len, y_len) = np.shape(map_data)
#
#         tmp_buf = np.zeros((x_len, y_len), dtype=np.int)
#         for i in range(num_cloud_seeds):
#             tmp_buf[tuple(seed_pos[i])] = 1
#
#         while np.sum(tmp_buf) < cloud_sz:
#             tmp_buf = np.multiply((2 * np.random.rand(x_len, y_len)).astype(np.int16),
#                                 np.multiply(np.greater(scipy.signal.convolve2d(tmp_buf, adj_def, 'same'), 0),
#                                             np.subtract(1, tmp_buf))) + tmp_buf
#         map_data[np.where(tmp_buf > 0 )] = 1
#         print("cld_grid: %s\r\n%s" % (tmp_buf.shape, tmp_buf))
#         print("num of  : %s/%s" % (np.sum(tmp_buf), cloud_sz))
#     else:
#         raise ValueError("Invalid input parameters")
#
#
# if __name__ == '__main__':
#     print("*** %s (%s)" % (__file__, time.ctime(time.time())))
#     print("Test generate_cloud")
#     board_size = np.array([20, 20])
#     board = np.zeros(board_size.tolist())
#     pos = np.array([np.random.randint(20, size=10),np.random.randint(20, size=10)]).T
#     coverage = board.size * 0.5
#     generate_cloud(board, pos, coverage)
#
#     print("Test cloud_generation")
#     x_len = 24
#     y_len = 24
#     map_data = np.zeros((x_len, y_len), dtype=np.int)
#     print("*** map_data:\r\n%s" % map_data)
#     cloud_generation(map_data, 0.5, 10)
#     print("*** map_data:\r\n%s" % map_data)
#
#     print("Test cloud_change")
#     print("*** map_data:\r\n%s" % map_data)
#     cloud_change(map_data, 0.5)
#     print("*** map_data:\r\n%s" % map_data)
#     cloud_change(map_data, 0.5)
#     print("*** map_data:\r\n%s" % map_data)
#     cloud_change(map_data, 0.5)
#     print("*** map_data:\r\n%s" % map_data)
#     print("*** END (%s)" % (time.ctime(time.time())))
