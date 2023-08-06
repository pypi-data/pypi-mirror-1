

"---------------------------------------------------------------------
" initialize PDB/Vim package
function! Pdb_init()
    highlight DebugBreak guibg=darkred guifg=white ctermbg=darkred ctermfg=white
    highlight DebugStop guibg=darkgreen guifg=white ctermbg=darkgreen ctermfg=white
    sign define breakpoint text=[] linehl=DebugBreak
    sign define current text=>> linehl=DebugStop

    if !exists(":Pdb")
        command -nargs=+ Pdb    :call Pdb_command(<q-args>, v:count)
    endif

    call Pdb_comm_init()
    call s:Pdb_shortcuts()

python <<EOT
vimpdb_buffer_write(["VIM PDB init."])
EOT

endfunction

"---------------------------------------------------------------------
" PDB Exit
function! Pdb_exit()
    call Pdb_comm_deinit()
python <<EOT
vimpdb_buffer_write(["VIM PDB exit."])
EOT
endfunction


"---------------------------------------------------------------------
" initialize PDB/Vim communication
function! Pdb_comm_init()
python <<EOT
import vim
import socket
 
PDB_SERVER_ADDRESS = '127.0.0.1'
PDB_SERVER_PORT = 6666
try:
    pdb_server.close()
except:
    pass
pdb_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
EOT
endfunction

"---------------------------------------------------------------------
" deinitialize PDB/vim communication
function! Pdb_comm_deinit()
python <<EOT
try:
    pdb_server.close()
except:
    pass
EOT
endfunction


"---------------------------------------------------------------------
" send a message to the PDB server
function! Pdb_send(message)
python <<EOT
_message = vim.eval("a:message")
pdb_server.sendto(_message, (PDB_SERVER_ADDRESS, PDB_SERVER_PORT))
EOT
endfunction

"---------------------------------------------------------------------
" send a command to the PDB server
function! Pdb_command(cmd, ...)
    call Pdb_send(a:cmd)
endfunction


"---------------------------------------------------------------------
" Mappings are dependant on Leader at time of loading the macro.
function! s:Pdb_shortcuts()
    nmenu Pdb.Execution.Step :<C-U>Pdb step<CR>
    nmenu Pdb.Execution.Next :<C-U>Pdb next<CR>
    nmenu Pdb.Execution.Return :Pdb return<CR>
    nmenu Pdb.Execution.Continue :<C-U>Pdb cont<CR>
    nmenu Pdb.Execution.Quit :<C-U>Pdb q<CR>
    nmenu Pdb.Frame.Up :Pdb u<CR>
    nmenu Pdb.Frame.Down :Pdb d<CR>
    nmenu Pdb.Set\ break :call Pdb_command("b ".bufname("%").":".line("."))<CR>
    nmenu Pdb.Toggle\ break :call Pdb_command("toggle_breakpoint ".bufname("%")." ".line("."))<CR>
    nmenu Pdb.-Sep- :
    nmenu Pdb.PdbCommand :<C-U>Pdb 
    nmenu Pdb.-Sep- :
    nmenu Pdb.Start :call Pdb_init()<CR>
    nmenu Pdb.Exit :call Pdb_exit()<CR>
endfunction

"---------------------------------------------------------------------
"---------------------------------------------------------------------
"---------------------------------------------------------------------

"---------------------------------------------------------------------
" callback: pdb server wants to call init
function! Pdb_cb_init()
    call Pdb_init()
endfunction

"---------------------------------------------------------------------
" callback: pdb server wants to call exit
function! Pdb_cb_exit()
    call Pdb_exit()
endfunction

"---------------------------------------------------------------------
" callback: pdb server wants to set a sign on given file
function! Pdb_cb_sign_set(id, type, filename, lineno)
    if !bufexists(a:filename)
        execute "bad ".a:filename
    endif
    execute "sign place ".a:id." name=".a:type." line=".a:lineno." file=".a:filename
endfunction

"---------------------------------------------------------------------
" callback: pdb server wants to clear a sign on given file
function! Pdb_cb_sign_clr(id, filename, lineno)
    if !bufexists(a:filename)
        execute "bad ".a:filename
    endif
    execute "sign unplace ".a:id
endfunction

"---------------------------------------------------------------------
" callback: pdb server wants to highlight the current line
function! Pdb_cb_current_line(file, line)
    if !bufexists(a:file)
        if !filereadable(a:file)
            return
        endif
        execute "e ".a:file
    else
    execute "b ".a:file
    endif
    let s:file=a:file
    sign unplace 2
    execute "sign place 2 name=current line=".a:line." file=".a:file
    execute a:line
    :silent! foldopen!
endf


"---------------------------------------------------------------------
" callback: pdb server wants to clear a sign on given file
function! Pdb_cb_sign_clr_all()
    sign unplace *
endfunction

"---------------------------------------------------------------------
" callback: pdb server wants to show the user a message
function! Pdb_cb_message(message)
python <<EOT
_message = vim.eval("a:message")
vimpdb_buffer_write(_message)
EOT
endfunction

"---------------------------------------------------------------------
" callback: pdb server wants to show the user a error message
function! Pdb_cb_error(message)
python <<EOT
_message = vim.eval("a:message")
vimpdb_buffer_write(_message)
EOT
endfunction


python <<EOT
def vimpdb_buffer_write(message):

    if not vimpdb_buffer_exist():
        vimpdb_buffer_create()

    pdb_buffer[:] = None

    for line in message:
        pdb_buffer.append(line)
    del pdb_buffer[0]

    #from normal mode into insert mode
    y, x = vim.current.window.cursor
    if len(vim.current.line) > x + 1:
        vim.command('normal l')
        vim.command('startinsert')
    else:
        vim.command('startinsert!')

def vimpdb_buffer_create():
    global pdb_buffer
    source_buffer = vim.current.buffer.name
    vim.command('silent rightbelow 5new -PDBVim-')
    vim.command('set buftype=nofile')
    vim.command('set noswapfile')
    vim.command('set nonumber')
    vim.command('set nowrap')
    pdb_buffer = vim.current.buffer
    while True:
        vim.command('wincmd w')   #switch back window
        if source_buffer == vim.current.buffer.name:
            break

def vimpdb_buffer_close():
    vim.command('silent! bwipeout -PDBVim-')

def vimpdb_buffer_exist():
    for win in vim.windows:
        try:                 #FIXME: Error while new a unnamed buffer
            if 'PDBVim' in win.buffer.name:
                return True
        except: pass
    return False
EOT

""""""""""""""""""""""""""""""""""""
" Startup
call Pdb_init()

" vim: set ft=vim ts=4 sw=4 expandtab :
