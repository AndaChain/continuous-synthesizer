# continuous-synthesizer
This is a synthesizer written in Python. It is played with the mouse. You can change the pitch by moving the cursor. That way you can create continuous transitions between any pitches you pre-define in a text file. In addition, you can also play notes on your computer keyboard to accompany yourself.


## Requirements
* Python 2
* numpy, pygame, sounddevice

## Warnings
* The program has not been optimized for performance. Try to use a very small number of voices.
* The program uses the Python function *eval* to evaluate expressions in the text file which defines the frequencies (frequency boards). Although it is checked whether those expressions contain only characters for math operations, you should be careful that you never load any file with malicious commands.
