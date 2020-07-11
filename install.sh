#!/usr/bin/env sh

if [ ! -d build ]; then
  mkdir build
fi

cd build
cmake ..
make
make install
make clean-all
cd ..
