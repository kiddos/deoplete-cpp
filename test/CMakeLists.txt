find_package(GTest)
if (GTEST_FOUND)
  include_directories("${CMAKE_SOURCE_DIR}/src")
  include_directories("${CMAKE_BINARY_DIR}/clang/include")
  link_directories("${CMAKE_BINARY_DIR}/clang/lib")

  include_directories(${GTEST_INCLUDE_DIRS})

  file(GLOB TEST_FILES sample* dependency*)
  file(COPY ${TEST_FILES} DESTINATION "${CMAKE_BINARY_DIR}/test")

  add_executable(test_clang_completer test_clang_completer.cc)
  target_link_libraries(test_clang_completer
    clang_completer ${GTEST_BOTH_LIBRARIES} pthread)

  add_test(test_clang_engine COMMAND ./bin/test_clang_completer)
endif ()

