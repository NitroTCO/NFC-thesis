import numpy as np
from scipy.signal import hilbert, butter, filtfilt, lfilter
import getopt
from sys import argv
import time

import matplotlib.pyplot as plt

FS = 62.5e6 # Hz
BIT_PERIOD = 9.44e-6
BG_ERROR_MARGIN = 1
PLOTTING = False

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


def save_signal_to_file(sig, file_path):
    with open(file_path, "w") as f:
        for x in sig:
            f.write(f"{x}\n")


###                          ###
#---- DECODE COMMUNICATION ----#
###                          ###

def miller_decode(sig):
    background_level = sig[0]
    decoded = []
    if PLOTTING:
        T = np.arange(len(sig)) / FS  # µs
        plt.plot(T, sig)

    before = background_level
    after = background_level
    acc = 0
    start = True
    for i, x in enumerate(sig):
        # looking for start of message
        if abs(x - background_level) < BG_ERROR_MARGIN and start:
            continue

        if start:
            start = False
            if PLOTTING:
                plt.axvline(i/FS, linewidth=.5, color="red")
                plt.xlim(left=(i/FS)-BIT_PERIOD)

        start_time = time.time()
        acc += 1/FS

        # bit period expired, decode
        if acc > BIT_PERIOD:
            if PLOTTING:
                plt.axvline(i/FS, linewidth=.5, color="black")
            if abs(before - background_level) >= BG_ERROR_MARGIN or \
               abs(after - background_level) >= BG_ERROR_MARGIN:
                if PLOTTING:
                    plt.axvline(i/FS - BIT_PERIOD/2, linewidth=.5, color="black", linestyle="--")
                if abs(before - after) > 0.1:
                    if before < after:
                        decoded.append(1)
                        if PLOTTING:
                            plt.plot(i/FS - BIT_PERIOD/2, 20, "go")
                    else:
                        decoded.append(0)
                        if PLOTTING:
                            plt.plot(i/FS - BIT_PERIOD/2, 10, "go")
                elif decoded[-1] == 1:
                    decoded.append(0)
                    if PLOTTING:
                        plt.plot(i/FS - BIT_PERIOD/2, 10, "go")
                        plt.axvline(1/FS, linewidth=.5, color="red")
                        plt.xlim(right=1/FS+BIT_PERIOD)
                    break

            before = background_level
            after = background_level
            acc = 0
            continue

        if acc > BIT_PERIOD/2:
            if x > after:
                after = x
        else:
            if x > before:
                before = x

    end_time = time.time()
    print(f"Miller decode: {end_time-start_time} s elapsed.")
    if PLOTTING:
        plt.show()
    return bits_to_hex(decoded[1:])


def manchester_decode(sig):
    background_level = sig[0]
    decoded = []
    if PLOTTING:
        T = np.arange(len(sig)) / FS  # µs
        plt.plot(T, sig)

    before = background_level
    after = background_level
    acc = 0
    start = True
    for i, x in enumerate(sig):
        # looking for start of message
        if abs(x - background_level) < BG_ERROR_MARGIN and start:
            continue

        if start:
            start = False
            if PLOTTING:
                plt.axvline(i/FS, linewidth=.5, color="red")
                plt.xlim(left=(i/FS)-BIT_PERIOD)

        start_time = time.time()
        acc += 1/FS

        # bit period expired, decode
        if acc > BIT_PERIOD:
            if PLOTTING:
                plt.axvline(i/FS, linewidth=.5, color="black")
            if abs(before - background_level) >= BG_ERROR_MARGIN or \
               abs(after - background_level) >= BG_ERROR_MARGIN:
                # stop if no signal
                if(abs(before - after) < 0.01):
                    if PLOTTING:
                        plt.axvline(i/FS, linewidth=.5, color="red")
                        plt.xlim(right=i/FS+BIT_PERIOD)
                    break

                if PLOTTING:
                    plt.axvline(i/FS - BIT_PERIOD/2, linewidth=.5, color="black", linestyle="--")

                decoded.append(1 if before > after else 0)
                if PLOTTING:
                    plt.plot(i/FS - BIT_PERIOD/2, 76 if before > after else 74, "go")

            before = background_level
            after = background_level
            acc = 0
            continue

        if acc > BIT_PERIOD/2:
            if x > after:
                after = x
        else:
            if x > before:
                before = x

    end_time = time.time()
    print(f"Manchester decode: {end_time-start_time} s elapsed.")
    if PLOTTING:
        plt.show()
    return bits_to_hex(decoded[1:])



###                               ###
#-------- PROGRAM AGRUMENTS --------#
###                               ###
trace = "../waveform-traces/trace-2026-03-30 16:20:55.750289-62.5Mss-12.5Mpts.txt"
args = argv[1:]
options = "hpt:"
long_options = ["Help", "Plot", "Trace="]

try:
    arguments, values = getopt.getopt(args, options, long_options)
    for currentArg, currentVal in arguments:
        if currentArg in ("-h", "--Help"):
            print("""Usage:
    python mfdes_demodulate.py [options]

Options:
    -h --Help               :  Show this message
    -p --Plot               :  Show plots while running
    -t --Trace <trace file> :  Set to decode given file""")
            exit(0)
        elif currentArg in ("-p", "--Plot"):
            PLOTTING = True
        elif currentArg in ("-t", "--Trace"):
            trace = currentVal
except getopt.error as err:
    print(str(err))
    exit(1)

###                               ###
#---------- MAIN ANALYSIS ----------#
###                               ###

try:
    sig = np.loadtxt(trace)
except FileNotFoundError:
    print(f"No such file or directory: {trace}")
    exit(1)
sig = sig[int(4e6):int(1.1e7)]  # cut region of interest
# plot_signal(sig, FS, "raw signal")


analytic_signal = hilbert(sig)
amplitude_envelope = np.abs(analytic_signal)
# plot_signal(amplitude_envelope, FS, "absoluted hilbert")

b, a = butter(4, 2e6 / (FS / 2), btype='low')
smoothed_signal = lfilter(b, a, amplitude_envelope)

# remove start and end of envelope
smoothed_signal = smoothed_signal[1000:-1000000]

# plt.plot(np.arange(0, 590, 1), smoothed_signal[0:590])
# plt.show()
# exit(0)

save_signal_to_file(smoothed_signal, "../smoothed_signal.txt")

# plot_signal(smoothed_signal, FS, "smoothed signal")

# Extract blocks of signal by amplitude
reader_blocks = extract_signal_by_amplitude(smoothed_signal, 1000, (0, 82), 5)
card_blocks = extract_signal_by_amplitude(smoothed_signal, 1000, (70, 78), 2)

# For each call response, decode the card and reader messages
for i, rc in enumerate(zip(reader_blocks, card_blocks)):
    reader, card = rc
    start_r, stop_r = reader
    start_c, stop_c = card

    # plot_signal(smoothed_signal[start_r: stop_c], FS, f"reader card {i}")

    # reader message block
    sig_r = smoothed_signal[start_r - 2000 : stop_r + 2000]
    message_r = miller_decode(sig_r)
    print("Reader message: ", message_r)

    # card message block
    sig_c = smoothed_signal[start_c - 2000: stop_c + 2000]
    message_c = manchester_decode(sig_c)
    print("Card bytes", message_c)
