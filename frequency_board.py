import math
import numpy as np

class FrequencyBoard:
    def __init__(self, size_x, size_y, filename, transition_size):
        self.size_x = size_x
        self.size_y = size_y
        self.filename = filename
        self.transition_size = transition_size
        self.row_frequencies = None
        self.frequencies = np.zeros((size_y, size_x))
        self.colors = np.ones((size_y, size_x, 3), dtype=np.uint8) \
                      * np.ones((size_y, size_x, 1), dtype=np.uint8)

        self.load_file(self.filename)
        self.calculate_frequencies_of_pixels()
        self.calculate_colors()




    def calculate_colors(self):
        for ix in range(self.size_x):
            for iy in range(self.size_y):
                x_normalized = float(ix) / self.size_x
                y_normalized = float(iy) / self.size_y
                color_factor = self.get_color_factor_normalized(x_normalized, y_normalized)
                color_start = [255,51,51]
                color_end = [204,153,255]
                mixed_color = [color_factor * color_start[i] \
                              + (1.0 - color_factor) * color_end[i] \
                              for i in range(len(color_start))]
                self.colors[iy][ix] = mixed_color

        # create lines
        line_color = [255,255,255]
        no_of_rows = len(self.row_frequencies)
        dy = int(round(self.size_y / float(no_of_rows)))
        for i in range(1,no_of_rows):
            for ix in range(self.size_x):
                line_y = i * dy
                for iy in range(line_y, line_y + 3):
                    self.colors[iy][ix] = line_color


        # import cv2
        # cv2.imshow("test", self.colors)
        # cv2.waitKey(5555)


    def calculate_frequencies_of_pixels(self):
        """
        Calculate the values of the array self.frequencies.
        We precalculate the values to save time.
        """
        for ix in range(self.size_x):
            for iy in range(self.size_y):
                x_normalized = float(ix) / self.size_x
                y_normalized = float(iy) / self.size_y
                frequency = self.get_frequency_normalized(x_normalized, y_normalized)
                self.frequencies[iy][ix] = frequency

    def load_file(self, filename):
        frequencies = []
        with open(filename) as infile:
            lines = infile.read().split("\n")
            for line in lines:
                if line != "":
                    value_strings = line.split(" ")
                    values = []
                    for s in value_strings:
                        factors = s.split("*")
                        factors = [float(f) for f in factors]
                        freq = factors[0]
                        for f in factors[1:]:
                            freq *= f
                        values.append(freq)
                    frequencies.append(values)
        self.row_frequencies = frequencies


    def get_color_factor_normalized(self, x, y):
        """
        Returns the color factor on a normalized board, where
        x, y must be between 0 and 1.
        The color factor is a value between 0 and 1. It will later
        be used to produce color gradients between adjacent pitch centers.
        """
        index_start, index_end, frequency_centers, row_no = self.get_position_info(x, y)
        if x < frequency_centers[0]:
            res_factor = 1.0
        elif x > frequency_centers[-1]:
            res_factor = 1.0
        elif index_start != index_end:
            x_start = frequency_centers[index_start]
            x_end = frequency_centers[index_end]
            factor = get_transition_factor(x, x_start, x_end, self.transition_size)
            if factor < 0.5:
                res_factor = 1.0 - 2.0 * factor
            else:
                res_factor = (factor - 0.5) * 2.0
        else:
            # It may happen that index_start = index_end holds.
            # I guess its a problem with rounding.
            res_factor = 1.0
        return res_factor


    def get_frequency_normalized(self, x, y):
        """
        Returns the frequency on a normalized board, where
        x, y must be between 0 and 1.
        """
        index_start, index_end, frequency_centers, row_no = self.get_position_info(x, y)
        if x < frequency_centers[0]:
            res_frequency = self.row_frequencies[row_no][0]
        elif x > frequency_centers[-1]:
            res_frequency = self.row_frequencies[row_no][-1]
        elif index_start != index_end:
            x_start = frequency_centers[index_start]
            x_end = frequency_centers[index_end]
            factor = get_transition_factor(x, x_start, x_end, self.transition_size)
            frequency_start = self.row_frequencies[row_no][index_start]
            frequency_end = self.row_frequencies[row_no][index_end]
            log_start = math.log(frequency_start)
            log_end = math.log(frequency_end)
            log_middle = log_start + factor * (log_end - log_start)
            res_frequency = math.exp(log_middle)
        else:
            # It may happen that index_start = index_end holds.
            # I guess its a problem with rounding.
            res_frequency = self.row_frequencies[row_no][index_start]
        return res_frequency


    def get_position_info(self, x, y):
        no_of_rows = len(self.row_frequencies)
        dy = 1.0 / float(no_of_rows)
        row_no = min(int(y / dy), len(self.row_frequencies) - 1)
        no_of_frequencies = len(self.row_frequencies[row_no])
        dx = 1.0 / float(no_of_frequencies)
        frequency_centers = [i * dx + 0.5 * dx for i in range(no_of_frequencies)]
        index_start = int( (x - frequency_centers[0]) / dx )
        index_end = min(int( (x + frequency_centers[0]) / dx ), no_of_frequencies - 1)
        return index_start, index_end, frequency_centers, row_no

def get_transition_factor(x, x_start, x_end, transition_size):
    """
    transition_size between 0 (no transition) and
    1 (uses the complete space)
    """
    delta_x = x_end - x_start
    delta_transition = transition_size * 0.5 * delta_x
    if x < x_start + delta_transition:
        return 0.0
    elif x > x_end - delta_transition:
        return 1.0
    else:
        full_transition_length = delta_x - 2.0 * delta_transition
        diff = x - (x_start + delta_transition)
        factor = diff / full_transition_length
        return factor
