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
    def __init__(self, no_of_voices=2, no_of_bass_voices=1, waveform="sine", samplerate=None,
                transposition_factor=1.0,
                attack_time=0.01,
                decay_time=0.01,
                after_decay_level=1.0,
                release_time=1.0,
                bass_attack_time=0.01,
                bass_decay_time=0.01,
                bass_after_decay_level=1.0,
                bass_release_time=1.0):
        self.no_of_voices = no_of_voices
        self.no_of_bass_voices = no_of_bass_voices
        self.current_voice_index = 0
        self.current_bass_voice_index = 0
        self.samplerate = samplerate

        self.oscillators = [Oscillator(waveform=waveform, dt=1.0/self.samplerate, frequency=100.0) \
                            for i in range(self.no_of_voices)]
        self.bass_oscillators = [Oscillator(waveform=waveform, dt=1.0/self.samplerate, frequency=100.0) \
                                for i in range(self.no_of_bass_voices)]


        self.transposition_factor = transposition_factor
        self.envelopes = [envelope.Envelope(attack_time=attack_time, decay_time=decay_time, after_decay_level=after_decay_level, release_time=release_time) for i in range(self.no_of_voices)]
        self.bass_envelopes = [envelope.Envelope(attack_time=bass_attack_time, decay_time=bass_decay_time, after_decay_level=bass_after_decay_level, release_time=bass_release_time) for i in range(self.no_of_bass_voices)]

        self.start_envelope = False
        self.release_envelope = False
        self.start_bass_envelope = False
        self.release_bass_envelope = False
        self.is_recording = False
        self.recorded_wave = []
        self.volume = 0.3

    def set_frequency(self, f):
        self.oscillators[self.current_voice_index].frequency = self.transposition_factor * f

    def set_bass_frequency(self, f):
        self.bass_oscillators[self.current_bass_voice_index].frequency = self.transposition_factor * f


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

        if self.start_bass_envelope:
            self.start_bass_envelope = False
            current_env_value = self.bass_envelopes[self.current_bass_voice_index].current_value
            self.bass_envelopes[self.current_bass_voice_index].reset_start_level(current_env_value)
            self.bass_envelopes[self.current_bass_voice_index].reset_and_start()

        if self.release_envelope:
            self.release_envelope = False
            self.envelopes[self.current_voice_index].set_release()
            self.current_voice_index = (self.current_voice_index + 1) % self.no_of_voices

        if self.release_bass_envelope:
            self.release_bass_envelope = False
            self.bass_envelopes[self.current_bass_voice_index].set_release()
            self.current_bass_voice_index = (self.current_bass_voice_index + 1) % self.no_of_bass_voices


        for i in range(frames):
            #print( )
            v = 0.0
            for k in range(self.no_of_voices):
                v += self.oscillators[k].get() * self.envelopes[k]()

            for k in range(self.no_of_bass_voices):
                v += self.bass_oscillators[k].get() * self.bass_envelopes[k]()
            v *= self.volume


            outdata[i] = v

            if self.is_recording:
                self.recorded_wave.append(v)

            # step envelope and oscillator
            for k in range(self.no_of_voices):
                self.envelopes[k].step()
                self.oscillators[k].step()

            for k in range(self.no_of_bass_voices):
                self.bass_envelopes[k].step()
                self.bass_oscillators[k].step()







def main():
    options = options_play.get_options()
    #samplerate = sd.query_devices(options["device"], 'output')['default_samplerate']
    samplerate = 44100
    sd.default.samplerate = samplerate
    synth = Synth(no_of_voices=options["no_of_voices"],
                  no_of_bass_voices=1,
                  waveform=options["waveform"],
                  samplerate=samplerate,
                  transposition_factor=options["transposition_factor"],
                  attack_time=options["attack_time"],
                  release_time=options["release_time"],
                  decay_time=options["decay_time"],
                  after_decay_level=options["after_decay_level"],
                  bass_attack_time=options["bass_attack_time"],
                  bass_release_time=options["bass_release_time"],
                  bass_decay_time=options["bass_decay_time"],
                  bass_after_decay_level=options["bass_after_decay_level"])

    freq_board = FrequencyBoard(options["size_x"], options["size_y"],
                           filename=options["frequency_board"],
                           transition_size=options["transition_size"],
                           wildcard_frequency=options["wildcard_frequency"])

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
    # bass_hold = [False for i in range(13)]
    bass_hold = False
    current_bass_key = None
    from sets import Set
    current_bass_keys =  Set([])
    bass_f = 80.0
    bass_frequencies = freq_board.get_bass_frequencies(options["bass_frequencies_filename"])
    bass_keys = []
    bass_keys.append(pygame.K_a)
    bass_keys.append(pygame.K_w)
    bass_keys.append(pygame.K_s)
    bass_keys.append(pygame.K_e)
    bass_keys.append(pygame.K_d)
    bass_keys.append(pygame.K_f)
    bass_keys.append(pygame.K_t)
    bass_keys.append(pygame.K_g)
    bass_keys.append(pygame.K_z)
    bass_keys.append(pygame.K_h)
    bass_keys.append(pygame.K_u)
    bass_keys.append(pygame.K_j)
    bass_keys.append(pygame.K_k)

    with sd.OutputStream(channels=1, callback=synth, samplerate=samplerate):
        while running:
            sd.sleep(1)
            keys = pygame.key.get_pressed()

            if keys[pygame.K_F11]:
                pygame.display.toggle_fullscreen()

            # if keys[pygame.K_s]:
            #     if synth.is_recording:
            #         print("Stop recording.")
            #         synth.is_recording = False
            #         synth.save_wave()
            #         synth.recorded_wave = []
            # if keys[pygame.K_r]:
            #     if not synth.is_recording:
            #         print("Start recording.")
            #         synth.is_recording = True
            #
            # for bass_index, bass_key in enumerate(bass_keys):
            #     if keys[bass_key] and not bass_hold[bass_index]:
            #         other_key_pressed = False
            #         for i in range(len(bass_hold)):
            #             if bass_hold[i] and i != bass_index:
            #                 other_key_pressed = True
            #             bass_hold[i] = False
            #         bass_hold[bass_index] = True
            #         synth.set_bass_frequency(bass_frequencies[bass_index])
            #         if not other_key_pressed:
            #             synth.start_bass_envelope = True
            #     elif not keys[bass_key] and bass_hold[bass_index]:
            #         bass_hold[bass_index] = False
            #         synth.release_bass_envelope = True

            for key in list(current_bass_keys):
                if not keys[key]:
                    # current_bass_keys.discard(key)
                    current_bass_keys = Set([])
                    break

            for bass_index, bass_key in enumerate(bass_keys):
                if keys[bass_key]:
                    if not bass_key in current_bass_keys:
                        synth.set_bass_frequency(bass_frequencies[bass_index])
                        current_bass_keys.add(bass_key)
                        current_bass_key = bass_key
                        synth.start_bass_envelope = True
                        current_bass_key = bass_key
                        bass_hold = True
                        # if not bass_hold:
                        #     bass_hold = True
                        #     #current_bass_key = bass_key
                        #     synth.start_bass_envelope = True
                        #     print("bass", current_bass_key)



            # for bass_index, bass_key in enumerate(bass_keys):
            if len(current_bass_keys) == 0 and bass_hold:
                #current_bass_keys = Set([])
                bass_hold = False
                synth.release_bass_envelope = True




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
