deoplete-cpp
============

c, c++, objc, objc++, arduino, cmake source for [deoplete.nvim](https://github.com/Shougo/deoplete.nvim)

##Installation
I made this source using libclang. I am using version 3.6 on my labtop.
- install libclang
- install python3 port libclang

``` shell
sudo apt-get install libclang-3.6-dev
sudo pip3 install libclang==3.6
```

##Support
* cmake (you need to install cmake to for this to work)
* arduino (you need to have the [Arduino IDE](https://www.arduino.cc/en/Main/Software))

##Options
* set the compilation flags

``` vim
let g:deoplete#sources#cpp#cflags = ['-std=c11', '-Wall', '-Wextra']
let g:deoplete#sources#cpp#cppflags = ['-std=c++11', '-Wall', '-Wextra']
```
* set the compilation include flags

``` vim
let g:deoplete#sources#cpp#include_path = ['/usr/local', '.']
```
* set where you install arduino

I have my Arduino IDE folder in /usr/local/share

``` vim
let g:deoplete#sources#cpp#arduino_path = '/usr/local/share/arduino'
```
