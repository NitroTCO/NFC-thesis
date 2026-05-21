import numpy as np
import matplotlib.pyplot as plt

def do_the_plotting(i, bg, j):
    plt.axhline(bg, color="black", linewidth=.5)
    plt.axhline(bg+1, color="red", linewidth=.5, linestyle="-.")
    plt.axhline(bg-1, color="red", linewidth=.5, linestyle="-.")
    plt.axvline(295, color="green", linewidth=.75, linestyle=":")
    plt.axvline(j, color="orange", linestyle=":")
    plt.plot(np.arange(0,590,1), sig[i:i+590])
    plt.show()

sig = np.loadtxt("smoothed_signal.txt")
background_level = sig[0]
print(f"number of bit periods: {len(sig)/590}")
for i in range(0, len(sig), 590):
    period = sig[i:i+590]
    for j, x in enumerate(period):
        if abs(background_level - x) > 1:
            print(f"in the {i/590}th bit period")
            do_the_plotting((i+j)+(j-590), background_level, j)
            exit(0)

