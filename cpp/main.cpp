#include <fstream>
#include <iostream>
#include <string>
#include <vector>

#include <maximalgorithm.h>

using namespace std;
int c = 0;
int main(int argc, char** argv)
{
  std::ifstream ifs_ir, ifs_red;
  ifs_ir.open("../../RT_IR.txt");
  ifs_red.open("../../RT_RED.txt");

  std::string ir_str, red_str;
  std::vector<int> ir_data, red_data;
  while(getline(ifs_ir, ir_str) && getline(ifs_red, red_str))
  {
    ir_data.push_back(std::stoi(ir_str));
    red_data.push_back(std::stoi(red_str));
  }
  std::cout << "Data size: " << ir_data.size() << std::endl;
  // Start processing
  int32_t n_ir_buffer_length = 100; // input data length
  int32_t n_spo2, n_heart_rate; 
  int8_t ch_spo2_valid, ch_hr_valid; 
  uint32_t aun_ir_buffer[100], aun_red_buffer[100];

  // Initial fill
  for(int i = 0; i < 100; i++)
  {
    aun_ir_buffer[i] = ir_data[i];
    aun_red_buffer[i] = red_data[i];
  }
  uint data_pos = 100, data_pos_end = ir_data.size() - 25;
  while(data_pos <= data_pos_end)
  {
    // if(c > 5)
    //   return(0);
    // for(int i = 0; i < 100; i++)
    // {
    //   cout << aun_ir_buffer[i] << " " << flush;
    // }
    // cout << endl;
    maxim_heart_rate_and_oxygen_saturation(aun_ir_buffer, n_ir_buffer_length, aun_red_buffer, &n_spo2, &ch_spo2_valid, &n_heart_rate, &ch_hr_valid); 
    if(ch_spo2_valid) printf("SPO2: %d,", n_spo2);
    else printf("SPO2: nan, ");
    if(ch_hr_valid) printf("HR: %d\n", n_heart_rate);
    else printf("HR: nan\n");

    for(int i = 0; i < 75; i++)
    {
      aun_ir_buffer[i] = aun_ir_buffer[i + 25];
      aun_red_buffer[i] = aun_red_buffer[i + 25];
    }
    for(int i = 75; i < 100; i++)
    {
      aun_ir_buffer[i] = ir_data[data_pos];
      aun_red_buffer[i] = red_data[data_pos];
      data_pos++;
    }
    c++;
  }
  return(0);
}