deoplete-cpp
============
[![Build Status](https://travis-ci.org/kiddos/deoplete-cpp.svg?branch=master)](https://travis-ci.org/kiddos/deoplete-cpp)

c, c++, objc, objc++, arduino, cmake source for [deoplete.nvim](https://github.com/Shougo/deoplete.nvim)

##Installation
I made this source using libclang. I am using version 3.8 on my labtop.
- install libclang
- install python3 port libclang

  * clang 3.6

  ``` shell
  sudo apt-get install libclang-3.6-dev
  sudo pip3 install libclang-py3==3.6
  ```

  * clang 3.8

  ``` shell
  sudo apt-get install libclang-3.8-dev
  sudo pip3 install libclang-py3==3.8
  ```

##Support
* cmake (you need to install cmake to for this to work)
* arduino (you need to have the [Arduino IDE](https://www.arduino.cc/en/Main/Software))

##Options
* set the compilation flags

``` vim
let g:deoplete#sources#cpp#cflags = ['-std=c89', '-Wall', '-Wextra']
let g:deoplete#sources#cpp#cppflags = ['-std=c++11', '-Wall', '-Wextra']
let g:deoplete#sources#cpp#objcflags = ['-Wall', '-Wextra']
let g:deoplete#sources#cpp#objcppflags = ['-Wall', '-Wextra']
```
* set the compilation include flags

``` vim
let g:deoplete#sources#cpp#c_include_path = ['/usr/local/include', '.']
let g:deoplete#sources#cpp#cpp_include_path = ['/usr/local/include', '.']
let g:deoplete#sources#cpp#objc_include_path = ['/usr/local/include', '/usr/include/GNUstep', '.']
let g:deoplete#sources#cpp#objcpp_include_path = ['/usr/local/include', '/usr/include/GNUstep', '.']
```
* set where you install arduino

I have my Arduino IDE folder in /usr/local/share

``` vim
let g:deoplete#sources#cpp#arduino_path = '/usr/local/share/arduino'
```
