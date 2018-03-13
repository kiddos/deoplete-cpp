if exists('g:loaded_deoplete_cpp')
  finish
endif
let g:loaded_deoplete_cpp = 1

let g:deoplete#sources#cpp#clang_version='5.0'

" flags
let g:deoplete#sources#cpp#cflags =
\   get(g:, 'deoplete#sources#cpp#cflags',
\   ['-std=c89'])

let g:deoplete#sources#cpp#cppflags =
\   get(g:, 'deoplete#sources#cpp#cppflags',
\   ['-std=c++98'])

let g:deoplete#sources#cpp#objcflags =
\   get(g:, 'deoplete#sources#cpp#objcflags',
\   ['-Wall', '-Wextra'])

let g:deoplete#sources#cpp#objcppflags =
\   get(g:, 'deoplete#sources#cpp#objcppflags',
\   ['-Wall', '-Wextra'])

" include path
let g:deoplete#sources#cpp#c_include_path =
\   get(g:, 'deoplete#sources#cpp#c_include_path',
\   ['/usr/local/include', '.'])

let g:deoplete#sources#cpp#cpp_include_path =
\   get(g:, 'deoplete#sources#cpp#cpp_include_path',
\   ['/usr/local/include', '.'])

let g:deoplete#sources#cpp#objc_include_path =
\   get(g:, 'deoplete#sources#cpp#objc_include_path',
\   ['/usr/local/include', '/usr/include/GNUstep'])

let g:deoplete#sources#cpp#objcpp_include_path =
\   get(g:, 'deoplete#sources#cpp#objcpp_include_path',
\   ['/usr/local/include', '/usr/include/GNUstep'])

" arudino ide path
let g:deoplete#sources#cpp#arduino_path =
\   get(g:, 'deoplete#sources#cpp#arduino_path',
\   '/usr/local/share/arduino')

" cuda path
let g:deoplete#sources#cpp#cuda_path =
\   get(g:, 'deoplete#sources#cpp#cuda_path',
\   ['/usr/local/cuda/include'])

" should display detail
let g:deoplete#sources#cpp#get_detail =
\   get(g:, 'deoplete#sources#cpp#get_detail',
\   1)

" complete paren
let g:deoplete#sources#cpp#complete_paren =
\   get(g:, 'deoplete#sources#cpp#complete_paren',
\   0)
