from scipy.interpolate import interp1d
import math

# get the value at position t between a[0] and b[0]
# using linear interpolation.
# a and b are array-like.
# t is float.
# def connect_linear(a, b, t):
#     x = [a[0], b[0]]
#     y = [a[1], b[1]]
#     f = interp1d(x, y, kind='linear')
#     value = f(t)
#     return value


def connect_linear(a, b, t):
    steigung = (b[1] - a[1]) / (b[0] - a[0])
    value = a[1] + (t-a[0]) * steigung
    # print(steigung, value, t)
    return value


class LinearConnector(object):
    def __init__(self, point_a=None, point_b=None):
        self.point_a=point_a
        self.point_b=point_b
        self.slope = (point_b[1] - point_a[1]) / (point_b[0] - point_a[0])
        self.y_a = point_a[1]


    def __call__(self, x):
        return self.y_a + (x - self.point_a[0]) * self.slope
