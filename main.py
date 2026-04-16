import numpy as np
import matplotlib.pyplot as plt
import collections
import argparse
import soundfile as sf
import impulseresponse
    

def stereo2mono(signal):
    return np.mean(signal, axis=1)


def manual_convolve(inputsig, ir):
    input_len = len(inputsig)
    print(input_len)
    ir_len = len(ir)
    print(ir_len)
    
    ir_flip = ir[::-1] 
    convolved = []

    padded_input = np.pad(inputsig, (ir_len - 1, ir_len - 1), mode='constant')

    for i in range (input_len + ir_len - 1):
        window = padded_input[i : i + ir_len]
        sum_curr = 0
        for j in range(ir_len):
            sum_curr += window[j] * ir_flip[j]
        convolved.append(sum_curr)
    
    return convolved


# Define input and output arguments
parser = argparse.ArgumentParser()
parser.add_argument("--input", required=True)
parser.add_argument("--ir", required=True)
parser.add_argument("--output", required=True)
args = parser.parse_args()

# Load data
# Using the python soundfile library (docs found here: https://python-soundfile.readthedocs.io/en/0.13.1/)
# import any audio file and output it to a 2D numpy array (stereo data even if input is mono)
input, input_rate = sf.read(args.input, always_2d=True)
ir, ir_rate = sf.read(args.ir, always_2d=True)
input = stereo2mono(input)
irsig = stereo2mono(ir)

# Fill in following constants with data from files
# INPUT_BUF_LEN = input.size()
# IR_BUF_LEN = ir.size()

### DEBUG!!!!!!!!!!!
# print("Input file length is:", INPUT_BUF_LEN, "samples.")
# print("Impulse file length is:", IR_BUF_LEN, "samples.")

# Define buffers (only if doing real time convolve so we can run the convolve function on chunks)
# inputBuffer = collections.deque(maxlen=INPUT_BUF_LEN)
# irBuffer = collections.deque(maxlen=IR_BUF_LEN)
# outputBuffer = collections.deque(maxlen=IR_BUF_LEN)

# Output generation
output = manual_convolve(input, irsig) # Output result to file
sf.write(args.output, output, input_rate)
print(f"Saved audio to {args.output}")

for name, data in zip(
    ["Input", "Impulse response", "Output"],
    [input, ir, output]
):
    plt.figure(figsize=(10, 4))
    plt.plot(data)
    plt.title(f"{name} audio")
    plt.xlabel("Samples")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()
