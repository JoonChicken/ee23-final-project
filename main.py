import numpy as np
import matplotlib.pyplot as plt
import collections
import argparse
import pyaudio
import soundfile as sf
import impulseresponse
    

# Converts a stereo signal, represented in a numpy array, into a mono singal
def stereo2mono(signal):
    return np.mean(signal, axis=1)

# Our best attempt at not using libraries to convolve the signals
# we found that time-domain convolution with basic numpy arrays was taking too long
def manual_convolve(inputsig, ir):
    input_len = len(inputsig)
    ir_len = len(ir)

    # Convert to frequency domain
    in_fft = np.fft.fft(inputsig, n=(input_len + ir_len - 1))
    ir_fft = np.fft.fft(ir, n=(input_len + ir_len - 1))
    
    # Perform convolution
    convolved_fft = in_fft * ir_fft
    
    # Convert back to time domain
    result = np.fft.ifft(convolved_fft)
    
    return np.real(result)


# If the user specifies that they don't want realtime input and instead
# provides an input file, this function runs to do convolution on the files
def non_realtime_convolve(inputfile, irfile, outputfile):
        # Load data
        # Using the python soundfile library (docs found here: https://python-soundfile.readthedocs.io/en/0.13.1/)
        # import any audio file and output it to a 2D numpy array (stereo data even if input is mono)
        input_sig, input_rate = sf.read(inputfile, always_2d=True)
        input_sig = stereo2mono(input_sig)
        ir_sig, ir_rate = sf.read(irfile, always_2d=True)
        ir_sig = stereo2mono(ir_sig)

        # Output generation
        output = manual_convolve(input_sig, ir_sig) # Output result to file
        sf.write(outputfile, output, input_rate)
        print(f"Saved audio to {outputfile}")

        for name, data in zip(
            ["Input", "Impulse response", "Output"],
            [input_sig, ir_sig, output]
        ):
            plt.figure(figsize=(10, 4))
            plt.plot(data)
            plt.title(f"{name} audio")
            plt.xlabel("Samples")
            plt.ylabel("Amplitude")
            plt.grid(True)
            plt.show()


# Implementation of real-time convolution, taking in input from computer
# audio device and outputting to another audio file (possibly change to speaker
# output later)
def realtime_convolve(irfile):
    # get ir audio:
    ir_sig, ir_rate = sf.read(irfile, always_2d=True)
    ir_sig = stereo2mono(ir_sig)
    
    IR_LEN = len(ir_sig)

    CHUNK_SIZE = 1024
    AUDIO_FORMAT = pyaudio.paFloat32
    AUDIO_CHANNELS = 1
    AUDIO_RATE = 44100

    buffer_size = CHUNK_SIZE + IR_LEN - 1
    tail_buffer = np.zeros(buffer_size, dtype=np.float32)

    p = pyaudio.PyAudio()

    # open stream from microphone
    instream = p.open(format=AUDIO_FORMAT,
                      channels=AUDIO_CHANNELS,
                      rate=AUDIO_RATE,
                      frames_per_buffer=CHUNK_SIZE,
                      input=True)
    
    # open stream to output to speaker
    outstream = p.open(format=AUDIO_FORMAT,
                       channels=AUDIO_CHANNELS,
                       rate=AUDIO_RATE,
                       frames_per_buffer=CHUNK_SIZE,
                       output=True)

    # Run until a key is pressed
    try:
        while (True):
            # read in from system default microphone
            live_data = instream.read(CHUNK_SIZE, exception_on_overflow=False)
            live_signal = np.frombuffer(live_data, dtype=np.float32).copy()

            # use our convolution function to apply filter
            live_result = manual_convolve(live_signal, ir_sig)
            tail_buffer += live_result

            output_result = tail_buffer[:CHUNK_SIZE].copy()
            tail_buffer = np.roll(tail_buffer, -CHUNK_SIZE)
            tail_buffer[-CHUNK_SIZE:] = 0
            
            # output to system default speaker
            outstream.write(output_result.astype(np.float32).tobytes())
    except KeyboardInterrupt:
        # clean up, close streams
        p.close(outstream)
        p.close(instream)
        print("END")
        return
    

def main():
    # Define input and output arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=False)
    parser.add_argument("--ir", required=True)
    parser.add_argument("--output", required=False)
    parser.add_argument("--realtime", action="store_true")    
    args = parser.parse_args()

    if args.realtime:
        realtime_convolve(args.ir)
    else:
        if args.input is None or args.output is None:
            parser.error("--input and --output arguments required for non-realtime convolution")
            return
        non_realtime_convolve(args.input, args.ir, args.output)
  

if __name__ == "__main__":
    main()