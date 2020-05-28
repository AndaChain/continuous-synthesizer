# import argparse

# import numpy as np

# import math

import pygame
import sounddevice as sd

import options_play
from frequency_board import FrequencyBoard


from synth import Synth



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
