if exists('g:loaded_deoplete_cpp')
  finish
endif
let g:loaded_deoplete_cpp = 1

let g:deoplete#sources#cpp#flags =
\   get(g:, 'deoplete#sources#cpp#flags',
\   ['-std=c++11', '-Wall', '-Wextra'])

let g:deoplete#sources#cpp#include_path =
\   get(g:, 'deoplete#sources#cpp#include_path',
\   ['/usr/local', '.'])

let g:deoplete#sources#cpp#arduino_path =
\   get(g:, 'deoplete#sources#cpp#arduino_path',
\   '/usr/local/share/arduino')
