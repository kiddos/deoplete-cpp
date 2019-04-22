deoplete-cpp
============
[![Build Status](https://travis-ci.org/kiddos/deoplete-cpp.svg?branch=master)](https://travis-ci.org/kiddos/deoplete-cpp)

c, c++, objc, objc++, arduino, cmake source for [deoplete.nvim](https://github.com/Shougo/deoplete.nvim)

## Installation

run the installation script

```shell
./install.sh
```

## Support

* cmake (you need to install cmake to for this to work)
* arduino (you need to have [PlatformIO](https://platformio.org/))

## Options

### C

* Set the standard (default 99)

  ```vim
  let g:deoplete#sources#c#standard = 90
  ```

* Set compile definitions (default is ['-DDEBUG'])

  ```vim
  let g:deoplete#sources#c#definitions = ['-DDEBUG']
  ```

* Set include path (default is ['/usr/local/include'])

  ```vim
  let g:deoplete#sources#c#include_paths = ['/usr/local/include']
  ```

* Set enable kernel development (default is 0)

  ```vim
  let g:deoplete#sources#c#enable_kernel_dev = 1
  ```

to enable include directory for kernel development

make sure the `g:deoplete#sources#c#kernel_root` variable is also set

* Set kernel root

  ```vim
  let g:deoplete#sources#c#kernel_root = '/usr/src/linux-headers-4.4.0-116'
  ```

* Set enable platformio development (default is 1)

  ```vim
  let g:deoplete#sources#c#enable_platformio_dev = 0
  ```

* Set platformio root (default is '~/.platformio')

  ```vim
  let g:deoplete#sources#c#platformio_root = '~/.platformio'
  ```

### CPP

* Set CPP standard (default is 14)

  ```vim
  let g:deoplete#sources#cpp#standard = 11
  ```

* Set CPP compile definitions (default is ['-DDEBUG'])

  ```vim
  let g:deoplete#sources#cpp#definitions = ['-DDEBUG']
  ```

* Set CPP include paths

  ```vim
  let g:deoplete#sources#cpp#include_paths = []
  ```

the defaults are

```vim
let g:deoplete#sources#cpp#include_paths =
\   get(g:, "deoplete#sources#cpp#include_paths", [
\   "/usr/local/include",
\   ".",
\   'src',
\   "build",
\   "include",
\   "third_party",
\   'lib',
\   "..",
\   "../src",
\   "../include",
\   "../build",
\   '../lib',
\   "../third_party",
\   "../../src",
\   "../../include",
\   '../../lib',
\   "../../third_party"
\   ])
```

* Set enable qt development (default is 1)

  ```vim
  let g:deoplete#sources#cpp#enable_qt_dev = 0
  ```

* Set qt root (default is '/usr/include/x86_64-linux-gnu/qt5')

  ```vim
  let g:deoplete#sources#cpp#qt_root = '/usr/include/x86_64-linux-gnu/qt5'
  ```

* Set enable ros development (default is 1)

  ```vim
  let g:deoplete#sources#cpp#enable_ros_dev = 0
  ```

* Set ros root (default is '/opt/ros/melodic')

  ```vim
  let g:deoplete#sources#cpp#ros_root = '/opt/ros/kinetic'
  ```

* Set ros user workspace (default is '~/catkin_melodic')

  ```vim
  let g:deoplete#sources#cpp#ros_user_ws = '~/catkin_kinetic'
  ```

### objc/objc++

* Set objc/objc++ compile definitions (default is ['-DDEBUG'])

  ```vim
  let g:deoplete#sources#objc#definitions = ['-DDEBUG']
  ```

* Set include path

  ```vim
  let g:deoplete#sources#objc#include_paths = ['/usr/local/include']
  ```

the default is

```vim
let g:deoplete#sources#objc#include_paths =
\   get(g:, "deoplete#sources#objc#include_paths", [
\   "/usr/local/include",
\   "/usr/include/GNUstep",
\   "/usr/include/GNUstep/Foundation",
\   "/usr/include/GNUstep/gnustep",
\   "/usr/include/GNUstep/GNUstepBase",
\   ])
```


### arduino

* Set arduino compile definitions (default is ['-DDEBUG'])

  ```vim
  let g:deoplete#sources#arduino#definitions = ['-DDEBUG']
  ```

* Set arduino include path

  ```
  let g:deoplete#sources#arduino#include_paths = ['/usr/local/include']
  ```

the default is

```vim
let g:deoplete#sources#arduino#include_paths =
\   get(g:, "deoplete#sources#arduino#include_paths", [
\   ".",
\   'src',
\   "build",
\   "include",
\   "third_party",
\   'lib',
\   "..",
\   "../src",
\   "../include",
\   "../build",
\   '../lib',
\   "../third_party",
\   "../../src",
\   "../../include",
\   '../../lib',
\   "../../third_party"
\   ])
```

* Set enable platformio development (default is 1)

  ```vim
  let g:deoplete#sources#arduino#enable_platformio_dev = 0
  ```

* Set platformio root directory (default is '~/.platformio')

  ```vim
  let g:deoplete#sources#arduino#platformio_root = '~/.platformio'
  ```
