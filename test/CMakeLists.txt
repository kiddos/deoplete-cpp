########################### GTEST
# Enable ExternalProject CMake module
include(ExternalProject)

# Set default ExternalProject root directory
set_directory_properties(PROPERTIES EP_PREFIX ${CMAKE_BINARY_DIR}/third_party)

# Add gtest
# http://stackoverflow.com/questions/9689183/cmake-googletest
ExternalProject_Add(
    googletest
    URL https://github.com/google/googletest/archive/release-1.8.1.zip
    TIMEOUT 10
    # Disable install step
    INSTALL_COMMAND ""
    # Wrap download, configure and build steps in a script to log output
    LOG_DOWNLOAD ON
    LOG_CONFIGURE ON
    LOG_BUILD ON)

# Specify include dir
ExternalProject_Get_Property(googletest source_dir)
set(GTEST_INCLUDE_DIR ${source_dir}/include)

# Library
ExternalProject_Get_Property(googletest binary_dir)
set(GTEST_LIBRARY_PATH ${binary_dir}/googlemock/gtest/${CMAKE_FIND_LIBRARY_PREFIXES}gtest.a)
set(GTEST_LIBRARY gtest)
add_library(${GTEST_LIBRARY} UNKNOWN IMPORTED)
set_property(TARGET ${GTEST_LIBRARY} PROPERTY IMPORTED_LOCATION
             ${GTEST_LIBRARY_PATH})
add_dependencies(${GTEST_LIBRARY} googletest)


include_directories("${CMAKE_SOURCE_DIR}/src")
include_directories("${CMAKE_BINARY_DIR}/clang/include")
link_directories("${CMAKE_BINARY_DIR}/clang/lib")

include_directories(${GTEST_INCLUDE_DIRS})

file(GLOB TEST_FILES sample* dependency*)
file(COPY ${TEST_FILES} DESTINATION "${CMAKE_BINARY_DIR}/test")

add_executable(test_clang_completer test_clang_completer.cc)
add_dependencies(test_clang_completer ${GTEST_LIBRARY})
target_link_libraries(test_clang_completer
  clang_completer ${GTEST_LIBRARY} pthread)
