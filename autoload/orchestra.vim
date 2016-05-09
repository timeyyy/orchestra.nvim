
function! orchestra#prelude()
    " Can now use our rmeote plugin functio from within vimrc
    runtime! plugin/rplugin.vim
endfunction

function! orchestra#set_tune(theme)
    " Python3 function
    call OrchestraSetTheme(a:theme)
endfunction
