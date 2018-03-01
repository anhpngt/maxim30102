cmake_minimum_required(VERSION 2.8.3)
project(maxim)

set(CMAKE_CXX_FLAGS "-std=c++0x -O2 ${CMAKE_CXX_FLAGS}")

include_directories(
  .
)
# find_package(OpenCV REQUIRED)
add_executable(main main.cpp maximalgorithm.h maximalgorithm.cpp)
# target_link_libraries(main ${OpenCV_LIBS})