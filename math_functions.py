from scipy.interpolate import interp1d
import math

def connect_linear(a, b, t):
    slope = (b[1] - a[1]) / (b[0] - a[0])
    res = a[1] + (t - a[0]) * slope
    return res


class LinearInterpolator(object):
    def __init__(self, point_a=None, point_b=None):
        self.point_a=point_a
        self.point_b=point_b
        self.slope = (point_b[1] - point_a[1]) / (point_b[0] - point_a[0])
        self.y_a = point_a[1]


    def __call__(self, x):
        return self.y_a + (x - self.point_a[0]) * self.slope
