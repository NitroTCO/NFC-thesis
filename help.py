#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt


bg = 72.25
sig = np.loadtxt("test.txt")
xs = np.arange(0, len(sig), 1)
plt.axhline(bg, color="black", linewidth=.5)
plt.axhline(bg + 1.5, color="red", linewidth=.5, linestyle="-.")
plt.axhline(bg - 1.5, color="red", linewidth=.5, linestyle="-.")
for i in range(0, len(sig)+590, 590): #bitlines
    plt.axvline(i, color="green", linestyle=":")
for i in range(295, len(sig), 590): # mid bitlines
    plt.axvline(i, color="orange", linestyle=":", linewidth=.75)
plt.plot(xs, sig)
plt.show()

