import numpy as np
from scipy.signal import hilbert, butter, filtfilt, lfilter

import matplotlib.pyplot as plt

FS = 62.5e6 # Hz
BIT_PERIOD = 9.44e-6
BG_ERROR_MARGIN = 2



###                          ###
#------ HELPER FUNCTIONS ------#
###                          ###
def estimate_fc(signal, fs):
    spectrum = np.fft.fft(signal)
    freqs = np.fft.fftfreq(len(signal), 1/fs)
    return abs(freqs[np.argmax(np.abs(spectrum))])


def plot_spectrum(signal, fs):
    N = len(signal)

    # FFT
    S = np.fft.fft(signal)
    freqs = np.fft.fftfreq(N, 1/fs)

    # Only positive frequencies
    mask = freqs >= 0

    plt.plot(freqs[mask], np.abs(S[mask]))
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude")
    plt.title("Spectrum")
    plt.savefig("signal-fft.png")
    plt.clf


def plot_signal(sig, fs, title="Signal"):
    T = np.arange(len(sig)) / fs

    plt.figure(figsize=(12,4))
    plt.plot(T, sig, linewidth=.5)

    plt.title(title)
    plt.xlabel("Time [s]")
    plt.ylabel("Amplitude")

    plt.grid()

    plt.savefig(title+".png")

    plt.clf()
    plt.close("all")


# bandpass = (50, 70) # reader
# bandpass = (3, 5) # card
def extract_signal_by_amplitude(sig, step = 1000, bandpass = (0,90), threshold = 5):
    signal_indices = []
    b_min, b_max = bandpass

    for i in range(0, len(sig) - step, step):
        window = sig[i : i + step]
        window_max = np.max(window)
        window_min = np.min(window)

        # print(i, window_min, window_max, abs(b_min - window_min) < threshold and abs(b_max - window_max) < threshold)
        if abs(b_min - window_min) < threshold and abs(b_max - window_max) < threshold:
            #print(i, window_min, window_max, abs(b_min - window_min) < threshold and abs(b_max - window_max) < threshold)
            signal_indices.append(i)

    blocks = []
    start_b = signal_indices[0]
    for j in range(1, len(signal_indices)):
        signal_indices[j]

        if signal_indices[j] - signal_indices[j-1] > (step * 2):
            blocks.append((start_b, (signal_indices[j-1] + step)))
            start_b = signal_indices[j]

    return blocks


def bits_to_hex(bit_list):
    hex_values = []
    # Step through the list in chunks of 9 (8 data + 1 parity)
    for i in range(0, len(bit_list) - 8, 9):
        byte_bits = bit_list[i : i+8]

        if i + 8 >= len(bit_list): break
        parity_bit = bit_list[i + 8]

        # Calculate parity (Odd)
        ones_count = sum(byte_bits)
        is_valid = (ones_count + parity_bit) % 2 != 0

        if(not is_valid):
            print("Warning parity check unsuccesfull")

        # ISO 14443-A is LSB-first: Reverse the bits to read normally
        # [::-1] flips the bits before converting to int
        byte_val = int("".join(map(str, byte_bits[::-1])), 2)
        hex_values.append(hex(byte_val))
    return hex_values


def decode_is_one(b_max, b_min, a_max, a_min):
    b_avg = (b_max + b_min) / 2
    a_avg = (a_max + a_min) / 2
    return abs(b_avg - a_avg) < 0.1 or b_avg > a_avg



###                          ###
#---- DECODE COMMUNICATION ----#
###                          ###

def miller_decode(sig):
    T = np.arange(len(sig)) / FS # µs
    decoded = []

    background_level = sig[0]

    # plt.plot(T, sig)
    # plt.ylim(50, 90)
    # plt.axhline(background_level, color="black")

    # Set set lines
    bit_lines = []
    bit_lines.append(T[0])

    acc = 0
    for i in range(len(sig)):
        acc += (1/FS)

        if(acc > BIT_PERIOD):
            bit_lines.append(T[i])
            acc = 0

    half_lines = [x + BIT_PERIOD/2 for x in bit_lines]

    # for line in bit_lines:
    #     plt.axvline(line, color="orange")
    # for line in half_lines:
    #     plt.axvline(line, linestyle="--", color="orange")

    # Decode signal
    before_mid_min = background_level
    after_mid_min = background_level
    after = False

    for i, x in enumerate(sig):
        if i/FS in bit_lines:
            if abs(before_mid_min - background_level) >= BG_ERROR_MARGIN or \
               abs(after_mid_min - background_level) >= BG_ERROR_MARGIN:
                if before_mid_min < after_mid_min and \
                   before_mid_min < background_level - BG_ERROR_MARGIN:
                    decoded.append(0)
                else:
                    decoded.append(1)
            before_mid_min = background_level
            after_mid_min = background_level
            after = False

        if i/FS in half_lines:
            after = True

        if after:
            if x < after_mid_min:
                after_mid_min = x
        else:
            if x < before_mid_min:
                before_mid_min = x

    # plt.show()
    return decoded


def manchester_decode(sig):
    T = np.arange(len(sig)) / FS  # µs

    # TODO: Decode signal

    return [1,0,1,0,0,1,1,1,0,0,1]



###                               ###
#---------- MAIN ANALYSIS ----------#
###                               ###

sig = np.loadtxt("../waveform-traces/trace-2026-03-30 16:20:55.750289-62.5Mss-12.5Mpts.txt")
sig = sig[int(4e6):int(1.1e7)]  # cut region of interest
plot_signal(sig, FS, "raw signal")


analytic_signal = hilbert(sig)
amplitude_envelope = np.abs(analytic_signal)

b, a = butter(4, 2e6 / (FS / 2), btype='low')
smoothed_signal = lfilter(b, a, amplitude_envelope)

# remove start and end of envelope
smoothed_signal = smoothed_signal[1000:-1000000]

plot_signal(smoothed_signal, FS, "smoothed signal")

# Extract blocks of signal by amplitude
reader_blocks = extract_signal_by_amplitude(smoothed_signal, 1000, (0, 82), 5)
card_blocks = extract_signal_by_amplitude(smoothed_signal, 1000, (70, 78), 2)

# For each call response, decode the card and reader messages
for i, rc in enumerate(zip(reader_blocks, card_blocks)):
    reader, card = rc
    start_r, stop_r = reader
    start_c, stop_c = card

    plot_signal(smoothed_signal[start_r: stop_c], FS, f"reader card {i}")

    # reader message block
    sig_r = smoothed_signal[start_r - 2000 : stop_r + 2000]
    message_r = miller_decode(sig_r)
    print("Reader message: ", message_r)

    # card message block
    sig_c = smoothed_signal[start_c - 2000: stop_c + 2000]
    message_c = manchester_decode(sig_c)
    print("Card bytes", message_c)
