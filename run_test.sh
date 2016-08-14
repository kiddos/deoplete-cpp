#!/usr/bin/env sh

set -e

PY=python3
TEST_CODE_COMPLETION=test/test_code_complete.py
TEST_C=test/test.c
TEST_CPP=test/test.cpp
TEST_CMAKE=test/test_cmake_command.py


$PY $TEST_CODE_COMPLETION $TEST_C 11 1 c11 "printf"
$PY $TEST_CODE_COMPLETION $TEST_C 22 33 c11 "'i', TypedText"
$PY $TEST_CODE_COMPLETION $TEST_C 22 38 c11 "'i', TypedText"
$PY $TEST_CODE_COMPLETION $TEST_CPP 31 9 c++11 "test_func1"
$PY $TEST_CODE_COMPLETION $TEST_CPP 33 11 c++11 "geta"
$PY $TEST_CODE_COMPLETION $TEST_CPP 33 25 c++11 "getd"
$PY $TEST_CODE_COMPLETION $TEST_CPP 34 9 c++11 "getsize"
$PY $TEST_CODE_COMPLETION $TEST_CPP 34 19 c++11 "'width', TypedText"
$PY $TEST_CODE_COMPLETION $TEST_CPP 34 40 c++11 "'height', TypedText"

$PY  $TEST_CMAKE
