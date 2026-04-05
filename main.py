import pydub 
import numpy as np
import matplotlib.pyplot as plt
import collections
import argparse
import soundfile
import impulseresponse



# found here: https://stackoverflow.com/questions/53633177/how-to-read-a-mp3-audio-file-into-a-numpy-array-save-a-numpy-array-to-mp3
# converts an mp3 file to a numpy array
filetypes = enumerate(["mp3", "wav"])

def read(f, normalized=False):
    filetype = f.split(".")[-1]
    a = None
    if (filetype == "mp3"):
        a = pydub.AudioSegment.from_mp3(f)
    elif (filetype == "wav"):
        a = pydub.AudioSegment.from_wav(f)
    y = np.array(a.get_array_of_samples())
    if a.channels == 2:
        y = y.reshape((-1, 2))
    if normalized:
        return a.frame_rate, np.float32(y) / 2**15
    else:
        return a.frame_rate, y
    

# Define input and output arguments
parser = argparse.ArgumentParser()
parser.add_argument("--input", required=True)
parser.add_argument("--impulse", required=True)
parser.add_argument("--output", required=True)
args = parser.parse_args()

# Load data
input_rate, input = read(args.input)
ir_rate, ir = read(args.impulse)


# plt.figure(figsize=(10, 4))
plt.plot(input)
plt.title("Input File Graph")
plt.xlabel("Samples")
plt.ylabel("Amplitude")
plt.grid(True)
plt.show()

# Fill in following constants with data from files
INPUT_BUF_LEN = 0
IR_BUF_LEN = 0

inputBuffer = collections.deque(maxlen=INPUT_BUF_LEN)
irBuffer = collections.deque(maxlen=IR_BUF_LEN)
outputBuffer = collections.deque(maxlen=IR_BUF_LEN)


# soundfile.write(args.output, [[our convolved audio]], input_rate)
# print(f"Saved audio to {args.output}")