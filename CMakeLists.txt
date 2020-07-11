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

# execute_process(
#   COMMAND lsb_release -r
#   COMMAND cut -d: -f2
#   COMMAND xargs
#   COMMAND tr -d '\n'
#   OUTPUT_VARIABLE UBUNTU_VERSION)

# message(STATUS "detected ubuntu version: ${UBUNTU_VERSION}")

# download clang prebuilt
set(CLANG_BINARY "${CMAKE_BINARY_DIR}/clang.tar.xz")
set(CLANG_VERSION "10.0.0")
set(CLANG_BASE_URL "https://github.com/llvm/llvm-project/releases/download/llvmorg-${CLANG_VERSION}")
if (NOT EXISTS ${CLANG_BINARY})
  # if ("${UBUNTU_VERSION}" STREQUAL "18.04")
  if (${CMAKE_SYSTEM_NAME} STREQUAL "Linux")
    set(CLANG_FILE clang+llvm-10.0.0-x86_64-linux-gnu-ubuntu-18.04.tar.xz)
  elseif (${CMAKE_SYSTEM_NAME} STREQUAL "Darwin")
    set(CLANG_FILE clang+llvm-10.0.0-x86_64-apple-darwin.tar.xz)
  else ()
    message(FATAL_ERROR "not supported")
  endif ()

  set(CLANG_URL "${CLANG_BASE_URL}/${CLANG_FILE}")
  message(STATUS "Downloading from ${CLANG_URL}...")
  file(DOWNLOAD ${CLANG_URL} ${CLANG_BINARY} SHOW_PROGRESS)
endif ()

if (NOT EXISTS "clang")
  execute_process(
    COMMAND mkdir -p clang
    COMMAND tar xvf clang.tar.xz -C clang --strip-components=1
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR})

  # execute_process(
  #   COMMAND mv clang+llvm-9.0.0-x86_64-linux-gnu-ubuntu-${UBUNTU_VERSION} clang
  #   WORKING_DIRECTORY ${CMAKE_BINARY_DIR})
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

# clean unnecessary files
add_custom_target(clean-all
  COMMAND rm -rf ${CMAKE_BINARY_DIR}/clang.tar.xz
  COMMAND rm -rf ${CMAKE_BINARY_DIR}/clang/bin
  COMMAND rm -rf ${CMAKE_BINARY_DIR}/clang/libexec
  COMMAND rm -rf ${CMAKE_BINARY_DIR}/clang/share)
