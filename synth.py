import envelope
import wave
from oscillator import Oscillator
import struct
import copy
import datetime


class Synth:
    def __init__(self,
                no_of_voices=2,
                no_of_bass_voices=1,
                waveform="sine",
                samplerate=None,
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
