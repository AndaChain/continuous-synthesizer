import math

def triangle(phase):
    if phase < 0.5:
        return 1.0 - phase * 4.0
    else:
        return -1.0 + (phase - 0.5) * 4.0

def square(phase):
    if phase < 0.5:
        return 1.0
    else:
        return -1.0

class Oscillator:
    def __init__(self, waveform="sine", dt=None, frequency=100.0):
        self.waveform = waveform
        self.dt = dt
        self.phase = 0.0
        self.frequency = frequency
        self.osc_function = None
        self.init_osc_function()

    def init_osc_function(self):
        if self.waveform == "sine":
            self.osc_function = lambda x : math.sin(2.0 * math.pi * x)
        elif self.waveform == "triangle":
            self.osc_function = triangle
        elif self.waveform == "square":
            self.osc_function = square

    def step(self):
        """
        Increment the phase.
        Phase will remain between 0 and 1.
        """
        self.phase += self.frequency * self.dt
        self.phase = self.phase % 1.0

    def get(self):
        value = self.osc_function(self.phase)
        return value







def main():
    o = Oscillator()

if __name__ == '__main__':
    main()
