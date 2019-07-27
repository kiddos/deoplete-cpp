if exists("g:loaded_deoplete_cpp")
  finish
endif
let g:loaded_deoplete_cpp = 1

" c
let g:deoplete#sources#c#standard =
\   get(g:, "deoplete#sources#c#standard", 99)

let g:deoplete#sources#c#definitions =
\   get(g:, "deoplete#sources#c#definitions", ['DEBUG'])

let g:deoplete#sources#c#include_paths =
\   get(g:, "deoplete#sources#c#include_paths", [
\   "/usr/local/include",
\   ])

let g:deoplete#sources#c#enable_kernel_dev =
\   get(g:, "deoplete#sources#c#enable_kernel_dev", 0)

let g:deoplete#sources#c#kernel_root =
\   get(g:, "deoplete#sources#c#kernel_root",
\   '')

let g:deoplete#sources#c#enable_platformio_dev =
\   get(g:, "deoplete#sources#c#enable_platformio_dev", 1)

let g:deoplete#sources#c#platformio_root =
\   get(g:, "deoplete#c#arduino#platformio_root",
\   '~/.platformio')


" cpp
let g:deoplete#sources#cpp#enable_bazel_includes =
\   get(g:, "deoplete#sources#cpp#enable_bazel_includes", 1)

let g:deoplete#sources#cpp#standard =
\   get(g:, "deoplete#sources#cpp#standard", 14)

let g:deoplete#sources#cpp#definitions =
\   get(g:, "deoplete#sources#cpp#definitions", ['DEBUG'])

let g:deoplete#sources#cpp#include_paths =
\   get(g:, "deoplete#sources#cpp#include_paths", [
\   "/usr/local/include",
\   ])

let g:deoplete#sources#cpp#enable_qt_dev =
\   get(g:, "deoplete#sources#cpp#enable_qt_dev", 1)

let g:deoplete#sources#cpp#qt_root =
\   get(g:, "deoplete#sources#cpp#qt_root",
\   '/usr/include/x86_64-linux-gnu/qt5')

let g:deoplete#sources#cpp#enable_ros_dev =
\   get(g:, "deoplete#sources#cpp#enable_ros_dev", 1)

let g:deoplete#sources#cpp#ros_root =
\   get(g:, "deoplete#sources#cpp#ros_root",
\   '/opt/ros/melodic')

let g:deoplete#sources#cpp#ros_user_ws =
\   get(g:, "deoplete#sources#cpp#ros_user_ws",
\   '~/catkin_melodic')

let g:deoplete#sources#cpp#enable_cuda_dev =
\   get(g:, "deoplete#sources#cpp#enable_cuda_dev", 1)

let g:deoplete#sources#cpp#cuda_root =
\   get(g:, "deoplete#sources#cpp#cuda_root",
\   '/usr/local/cuda')


" objc/objc++
let g:deoplete#sources#objc#definitions =
\   get(g:, "deoplete#sources#objc#definitions", ['DEBUG'])

let g:deoplete#sources#objc#include_paths =
\   get(g:, "deoplete#sources#objc#include_paths", [
\   "/usr/local/include",
\   "/usr/include/GNUstep",
\   "/usr/include/GNUstep/Foundation",
\   "/usr/include/GNUstep/gnustep",
\   "/usr/include/GNUstep/GNUstepBase",
\   ])


" arduino
let g:deoplete#sources#arduino#definitions =
\   get(g:, "deoplete#sources#arduino#definitions", ['DEBUG'])

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

let g:deoplete#sources#arduino#enable_platformio_dev =
\   get(g:, "deoplete#sources#arduino#enable_platformio_dev", 1)

let g:deoplete#sources#arduino#platformio_root =
\   get(g:, "deoplete#sources#arduino#platformio_root",
\   '~/.platformio')
