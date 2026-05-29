import numpy as np
import matplotlib.pyplot as plt

def do_the_plotting(i, bg, j, nr_bit_periods):
    plt.axhline(bg, color="black", linewidth=.5)
    plt.axhline(bg+1, color="red", linewidth=.5, linestyle="-.")
    plt.axhline(bg-1, color="red", linewidth=.5, linestyle="-.")
    for x in range(nr_bit_periods):
        plt.axvline(j+590*x, color="orange", linestyle=":")
        plt.axvline(295+590*x, color="green", linewidth=.75, linestyle=":")
    plt.plot(np.arange(0,590*nr_bit_periods,1), sig[i:i+590*nr_bit_periods])
    plt.axvline(590*nr_bit_periods, color="orange", linestyle=":")
    plt.show()

sig = np.loadtxt("smoothed_signal.txt")
background_level = sig[0]
print(f"number of bit periods: {len(sig)/590}")
acc = 0
for i in range(0, len(sig), 590):
    period = sig[i:i+590]
    for j, x in enumerate(period):
        acc += 1
        if abs(x - background_level) > 1:
            print(f"the {acc}th value in the {i/590}th bit period")
            do_the_plotting(i, background_level, j, 1)
            do_the_plotting(i+j, background_level, 0, 10)
            exit(0)

