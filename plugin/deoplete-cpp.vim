if exists("g:loaded_deoplete_cpp")
  finish
endif
let g:loaded_deoplete_cpp = 1

let g:deoplete#sources#cpp#clang_version =
\   get(g:, "deoplete#sources#cpp#clang_version", "6.0")


" flags
let g:deoplete#sources#cpp#cflags =
\   get(g:, "deoplete#sources#cpp#cflags",
\   ["-std=c89"])

let g:deoplete#sources#cpp#cppflags =
\   get(g:, "deoplete#sources#cpp#cppflags",
\   ["-std=c++11"])

let g:deoplete#sources#cpp#objcflags =
\   get(g:, "deoplete#sources#cpp#objcflags",
\   ["-Wall", "-Wextra"])

let g:deoplete#sources#cpp#objcppflags =
\   get(g:, "deoplete#sources#cpp#objcppflags",
\   ["-Wall", "-Wextra"])

" include path
let g:deoplete#sources#cpp#c_include_path =
\   get(g:, "deoplete#sources#cpp#c_include_path",
\   ["/usr/local/include", '.'])

let g:deoplete#sources#cpp#cpp_include_path =
\   get(g:, "deoplete#sources#cpp#cpp_include_path",
\   ["/usr/local/include", "."])

let g:deoplete#sources#cpp#objc_include_path =
\   get(g:, "deoplete#sources#cpp#objc_include_path",
\   ["/usr/local/include", "/usr/include/GNUstep"])

let g:deoplete#sources#cpp#objcpp_include_path =
\   get(g:, "deoplete#sources#cpp#objcpp_include_path",
\   ["/usr/local/include", "/usr/include/GNUstep"])

" cuda path
let g:deoplete#sources#cpp#cuda_path =
\   get(g:, "deoplete#sources#cpp#cuda_path",
\   ["/usr/local/cuda/include"])

" complete function and template
let g:deoplete#sources#cpp#full_completion =
\   get(g:, "deoplete#sources#cpp#full_completion", 0)
