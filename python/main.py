# INO/C++ REFERENCE: https://github.com/MaximIntegratedRefDesTeam/RD117_ARDUINO
from __future__ import print_function
import csv
import math
import numpy as np
import algorithm
import maxim

if __name__ == '__main__':
  # Input
  c = 0
  red_file = csv.reader(open('../RT_RED.txt'), delimiter='\n')
  ir_file = csv.reader(open('../RT_IR.txt'), delimiter='\n')
  red_input = []
  ir_input = []
  for ir_str, red_str in zip(ir_file, red_file):
    red_input.append(int(float(red_str[0])))
    ir_input.append(int(float(ir_str[0])))

  # Start processing, copy this loop over to your rasp
  FS = 25 # number of samples recorded per sec, change this to your real value!
  n_ir_buffer_length = FS * 4
  n_batch_buffer_length = int(n_ir_buffer_length / 4)

  # Get the first full buffer, this will need to be replaced with a for loop of continuous of reading
  # Replace with a loop of readings
  aun_ir_buffer = ir_input[:n_ir_buffer_length]
  aun_red_buffer = red_input[:n_ir_buffer_length]
  data_pos = n_ir_buffer_length

  un_min = min(aun_red_buffer)
  un_max = max(aun_red_buffer)
  un_prev_data = aun_red_buffer[n_ir_buffer_length - 1]

  while(True):
    # if c > 5:
      # break;
    un_min = 0x3FFFF
    un_max = 0
    # Do calculation, if the any value is invalid, a NaN is returned
    # spo2, hr = algorithm.calculate(np.array(aun_ir_buffer), np.array(aun_red_buffer), FS)
    spo2, hr = maxim.calculate(aun_ir_buffer, aun_red_buffer)
    print('SPO2: {} / Heart rate: {}'.format(spo2, hr))

    # Get the next batch of samples for next loop calculation
    # This is the dumping
    aun_red_buffer[:-n_batch_buffer_length] = aun_red_buffer[n_batch_buffer_length:]
    aun_ir_buffer[:-n_batch_buffer_length] = aun_ir_buffer[n_batch_buffer_length:]

    # Find min max
    un_min = min(aun_red_buffer)
    un_max = max(aun_red_buffer)

    # Get the next batch
    # Replace with a loop
    aun_red_buffer[-n_batch_buffer_length:] = red_input[data_pos:data_pos + n_batch_buffer_length]
    aun_ir_buffer[-n_batch_buffer_length:] = ir_input[data_pos:data_pos + n_batch_buffer_length]
    data_pos += n_batch_buffer_length
    if(data_pos > len(red_input) - 100):
      print('Warning: No data left')
      break
    c += 1
    # Brightness calculation. TODO
  
