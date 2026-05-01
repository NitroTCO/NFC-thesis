import pyMSO4

mso44 = pyMSO4.MSO4(trig_type=pyMSO4.MSO4EdgeTrigger)

mso44.con(ip="192.168.230.100") # Using p2p ethernet connection
mso44.ch_a_enable([False, False, False, True]) # Enable channel 1
mso44.acq.wfm_src = ['ch4'] # Set waveform source to channel 1
mso44.acq.wfm_start = 0
mso44.acq.wfm_stop = mso44.acq.horiz_record_length # Get all data points



wfm = mso44.sc.query_binary_values('CURVE?', datatype=mso44.acq.get_datatype(), is_big_endian=mso44.acq.is_big_endian)

import matplotlib.pyplot as plt

plt.rcParams["figure.figsize"] = (12,4)
plt.plot(wfm, linewidth=0.8)

plt.savefig("./waveform.png")

#print(wfm)

import numpy as np
import datetime

wave = np.array(wfm)
np.savetxt(f"trace-{datetime.datetime.now()}-62.5Mss-12.5Mpts.txt", wave)

mso44.dis()
