import numpy as np

# MAX_BRIGHTNESS = 255
MA4_SIZE = 4

uch_spo2_table =   [95, 95, 95, 96, 96, 96, 97, 97, 97, 97, 97, 98, 98, 98, 98, 98, 99, 99, 99, 99, 
                    99, 99, 99, 99, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 
                    100, 100, 100, 100, 99, 99, 99, 99, 99, 99, 99, 99, 98, 98, 98, 98, 98, 98, 97, 97, 
                    97, 97, 96, 96, 96, 96, 95, 95, 95, 94, 94, 94, 93, 93, 93, 92, 92, 92, 91, 91, 
                    90, 90, 89, 89, 89, 88, 88, 87, 87, 86, 86, 85, 85, 84, 84, 83, 82, 82, 81, 81, 
                    80, 80, 79, 78, 78, 77, 76, 76, 75, 74, 74, 73, 72, 72, 71, 70, 69, 69, 68, 67, 
                    66, 66, 65, 64, 63, 62, 62, 61, 60, 59, 58, 57, 56, 56, 55, 54, 53, 52, 51, 50, 
                    49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 31, 30, 29, 
                    28, 27, 26, 25, 23, 22, 21, 20, 19, 17, 16, 15, 14, 12, 11, 10, 9, 7, 6, 5, 
                    3, 2, 1]


# def calculate(pun_ir_buffer, n_ir_buffer_length, pun_red_buffer, pn_spo2,pch_spo2_valid, pn_heart_rate, pch_hr_valid):
def calculate(pun_ir_buffer, pun_red_buffer, FS=25):
  BUFFER_SIZE = FS * 4
  # output var holders
  pn_spo2 = 0
  pn_heart_rate = 0
  
  # calculates DC mean and subtract DC from ir
  un_ir_mean = int(np.mean(pun_ir_buffer))

  # remove DC and invert signal so that we can use peak detector as valley detector
  an_x = (-1*(pun_ir_buffer - un_ir_mean)).astype(np.int32)
      
  # 4 pt Moving Average
  for k in range(BUFFER_SIZE - MA4_SIZE):
    an_x[k] = (an_x[k] + an_x[k+1] + an_x[k+2] + an_x[k+3]) / int(4)

  # calculate threshold
  n_th1 = int(np.mean(an_x))
  # min allowed
  if n_th1 < 30:
    n_th1 = 30

  # max allowed
  if n_th1 > 60:
    n_th1 = 60

  # an_ir_valley_locs = [0] * 15
  # since we flipped signal, we use peak detector as valley detector
  an_ir_valley_locs = maximFindPeaks(an_x, n_th1, 4, 15) # (input, peak_min_height, peaks_min_distance, max_peak_num)
  n_npks = len(an_ir_valley_locs)
  n_peak_interval_sum = 0
  if n_npks >= 2:
    for k in range(1, n_npks):
      n_peak_interval_sum += an_ir_valley_locs[k] - an_ir_valley_locs[k-1]
    n_peak_interval_sum = int(n_peak_interval_sum / (n_npks-1))
    pn_heart_rate = (int)((FS * 60) / n_peak_interval_sum)
  else:
    pn_heart_rate = float('nan') # unable to calculate because # of peaks are too small

  # load raw value again for SPO2 calculation : RED(=y) and IR(=X)
  an_x = pun_ir_buffer
  an_y = pun_red_buffer

  # find precise min near an_ir_valley_locs
  n_exact_ir_valley_locs_count = n_npks

  # using exact_ir_valley_locs , find ir-red DC and ir-red AC for SPO2 calibration an_ratio
  # finding AC/DC maximum of raw
  for k in range(n_exact_ir_valley_locs_count):
    if an_ir_valley_locs[k] > BUFFER_SIZE:
      pn_spo2 = float('nan') # do not use SPO2 since valley loc is out of range
      return pn_spo2, pn_heart_rate

  # find max between two valley locations
  # and use an_ratio betwen AC compoent of Ir & Red and DC compoent of Ir & Red for SPO2
  n_y_dc_max_idx = 0
  n_x_dc_max_idx = 0
  an_ratio = []
  n_i_ratio_count = 0
  for k in range(n_exact_ir_valley_locs_count - 1):
    n_y_dc_max = -16777216
    n_x_dc_max = -16777216
    if an_ir_valley_locs[k+1] - an_ir_valley_locs[k] > 3:
      for i in range(an_ir_valley_locs[k], an_ir_valley_locs[k+1]):
        if an_x[i] > n_x_dc_max:
          n_x_dc_max = an_x[i]
          n_x_dc_max_idx = i
        if (an_y[i] > n_y_dc_max):
          n_y_dc_max = an_y[i]
          n_y_dc_max_idx = i

      # Remove DC component from IR and RED raw
      n_y_ac = (an_y[an_ir_valley_locs[k+1]] - an_y[an_ir_valley_locs[k]]) * (n_y_dc_max_idx - an_ir_valley_locs[k]) # red
      n_y_ac =  int(an_y[an_ir_valley_locs[k]] + n_y_ac / (an_ir_valley_locs[k+1] - an_ir_valley_locs[k]))
      n_y_ac =  an_y[n_y_dc_max_idx] - n_y_ac # subracting linear DC compoenents from raw

      n_x_ac = (an_x[an_ir_valley_locs[k+1]] - an_x[an_ir_valley_locs[k]]) * (n_x_dc_max_idx - an_ir_valley_locs[k]) # ir
      n_x_ac =  int(an_x[an_ir_valley_locs[k]] + n_x_ac / (an_ir_valley_locs[k+1] - an_ir_valley_locs[k]))
      n_x_ac =  an_x[n_y_dc_max_idx] - n_x_ac # subracting linear DC compoenents from raw
      # print('n_ac: {}, {}'.format(n_y_ac, n_x_ac))
      n_nume = int((n_y_ac * n_x_dc_max) / 128) # prepare X100 to preserve floating value
      n_denom = int((n_x_ac * n_y_dc_max) / 128)

      if (n_denom > 0 and n_i_ratio_count < 5 and n_nume != 0):
        an_ratio.append(int((n_nume * 100) / n_denom)) # formular is ( n_y_ac *n _x_dc_max) / ( n_x_ac *n_y_dc_max) ;
        n_i_ratio_count += 1

  ## exit if empty findings
  if len(an_ratio) == 0:
    pn_spo2 = float('nan')
    return pn_spo2, pn_heart_rate
  # choose median value since PPG signal may varies from beat to beat
  maximSortAscend(an_ratio)
  # if len(an_ratio) != n_i_ratio_count: # sanity checks
  #   print 'WARN: an_ratio length ({}) != n_i_ratio_count ({})'.format(len(an_ratio), n_i_ratio_count)
  n_middle_idx = int(n_i_ratio_count / 2)

  n_ratio_average = 0
  if n_middle_idx > 1:
    n_ratio_average = int((an_ratio[n_middle_idx-1] + an_ratio[n_middle_idx]) / 2) # use median
  else:
    n_ratio_average = int(an_ratio[n_middle_idx])

  if n_ratio_average > 2 and n_ratio_average < 184:
    pn_spo2 = uch_spo2_table[n_ratio_average]
    # n_spo2_calc = uch_spo2_table[n_ratio_average]
    # pn_spo2 = n_spo2_calc
    # float_SPO2 =  -45.060*n_ratio_average* n_ratio_average/10000 + 30.354 *n_ratio_average/100 + 94.845 # for comparison with table
  else:
    pn_spo2 = float('nan') # do not use SPO2 since signal an_ratio is out of range
  # print('.. SPO2: {}'.format(pn_spo2))
  return pn_spo2, pn_heart_rate
        
# Find peaks: Find at most MAX_NUM peaks above MIN_HEIGHT separated by at least MIN_DISTANCE
# def maxim_find_peaks( pn_locs, n_npks, pn_x, n_size, n_min_height, n_min_distance, n_max_num ):
def maximFindPeaks(pn_x, n_min_height, n_min_distance, n_max_num):
  pn_locs = maximFindPeaksAboveMinHeight(pn_x, n_min_height)
  pn_locs = maximRemoveClosePeaks(pn_locs, pn_x, n_min_distance)
  return pn_locs[:n_max_num]

# Find peaks above n_min_height
# def maxim_peaks_above_min_height( pn_locs, n_npks, pn_x, n_size, n_min_height ):
def maximFindPeaksAboveMinHeight(pn_x, n_min_height):
  i = 1
  n_size = len(pn_x)
  n_width = 0
  n_npks = 0
  pn_locs = []
  while (i < n_size - 1):
    # if len(pn_locs) != n_npks: # sanity check
    #   print 'WARN: {} != {} in maximFindPeaksAboveMinHeight'.format(len(pn_locs), n_npks)
    if pn_x[i] > n_min_height and pn_x[i] > pn_x[i - 1]:              # find left edge of potential peaks
      n_width = 1
      while(i + n_width < n_size and pn_x[i] == pn_x[i + n_width]):   # find flat peaks
        n_width = n_width + 1
      if i + n_width >= 100:
        n_width = 99 - i
      if pn_x[i] > pn_x[i + n_width] and n_npks < 15:                 # find right edge of peaks
        pn_locs.append(i)
        n_npks += 1
        i += n_width + 1                                              # for flat peaks, peak location is left edge
      else:
        i += n_width
    else:
      i += 1
  return pn_locs

# Remove peaks: Remove peaks separated by less than MIN_DISTANCE
# def maxim_remove_close_peaks(pn_locs, pn_npks, pn_x, n_min_distance):
def maximRemoveClosePeaks(pn_locs, pn_x, n_min_distance):
  pn_npks = len(pn_locs)

  # Order peaks from large to small
  # maxim_sort_indices_descend(pn_x, pn_locs, pn_npks)
  maximSortIndicesDescend(pn_x, pn_locs)

  i = -1
  while i < pn_npks:
    n_old_npks = pn_npks
    pn_npks = i + 1
    for j in range(i + 1, n_old_npks):
      # lag-zero peak of autocorr is at index -1
      n_dist = pn_locs[j] - (-1 if i == -1 else pn_locs[i])
      if n_dist > n_min_distance or n_dist < -n_min_distance:
        pn_locs[pn_npks] = pn_locs[j]
        pn_npks += 1
    i += 1

  pn_locs = pn_locs[:pn_npks]

  # Resort indices int32_to ascending order
  maximSortAscend(pn_locs)
  return pn_locs

# Sort array: Sort array in ascending order (insertion sort algorithm)
# def maxim_sort_ascend(pn_x, n_size):
def maximSortAscend(pn_x):
  i = 0
  j = 0
  n_temp = 0
  for i in range(1, len(pn_x)):
    n_temp = pn_x[i]
    j = i
    while j > 0 and n_temp < pn_x[j-1]:
      pn_x[j] = pn_x[j-1]
      j = j - 1
    pn_x[j] = n_temp

# Sort indices: Sort indices according to descending order (insertion sort algorithm)      
def maximSortIndicesDescend(pn_x, pn_locs):
  j = 0
  n_temp = 0
  for i in range(1, len(pn_locs)):
    n_temp = pn_locs[i]
    j = i
    while j > 0 and pn_x[n_temp] > pn_x[pn_locs[j-1]]:
      pn_locs[j] = pn_locs[j-1]
      j = j - 1
    pn_locs[j] = n_temp