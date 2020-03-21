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

execute_process(
  COMMAND lsb_release -r
  COMMAND cut -d: -f2
  COMMAND xargs
  COMMAND tr -d '\n'
  OUTPUT_VARIABLE UBUNTU_VERSION)

message(STATUS "detected ubuntu version: ${UBUNTU_VERSION}")

# download clang prebuilt
if (NOT EXISTS "${CMAKE_BINARY_DIR}/clang.tar.xz")
  if ("${UBUNTU_VERSION}" STREQUAL "18.04")
    file(DOWNLOAD https://releases.llvm.org/9.0.0/clang+llvm-9.0.0-x86_64-linux-gnu-ubuntu-18.04.tar.xz
      "${CMAKE_BINARY_DIR}/clang.tar.xz" SHOW_PROGRESS)
  elseif ("${UBUNTU_VERSION}" STREQUAL "16.04")
    file(DOWNLOAD https://releases.llvm.org/9.0.0/clang+llvm-9.0.0-x86_64-linux-gnu-ubuntu-16.04.tar.xz
      "${CMAKE_BINARY_DIR}/clang.tar.xz" SHOW_PROGRESS)
  elseif ("${UBUNTU_VERSION}" STREQUAL "14.04")
    file(DOWNLOAD https://releases.llvm.org/9.0.0/clang+llvm-9.0.0-x86_64-linux-gnu-ubuntu-14.04.tar.xz
      "${CMAKE_BINARY_DIR}/clang.tar.xz" SHOW_PROGRESS)
  else ()
    message(FATAL_ERROR "not supported")
  endif ()
endif ()

if (NOT EXISTS "clang")
  execute_process(
    COMMAND tar xvf clang.tar.xz
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR})

  execute_process(
    COMMAND mv clang+llvm-9.0.0-x86_64-linux-gnu-ubuntu-${UBUNTU_VERSION} clang
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR})
endif ()

set(CMAKE_C_COMPILER "${CMAKE_BINARY_DIR}/clang/bin/clang")
set(CMAKE_CXX_COMPILER "${CMAKE_BINARY_DIR}/clang/bin/clang++")

include(ExternalProject)

ExternalProject_Add(googletest
  GIT_REPOSITORY    https://github.com/google/googletest.git
  GIT_TAG           master
  CMAKE_ARGS        "-DCMAKE_INSTALL_PREFIX=${CMAKE_CURRENT_BINARY_DIR}/googletest-build"
  UPDATE_COMMAND    ""
)
include_directories(${CMAKE_CURRENT_BINARY_DIR}/googletest-build/include)
set(GTEST_LIBS ${CMAKE_CURRENT_BINARY_DIR}/googletest-build/lib/libgtest.a
  ${CMAKE_CURRENT_BINARY_DIR}/googletest-build/lib/libgtest_main.a
  pthread)

# copy test files
file(COPY ${CMAKE_SOURCE_DIR}/test DESTINATION ${CMAKE_CURRENT_BINARY_DIR})
enable_testing()

# source build
add_subdirectory(src)
