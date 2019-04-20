cmake_minimum_required(VERSION 3.0)
project(clang_code_complete)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -Wno-sign-compare")
set(CMAKE_CXX_FLAGS_DEBUG "-g -O0")
set(CMAKE_CXX_FLAGS_RELEASE "-O3")
set(BUILD_SHARED_LIBS ON)

set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

if (NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Debug)
endif ()

if (NOT EXISTS "${CMAKE_BINARY_DIR}/clang.tar.xz")
  file(DOWNLOAD http://releases.llvm.org/8.0.0/clang+llvm-8.0.0-x86_64-linux-gnu-ubuntu-18.04.tar.xz
    "${CMAKE_BINARY_DIR}/clang.tar.xz" SHOW_PROGRESS)

  execute_process(
    COMMAND tar xvf clang.tar.xz
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR})

  execute_process(
    COMMAND mv clang+llvm-8.0.0-x86_64-linux-gnu-ubuntu-18.04
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR})
endif ()

set(CMAKE_C_COMPILER "${CMAKE_BINARY_DIR}/clang/bin/clang")
set(CMAKE_CXX_COMPILER "${CMAKE_BINARY_DIR}/clang/bin/clang++")

add_subdirectory(src)
enable_testing()
add_subdirectory(test)
