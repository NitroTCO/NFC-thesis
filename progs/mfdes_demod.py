import numpy as np
import matplotlib.pyplot as plt

from scipy.signal import hilbert, butter, filtfilt, lfilter

from sklearn.cluster import KMeans

FS = 62.5e6 # Hz 
BIT_PERIOD = 9.44e-6

def filter_trace(sig, fs, low_bp=10e3, high_bp=20e6, carrier_freq=13.56e6,
                 lowpass_cutoff=150e3, baseline_cutoff=500, highpass_cutoff=100):
    # Bandpass between 10.00MHz and 20.00MHz
    b, a = butter(5, [low_bp/(fs/2), high_bp/(fs/2)], btype='band')
    filtered = filtfilt(b, a, sig)

    # Carrier removal (demodulate)
    t = np.arange(len(filtered)) / fs
    baseband = filtered * np.exp(-1j * 2 * np.pi * carrier_freq * t)

    # Baseline removal (low-frequency drift)
    b, a = butter(2, baseline_cutoff/(fs/2), btype='low')
    baseline = filtfilt(b, a, np.real(baseband))
    baseband = baseband - baseline

    # High-pass filter for slow variations (>10ms)
    b, a = butter(2, highpass_cutoff/(fs/2), btype='high')
    baseband = filtfilt(b, a, baseband)

    # Remove DC
    baseband = baseband - np.mean(baseband)

    # Envelope
    env = np.abs(baseband)

    # Low-pass (~150 kHz for 106 kbps)
    b, a = butter(5, lowpass_cutoff/(fs/2))
    env = filtfilt(b, a, env)

    env = env - np.median(env)

    return env


def estimate_fc(signal, fs):
    spectrum = np.fft.fft(signal)
    freqs = np.fft.fftfreq(len(signal), 1/fs)
    return abs(freqs[np.argmax(np.abs(spectrum))])


def plot_spectrum(signal, fs, title):
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
    plt.savefig(f"{title}-signal-fft.png")
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
def extract_signal_by_amplitude(sig, step = 1000, bandpass = (0,90), threshold = .3):
    signal_indices = []
    b_min, b_max = bandpass

    for i in range(0, len(sig) - step, step):
        window = sig[i : i + step]
        window_max = np.max(window)
        window_min = np.min(window)

        # print(i, window_min, window_max, abs(b_min - window_min) < threshold and abs(b_max - window_max) < threshold)
        if abs(b_min - window_min) < threshold and abs(b_max - window_max) < threshold:
            signal_indices.append(i)

    blocks = []
    start_b = signal_indices[0]
    for j in range(1, len(signal_indices)):
        signal_indices[j] 

        if signal_indices[j] - signal_indices[j-1] > (step * 2):
            blocks.append((start_b, (signal_indices[j-1] + step)))
            start_b = signal_indices[j]

    return blocks


def extract_signal_clusters(signal, step = 6000):
    cinder_blocks = []

    # create window differences of signal.
    window_diffs = []
    for i in range(0, len(signal) - step, step):
        window = signal[i : i + step]

        window_max = np.max(window)
        window_min = np.min(window)

        window_diff = window_max - window_min
        
        window_diffs.append([window_diff])

    # cluster differences
    kmeans = KMeans(n_clusters=3).fit(window_diffs)

    centers = [(i, c) for i,c in enumerate(kmeans.cluster_centers_)]
    centers.sort(key=lambda x: -x[1])

    # print(centers)
    # remove noise cluster
    centers = centers[:-1]

    cinder_blocks = []
    for i, c in centers:
        indices = np.where(kmeans.labels_ == i)[0]
        # print(indices)

        # merge blocks together
        blocks = []
        start_b = indices[0]
        for j in range(1, len(indices)):

            if indices[j] != indices[j-1] + 1:
                blocks.append((start_b*step, ((indices[j-1])*step) + step))
                start_b = indices[j]

        cinder_blocks.append((i, c, blocks))

    return cinder_blocks


def miller_decode(sig):
    T = np.arange(len(sig)) / FS

    flank_i = index = next((i for i, x in enumerate(sig) if x < 0.5), -1)
    sig = sig[flank_i:]
    T = T[flank_i:]

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

    bits = []
    for line in half_lines:


        line_index = next((i for i, x in enumerate(T) if x > line), -1)
        before_offset = next((i for i, x in enumerate(T) if x > line - (BIT_PERIOD/2)), -1)
        after_offset = next((i for i, x in enumerate(T) if x > line + (BIT_PERIOD/2)), -1)


        before = np.mean(sig[before_offset:line_index])
        after = np.mean(sig[line_index:after_offset])

        if abs(before - after) > 0.1:
            if before > after:
                bits.append(1)
                continue

            bits.append(0)
            continue

        if bits[-1] == 1:
            bits.append(0)
            continue
        else:
            break

    byte = bits_to_hex(bits[1:])
    
    if byte:
        return byte
    else:
        return bits


def manchester_decode(sig):
    sample_period = 1.0 / FS
    T = np.arange(len(sig)) / FS  # µs

    bits = []

    # Advance to the first flank
    flank_i = index = next((i for i, x in enumerate(sig) if x > ((max(sig)+ min(sig)) / 2)), -1)
    sig = sig[flank_i:]

    # plot_signal(sig, FS, f"card debug {flank_i}")

    # Set set lines
    bit_lines = []
    bit_lines.append(T[0] + (BIT_PERIOD/2))

    acc = 0
    for i in range(len(sig)):
        acc += sample_period

        if(acc > BIT_PERIOD):
            bit_lines.append(T[i] + (BIT_PERIOD/2))
            acc = 0

    # Decode
    for i, bit_line in enumerate(bit_lines):
        
        bit_line_i = index = next((i for i, x in enumerate(T) if x > bit_line), -1)

        before = np.mean(sig[bit_line_i-50:bit_line_i])
        after = np.mean(sig[bit_line_i:bit_line_i+50])

        # stop if no signal
        if(abs(before - after) < 0.01): 
            break

        bits.append(1 if before > after else 0)

    # print(bits)
    return bits_to_hex(bits[1:])


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


def print_communication(signal, title):
    analytic_signal = hilbert(signal)
    amplitude_envelope = np.abs(analytic_signal)

    b, a = butter(4, 2e6 / (FS / 2), btype='low')
    signal_s = lfilter(b, a, amplitude_envelope)
    signal_s = signal_s[8000000:-5500000]

    signal_n = (signal_s - signal_s.min()) / (signal_s.max() - signal_s.min())
    
    plot_signal(signal_n, FS, title)

    signal_blocks = extract_signal_clusters(signal_s)

    card = small = min(signal_blocks, key=lambda x: x[1])
    reader = large = max(signal_blocks, key=lambda x: x[1])

    _, _, card_blocks = card
    _, _, reader_blocks = reader

    # For each call response, decode the card and reader messages
    T = np.arange(len(signal_n)) / FS  # µs
    for i, rc in enumerate(zip(reader_blocks, card_blocks)):
        f= open(f"data/{title}.txt", 'a')
        reader, card = rc
        start_r, stop_r = reader
        start_c, stop_c = card

        plot_signal(signal_n[start_r: stop_c], FS, f"{title}-rc {i}")

        # reader message block
        sig_r = signal_n[start_r - 2000 : stop_r + 2000]
        message_r = miller_decode(sig_r)

        print(f"[{T[start_r]:.4f}] R:", message_r)
        # f.write(f"[{T[start_r]:.4f}], R: {", ".join(map(str, message_r))} \n")

        # card message block
        sig_c = signal_n[start_c - 500: stop_c + 1000]
        message_c = manchester_decode(sig_c)

        print(f"[{T[start_c]:.4f}] C:", message_c)
        # f.write(f"[{T[start_c]:.4f}], C: {", ".join(map(str, message_c))} \n")

    return


###                               ###
#--------------MAIN-----------------#
###                               ###
import glob, re

traces = glob.glob("./waveform-traces/*") 
print(traces)

for trace in traces:
    # get spaces and index
    # auth_block, t_flankA, t_flank0 = 

    title = re.findall(r"(?<=/waveform-traces/)([^/]+)(?=\.)", trace)[0]
    print(title, "file:", trace)

    print_communication(np.loadtxt(trace), title)

