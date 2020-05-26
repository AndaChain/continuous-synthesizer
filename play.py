# import argparse

# import numpy as np

# import math

import pygame
import sounddevice as sd
from oscillator import Oscillator
import options_play
from frequency_board import FrequencyBoard
import envelope
import wave
import struct
import copy
import datetime

class Synth:
    def __init__(self, no_of_voices=2, waveform="sine", samplerate=None, transposition_factor=1.0):
        self.no_of_voices = no_of_voices
        self.current_voice_index = 0
        self.samplerate = samplerate

        self.oscillators = [Oscillator(waveform=waveform, dt=1.0/self.samplerate, frequency=100.0) \
                            for i in range(self.no_of_voices)]

        # self.oscillator = Oscillator(waveform=waveform, dt=1.0/self.samplerate, frequency=100.0)
        self.transposition_factor = transposition_factor
        self.envelopes = [envelope.Envelope(attack_time=0.01,decay_time = 0.01,after_decay_level=1.0, release_time = 3.51) for i in range(self.no_of_voices)]



        self.start_envelope = False
        self.release_envelope = False
        self.is_recording = False
        self.recorded_wave = []
        self.volume = 0.3

    def set_frequency(self, f):
        self.oscillators[self.current_voice_index].frequency = self.transposition_factor * f


    def save_wave(self):
        internalAmplitude = 32767
        no_of_channels = 1
        date_time_string = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        filename = "./wave_files/" + date_time_string + ".wav"
        out_file = wave.open(filename, "w")
        out_file.setframerate(self.samplerate)
        out_file.setnchannels(no_of_channels)
        out_file.setsampwidth(2)
        for value in copy.deepcopy(self.recorded_wave):
            out_file.writeframes(struct.pack('h', int(internalAmplitude * value)))
        out_file.close()
        print("Written to file " + filename)





    def __call__(self, outdata, frames, time, status):
        # if status:
        #     print(status)
        # t = (self.start_idx + np.arange(frames)) * self.dt * 2.0 * np.pi * self.frequency
        # #print(t)
        # t = t.reshape(-1, 1)
        # outdata[:] = self.amplitude * np.sin(t)
        # self.start_idx += frames
        if self.start_envelope:
            self.start_envelope = False
            current_env_value = self.envelopes[self.current_voice_index].current_value
            self.envelopes[self.current_voice_index].reset_start_level(current_env_value)
            self.envelopes[self.current_voice_index].reset_and_start()

        if self.release_envelope:
            self.release_envelope = False
            self.envelopes[self.current_voice_index].set_release()
            self.current_voice_index = (self.current_voice_index + 1) % self.no_of_voices


        for i in range(frames):
            #print( )
            v = 0.0
            for k in range(self.no_of_voices):
                v += self.oscillators[k].get() * self.envelopes[k]()
            v *= self.volume
            outdata[i] = v

            if self.is_recording:
                self.recorded_wave.append(v)

            # step envelope and oscillator
            for k in range(self.no_of_voices):
                self.envelopes[k].step()
                self.oscillators[k].step()







def main():
    options = options_play.get_options()
    #samplerate = sd.query_devices(options["device"], 'output')['default_samplerate']
    samplerate = 44100
    sd.default.samplerate = samplerate
    synth = Synth(no_of_voices=options["no_of_voices"], waveform=options["waveform"], samplerate=samplerate, transposition_factor=options["transposition_factor"])

    freq_board = FrequencyBoard(options["size_x"], options["size_y"],
                           filename=options["frequency_board"],
                           transition_size=options["transition_size"])

    pygame.init()
    display = pygame.display.set_mode((options["size_x"], options["size_y"]))
    for ix in range(options["size_x"]):
        for iy in range(options["size_y"]):
            color =  freq_board.colors[iy][ix][::-1]
            display.set_at((ix,iy), color)
    pygame.display.update()

    running = True
    is_sliding = False
    # hold = False
    with sd.OutputStream(channels=1, callback=synth, samplerate=samplerate):
        while running:
            sd.sleep(1)
            keys = pygame.key.get_pressed()

            if keys[pygame.K_F11]:
                pygame.display.toggle_fullscreen()

            if keys[pygame.K_s]:
                if synth.is_recording:
                    print("Stop recording.")
                    synth.is_recording = False
                    synth.save_wave()
                    synth.recorded_wave = []
            if keys[pygame.K_r]:
                if not synth.is_recording:
                    print("Start recording.")
                    synth.is_recording = True


            # if keys[pygame.K_LCTRL]:
            #     hold = True
            # else:
            #     hold = False
            #     if not is_sliding:
            #         synth.amplitude = 0.0


            for event in pygame.event.get():
                if event.type == pygame.MOUSEMOTION:
                    if is_sliding:
                        pos = pygame.mouse.get_pos()
                        pos_x = pos[0]
                        pos_y = pos[1]

                        freq = freq_board.frequencies[pos_y][pos_x]
                        # synth.next_freq = freq
                        synth.set_frequency(freq)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    # if the left button is pressed
                    if event.button in [1,3]:
                        is_sliding = True
                        pos = pygame.mouse.get_pos()
                        pos_x = pos[0]
                        pos_y = pos[1]
                        freq = freq_board.frequencies[pos_y][pos_x]
                        synth.set_frequency(freq)
                        synth.start_envelope = True
                        # callback.break_point = break_point
                        # callback.next_freq = freq
                        # callback.start_envelope = True


                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button in [1,3]:
                        is_sliding = False
                        # callback.release_envelope = True
                        # if not hold:
                            #synth.amplitude = 0.0
                        synth.release_envelope = True

                if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
                    running = False


if __name__ == '__main__':
    main()
