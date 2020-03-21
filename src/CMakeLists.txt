include_directories("${CMAKE_BINARY_DIR}/clang/include")
link_directories("${CMAKE_BINARY_DIR}/clang/lib")

file(GLOB SOURCE_FILES *.cc *.h)
add_library(clang_completer ${SOURCE_FILES})
target_link_libraries(clang_completer clang)
target_compile_definitions(clang_completer
  PUBLIC "-DCLANG_INCLUDE_DIR=\"${CMAKE_BINARY_DIR}/clang/lib/clang/9.0.0/include\"")

## SWIG3
find_package(SWIG)
find_package(PythonLibs 3)

message(STATUS "Using PythonLibs ${PYTHONLIBS_VERSION_STRING}")
include(${SWIG_USE_FILE})
include_directories(${PYTHON_INCLUDE_DIR})
include_directories(${CMAKE_CURRENT_SOURCE_DIR})

set(CMAKE_SWIG_FLAGS "")
set_source_files_properties(clang_completer.i PROPERTIES CPLUSPLUS ON)
swig_add_library(clang_completer LANGUAGE python SOURCES clang_completer.i ${SOURCE_FILES})
swig_link_libraries(clang_completer ${PYTHON_LIBRARY} clang)

target_compile_definitions(_clang_completer
  PUBLIC "-DCLANG_INCLUDE_DIR=\"${CMAKE_BINARY_DIR}/clang/lib/clang/9.0.0/include\"")

install(TARGETS _clang_completer
  DESTINATION "${CMAKE_BINARY_DIR}/../rplugin/python3/deoplete/")
install(FILES "${CMAKE_BINARY_DIR}/src/clang_completer.py"
  DESTINATION "${CMAKE_BINARY_DIR}/../rplugin/python3/deoplete/")
