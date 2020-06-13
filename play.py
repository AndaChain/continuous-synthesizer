import pygame
import sounddevice as sd
import options_play
from frequency_board import FrequencyBoard
from synth import Synth
from sets import Set
import os

def main():
    options = options_play.get_options()
    samplerate = options["samplerate"]
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
                  bass_after_decay_level=options["bass_after_decay_level"],
                  bass_transposition_factor=1.0,
                  volume=options["volume"])

    # set-up pygame dislay
    full_screen = options["fullscreen"]
    pygame.init()
    if full_screen:
        os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
        info = pygame.display.Info()
        options["size_x"] = info.current_w
        options["size_y"] = info.current_h
        display = pygame.display.set_mode((info.current_w, info.current_h), pygame.NOFRAME)
    else:
        display = pygame.display.set_mode((options["size_x"], options["size_y"]))


    freq_board = FrequencyBoard(options["size_x"], options["size_y"],
                           filename=options["frequency_board"],
                           transition_size=options["transition_size"],
                           wildcard_frequency=options["wildcard_frequency"],
                           shuffle_row_frequencies=options["shuffle_row_frequencies"])




    for ix in range(options["size_x"]):
        for iy in range(options["size_y"]):
            color =  freq_board.colors[iy][ix][::-1]
            display.set_at((ix,iy), color)
    pygame.display.update()

    # initialize variables
    running = True
    is_sliding = False
    bass_hold = False
    current_bass_key = None

    current_bass_keys =  Set([])
    bass_frequencies = freq_board.get_bass_frequencies(options["bass_frequencies_filename"])
    bass_keys = get_bass_keys()
    bass_change = 2.0**(1.0/96.0)

    bass_change_pressed = False

    with sd.OutputStream(channels=1, callback=synth, samplerate=samplerate):
        while running:
            sd.sleep(1)
            keys = pygame.key.get_pressed()

            # bass transpose
            if keys[pygame.K_DOWN] and (not bass_change_pressed):
                synth.bass_transposition_factor /= bass_change
                print("transpose bass down " + str(synth.bass_transposition_factor))
                bass_change_pressed = True
            elif keys[pygame.K_UP] and (not bass_change_pressed):
                synth.bass_transposition_factor *= bass_change
                bass_change_pressed = True
                print("transpose bass up " + str(synth.bass_transposition_factor))

            if not (keys[pygame.K_DOWN] or keys[pygame.K_UP]) and bass_change_pressed:
                bass_change_pressed = False


            for key in list(current_bass_keys):
                if not keys[key]:
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

            if len(current_bass_keys) == 0 and bass_hold:
                bass_hold = False
                synth.release_bass_envelope = True

            for event in pygame.event.get():
                if event.type == pygame.MOUSEMOTION:
                    if is_sliding:
                        pos = pygame.mouse.get_pos()
                        pos_x = pos[0]
                        pos_y = pos[1]
                        freq = freq_board.frequencies[pos_y][pos_x]
                        synth.set_frequency(freq)

                # mouse buttons are pressed
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button in [1,3]:
                        is_sliding = True
                        pos = pygame.mouse.get_pos()
                        pos_x = pos[0]
                        pos_y = pos[1]
                        freq = freq_board.frequencies[pos_y][pos_x]
                        synth.set_frequency(freq)
                        synth.start_envelope = True


                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button in [1,3]:
                        is_sliding = False
                        synth.release_envelope = True

                if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
                    running = False



def get_bass_keys():
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
    return bass_keys

if __name__ == '__main__':
    main()
