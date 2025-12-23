cmake_minimum_required(VERSION 3.16)

include_directories(.)

file(GLOB_RECURSE SRCS *.cc)

add_executable(uPIMulator ${SRCS})

find_package(OpenMP)
if(OpenMP_CXX_FOUND)
    target_link_libraries(uPIMulator PUBLIC OpenMP::OpenMP_CXX)
endif()
