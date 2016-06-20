if exists('g:loaded_deoplete_cpp')
  finish
endif
let g:loaded_deoplete_cpp = 1

let g:deoplete#sources#cpp#cflags =
\   get(g:, 'deoplete#sources#cpp#flags',
\   ['-std=c11', '-Wall', '-Wextra'])

let g:deoplete#sources#cpp#cppflags =
\   get(g:, 'deoplete#sources#cpp#flags',
\   ['-std=c++11', '-Wall', '-Wextra'])

let g:deoplete#sources#cpp#include_path =
\   get(g:, 'deoplete#sources#cpp#include_path',
\   ['/usr/local', '.'])

let g:deoplete#sources#cpp#arduino_path =
\   get(g:, 'deoplete#sources#cpp#arduino_path',
\   '/usr/local/share/arduino')

let g:deoplete#sources#cpp#get_detail =
\   get(g:, 'deoplete#sources#cpp#get_detail',
\   1)
