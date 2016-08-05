#!/usr/bin/env sh

set -e

TEST_PROGRAM=test/test_code_complete.py
TEST_C=test/test.c
TEST_CPP=test/test.cpp


python $TEST_PROGRAM $TEST_C 11 1 c11 "printf"
python $TEST_PROGRAM $TEST_C 22 33 c11 "'i', TypedText"
python $TEST_PROGRAM $TEST_C 22 38 c11 "'i', TypedText"
python $TEST_PROGRAM $TEST_CPP 31 9 c++11 "test_func1"
python $TEST_PROGRAM $TEST_CPP 33 11 c++11 "geta"
python $TEST_PROGRAM $TEST_CPP 33 25 c++11 "getd"
python $TEST_PROGRAM $TEST_CPP 34 9 c++11 "getsize"
python $TEST_PROGRAM $TEST_CPP 34 19 c++11 "'width', TypedText"
python $TEST_PROGRAM $TEST_CPP 34 40 c++11 "'height', TypedText"
