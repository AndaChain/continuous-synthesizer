from math_functions import LinearConnector

# A class for an envelope generator.


class Envelope(object):
    def __init__(
            self,
            attack_time=0.01,
            decay_time=0.11,
            release_time=1.1,
            dt=1.0 / 44100.0,
            after_decay_level=0.2,
            start_level=0.0,
            attack_level=1.0,
            after_release_level=0.0):
        # duration of the attack phase
        self.attack_time = attack_time

        # duration of the decay phase
        self.decay_time = decay_time

        # duration of the release phase
        self.release_time = release_time


        # time step
        self.dt = dt


        # internal time
        self.internal_time = 99999999.0

        # levels for the different phases
        self.start_level = start_level
        self.after_decay_level = after_decay_level
        self.attack_level = attack_level
        self.after_release_level = after_release_level  # level after release


        # callable to connect start_level and attack_level
        point_a = (0.0, self.start_level)
        point_b = (self.attack_time, self.attack_level)
        self.attack_function = LinearConnector(point_a, point_b)

        # callable to connect attack_level and after_decay_level
        point_a = (self.attack_time, self.attack_level)
        point_b = (self.attack_time + self.decay_time, self.after_decay_level)
        self.decay_function = LinearConnector(point_a, point_b)


        # callable to reach after_release_level; is defined later
        self.release_function = None

        # The time the release phase has been initiated
        self._release_hit_time = None

        # at the beginning, it is not active
        self.is_active = False

        self.current_value = 0.0


    def reset_start_level(self, start_level):
        self.start_level = start_level
        point_a = (0.0, self.start_level)
        point_b = (self.attack_time, self.attack_level)
        self.attack_function = LinearConnector(point_a, point_b)


    def reset_and_start(self):
        # is in release phase?
        self._release = False
        self.is_active = True

        # The time the release phase has been initiated
        self._release_hit_time = None

        # What is the level when the release phase is triggered?
        self._release_hit_level = None
        self.internal_time = 0.0




    # increment internal time
    def step(self):
        self.internal_time += self.dt
        if self._release_hit_time:
            if self.internal_time > self._release_hit_time + self.release_time:
                self.is_active = False


    def set_release(self):
        self._release_hit_time = self.internal_time
        self._release_hit_level = self()
        self._release = True

        # callable to reach after_release_level
        point_a = (self._release_hit_time, self._release_hit_level)
        point_b = (self._release_hit_time + self.release_time, self.after_release_level)

        self.release_function = LinearConnector(point_a, point_b)



    # get the current value
    #def get(self):
    def __call__(self):
        if not self.is_active:
            return 0.0
        elif not self._release:
            if self.internal_time < self.attack_time:
                value = self.attack_function(self.internal_time)
            elif self.internal_time < self.attack_time + self.decay_time:
                value = self.decay_function(self.internal_time)
            else:
                value = self.after_decay_level
        else:
            if self.internal_time < self._release_hit_time + self.release_time:
                value = self.release_function(self.internal_time)
                # if self.release_time == 11.81:
                #     if self.internal_time - self._release_hit_time < 0.5 * self.release_time:
                #         print(self.release_time, self._release_hit_time + self.release_time, self.internal_time, value)
            else:
                #print(self.internal_time, "hallo")
                value = self.after_release_level
        self.current_value = value
        return value


# Do some testing.
def main():
    dt = 1.0 / 44000.0
    e = Envelope(
        dt=dt,
        attack_time=0.15,
        decay_time=0.20,
        release_time=1.0,
        after_decay_level=0.1)
    release_set = False
    e.reset_and_start()
    def waveform(x): return 1.0 if x < 0.5 else -1.0

    import oscillator
    o = oscillator.Oscillator(frequency=940.0, dt=dt, waveform=waveform)

    with open("test.dat", "w") as outfile:
        for i in range(165700):
            value = e() * o()
            time = e.internal_time
            outfile.write("%f %f\n" % (time, value))
            # print(time, e.is_finished())
            if time > 0.5 and not release_set:
                e.set_release()
                release_set = True
            e.step()
            o.step()


if __name__ == "__main__":
    main()
