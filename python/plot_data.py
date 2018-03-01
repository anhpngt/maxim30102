import matplotlib.pyplot as plt
import numpy as np
import csv

if __name__ == '__main__':
  red_file = csv.reader(open('../RT_RED.txt'), delimiter='\n')
  ir_file = csv.reader(open('../RT_IR.txt'), delimiter='\n')
  red_input = []
  ir_input = []
  for ir_str, red_str in zip(ir_file, red_file):
    red_input.append(int(float(red_str[0])))
    ir_input.append(int(float(ir_str[0])))

  plt.figure(1)
  plt.plot(range(len(red_input)), red_input)
  plt.plot(range(len(ir_input)), ir_input)
  plt.show()