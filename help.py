import numpy as np
import matplotlib.pyplot as plt


bg = 72.25
sig = np.loadtxt("test.txt")
xs = np.arange(0, len(sig), 1)
plt.axhline(bg, color="black", linewidth=.5)
plt.axhline(bg + 1, color="red", linewidth=.5, linestyle="-.")
plt.axhline(bg - 1, color="red", linewidth=.5, linestyle="-.")
plt.axvline(len(sig)//2, color="green", linestyle=":")
plt.plot(xs, sig)
plt.show()

