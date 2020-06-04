# continuous-synthesizer
This is a synthesizer written in Python. It is played with the mouse. You can change the pitch by moving the cursor. That way you can create continuous transitions between any pitches you pre-define in a text file. In addition, you can also play notes on your computer keyboard to accompany yourself.


## Requirements
* Python 2
* numpy, pygame, sounddevice

## Warnings
* The program has not been optimized for performance. Try to use a very small number of voices.
* The program uses the Python function *eval* to evaluate expressions in the text file which defines the frequencies (frequency boards). Although it is checked whether those expressions contain only characters for math operations, you should be careful that you never load any file with malicious commands.

## Usage
* Run `python play.py` to load all options from *options.cfg*.
* Run `python play.py --help` to see a list of command-line parameters which can be used to overwrite the values provided by the options file.

## Manual
### What are frequency boards?
The window of the program shows a colored area which is called frequency board. Each pixel of the window corresponds to a frequency. If the mouse button is held, the synthesizer is retuned to the frequency which is associated to the current cursor position.
A frequency board is created on the basis of text files (see examples in the folder ./frequency_boards). Those text files may contain several rows with each row being allowed to hold a different number of frequencies. If a row contains, e.g., three frequencies, the program will interpolate between the first and the second and between the second and the third frequency. The size of the interpolation area can be defined in the options file.

### Parameters in options.cfg
* *fullscreen*
If this is set to true, the program runs with full screen. In this case, the values of *size_x* and *size_y* are obsolete.
* *waveform*
The waveform of the oscillator. Allowed values: sine, square, sawtooth, triangle.
* *size_x*
The width of the window.
* *size_y*
The height of the window.
* *frequency_board*
The path to the frequency board, e.g., ./frequency_boards/just_intonation.txt.
* *bass_frequencies_filename*
The path to the frequencies of the bass notes (played on the keyboard).
* *transition_size*
Size of the region with interpolated pitches. Allowed values are from 0 to 1.
* *transposition_factor*
All frequencies are multiplied by this value. Set to 1.0 to turn off transposition.
* *no_of_voices*
No of voices (excluding the bass voice). Multiple voices are required if you play a note before the previous note has left the release phase.
* *attack_time*
Attack time in seconds for the mouse voice.
* *release_time*
Release time in seconds for the mouse voice.
* *decay_time*
Decay time in seconds for the mouse voice.
* *after_decay_level*
Volume after the decay (sustain) of the mouse voice. May be between 0 and 1.
* *bass_attack_time*
Attack time in seconds for the bass voice.
* *bass_release_time*
Release time in seconds for the bass voice.
* *bass_decay_time*
Decay time in seconds for the bass voice.
* *bass_after_decay_level*
Volume after the decay (sustain) of the bass voice. May be between 0 and 1.
* *wildcard_frequency*
The wildcard character _ in the files for the frequency boards and bass frequencies will be replaced with this value. Wildcards make it easy to transpose to a specific root frequency.
* *samplerate*
Sample rate in Hertz of the synthesis.
* *volume*
The sound signal of all voices (including bass voice) are multiplied by this factor. If you use multiple voices, you should make sure that this value is small enough to avoid clipping. May be between 0 and 1.
