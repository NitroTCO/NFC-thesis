import pyMSO4

import subprocess
import numpy as np
import binascii

from datetime import datetime
from time import sleep

DEFAULT_KEY = '11223344556677881122334455667788'
N = 3

now = datetime.now().strftime("%Y%m%d_%H%M%S")
log = open(f'pm3-{now}.log','a')

mso44 = pyMSO4.MSO4(trig_type=pyMSO4.MSO4EdgeTrigger)

mso44.con(ip="192.168.230.100") # Using p2p ethernet connection
mso44.ch_a_enable([False, False, False, True]) # Enable channel 1
mso44.acq.wfm_src = ['ch4'] # Set waveform source to channel 1
mso44.acq.wfm_start = 0
mso44.acq.wfm_stop = mso44.acq.horiz_record_length # Get all data points

# get sampling frequency
freq = mso44.sc.query("HORizontal:MODE:SAMPLERate?")

def generate_2tdea_key():
    return binascii.hexlify(os.urandom(16)).decode()

def run_pm3_cmd(pm3_cmd): 
    result = subprocess.run(["pm3", "-c", pm3_cmd], capture_output=True, text=True)
    log.write(result.stdout)
    print(result.stdout)

key = DEFAULT_KEY
for i in range(N):
    
    _key = generate_2tdea_key()

    run_pm3_cmd(f"hf mfdes changekey --aid 123456 -t 2tdea --key {key} --newkey {_key}")
    
    sleep(4)
    wfm = mso44.sc.query_binary_values('CURVE?', 
                                       datatype=mso44.acq.get_datatype(), 
                                       is_big_endian=mso44.acq.is_big_endian)
    
    np.savetxt(f"./{key}-{freq:.1f}MSs.trace", wfm)

    key = _key


# reset back to DEFAULT_KEY
run_pm3_cmd(f"hf mfdes changekey --aid 123456 -t 2tdea --key {key} --newkey {DEFAULT_KEY}")

mso44.dis()
