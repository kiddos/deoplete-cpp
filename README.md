deoplete-cpp
============

c, c++, objc, objc++, arduino source for [deoplete.nvim](https://github.com/Shougo/deoplete.nvim)

##Installation
I made this source using libclang. I am using version 3.6 on my labtop.
- install libclang
- install python3 port libclang

``` shell
sudo apt-get install libclang-3.6-dev
sudo pip3 install libclang==3.6
```

##Support
This source also support arduino if you specify where you install your arduino

##Options
* set the compilation flags

``` vim
let g:deoplete#sources#cpp#flags = ['-std=c++11', '-Wall', '-Wextra']
```
* set the compilation flags

``` vim
let g:deoplete#sources#cpp#include_path = ['/usr/local', '.']
```
* set where you install arduino

I have my arduino folder in /usr/local/share/arduino

``` vim
let g:deoplete#sources#cpp#arduino_path = '/usr/local/share/arduino'
```
