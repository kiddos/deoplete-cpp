if exists("b:did_ftplugin")
  finish
endif

au BufRead,BufNewFile *.ino	setlocal filetype=arduino
