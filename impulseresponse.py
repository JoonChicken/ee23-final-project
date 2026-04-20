# This file generates a sample impulse response for us to convolve an input
# audio signal with

import numpy as np
import matplotlib.pyplot as plt
import pyroomacoustics as pra
import os

def get_rir(width, length, height):
    # Room parameters (meters)
    room_dim = [width, length, height]
    # Absorption coefficient 0.2 is a standard living room/office
    absorption = 0.2

    # Maximum number of reflections 
    max_order = 15

    room = pra.ShoeBox(
        room_dim, 
        fs=16000, 
        materials=pra.Material(absorption), 
        max_order=max_order
    )

    # Sim microphone source location: [x, y, z]
    source_pos = [1, 1, 1.5]
    room.add_source(source_pos)

    # Sim mic array location
    mic_pos = np.array([[2.5, 3.5, 1.5]]).T 
    room.add_microphone_array(mic_pos)

    # Compute the RIR
    room.compute_rir()

    # Plot the RIR: list of lists: rir[mic_index][source_index]
    rir = room.rir

    plt.figure(figsize=(10, 4))
    plt.plot(np.array(rir).flatten())
    plt.title("Generated Room Impulse Response (RIR)")
    plt.xlabel("Samples")
    plt.ylabel("Amplitude")
    plt.grid(True)
    output_dir = r'D:\Tufts\2026_Spring\linear systems\ee23-final-project\output_imgs'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 2. Save using a raw string for the full path
    save_path = os.path.join(output_dir, 'impulse_response.png')
    plt.savefig(save_path)

# get_rir(5, 7, 12)
