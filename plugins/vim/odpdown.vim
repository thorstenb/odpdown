" Vim global plugin for creating LibreOffice slides from markdown

if exists("g:loaded_odpdown")
  finish
endif
let g:loaded_odpdown = 1

let s:save_cpo = &cpo
set cpo&vim

let s:odpdown='/home/bjoern/.local/bin/odpdown'
let s:breakmaster='Discreet_25_20Dark1'
let s:contentmaster='Discreet_25_20Dark'
let s:template=$HOME . '/.vim/plugin/odpdown_data/discreet-dark.odp'
let s:highlightstyle='colorful'
let s:autofit='on'
let s:lastodp=''
let s:currentodp=''
let s:lastodp=''

function s:Update()
  let l:markdownfile=tempname()
  let s:lastodp=s:currentodp
  let s:currentodp=l:markdownfile . '.odp'
  let l:oldmakeprg=&mp
  let l:makeargs=''
  if s:autofit != 'on'
    let l:makeargs.= ' --no-autofit'
  endif
  let l:makeargs.= ' --highlight-style ' . s:highlightstyle
  if exists('s:breakmaster')
    let l:makeargs.=' --break-master ' . s:breakmaster
  endif
  if exists('s:contentmaster')
    let l:makeargs.=' --content-master ' . s:contentmaster
  endif
  let l:makeargs.=' ' . l:markdownfile . ' ' . s:template . ' ' . s:currentodp
  let &mp=s:odpdown
  execute 'write! ' . l:markdownfile
  execute 'make ' . l:makeargs
  execute 'silent !rm ' . l:markdownfile
  set mp=l:oldmakeprg
endfunction

function s:Autofit(args)
  if len(a:args) == 0
    echo 'Autofit is currently: ' . s:autofit . '.'
  else
    if a:args[0] ==? 'on' || a:args[0] ==? 'yes' || a:args[0] ==? 'active'
      let s:autofit = 'on'
    else
      let s:autofit = 'off'
    endif
    echo 'Autofit is now: ' . s:autofit . '.'
  endif
endfunction

function s:BreakMaster(args)
  if len(a:args) == 0
    echo 'The break-master has been disabled.'
    unlet s:breakmaster
  else
    let s:breakmaster=a:args[0]
    echo 'Break-master set to "' . s:breakmaster . '" now.'
  endif
endfunction

function s:ContentMaster(args)
  if len(a:args) == 0
    echo 'The content-master has been disabled.'
    unlet s:contentmaster
  else
    let s:contentmaster=a:args[0]
    echo 'Content-master set to "' . s:contentmaster . '" now.'
  endif
endfunction

function s:Example()
  if &mod
    new
  endif
  read $HOME/.vim/plugin/odpdown_data/demo-full.md
  set filetype=markdown
endfunction

function s:Highlightstyle(args)
  if len(a:args) == 0
    echo 'The current highlight style is: "' . s:highlightstyle . '".'
  else
    let s:highlightstyle=a:args[0]
    echo 'Highlight style set to "' . s:highlightstyle . '" now.'
  endif
endfunction

function s:Present()
  call s:Update()
  let l:cmd='python3 '. $HOME . '/.vim/plugin/odpdown_data/odpdownhelper.py --present --file ' . s:currentodp
  if len(s:lastodp)
    let l:cmd.=' --oldfile ' . s:lastodp
  endif
  execute 'silent ! ' . l:cmd
endfunction

function s:Settings()
  echo 'Autofit is: ' . s:autofit . '.'
  if !exists('s:breakmaster')
    echo 'The break-master has been disabled.'
  else
    echo 'The current break-master is: "' . s:breakmaster . '".'
  endif
  if !exists('s:contentmaster')
    echo 'The content-master has been disabled.'
  else
    echo 'The current content-master is: "' . s:contentmaster . '".'
  endif
  echo 'The current highlight style is: "' . s:highlightstyle . '".'
  echo 'The current template is: "' . s:template . '".'
endfunction

function s:Show()
  call s:Update()
  let l:cmd='python3 '. $HOME . '/.vim/plugin/odpdown_data/odpdownhelper.py --file ' . s:currentodp
  if len(s:lastodp)
    let l:cmd.=' --oldfile ' . s:lastodp
  endif
  execute 'silent ! ' . l:cmd
endfunction

function s:Template(args)
  if len(a:args) == 0
    echo 'The current template is: "' . s:template . '".'
  else
    let s:template=a:args[0]
    echo 'Template set to "' . s:template . '" now.'
  endif
endfunction

function s:ShowSlides(...)
  if a:0 == 0
    call s:Show()
  else
    if a:000[0] == 'autofit'
      call s:Autofit(a:000[1:])
    elseif a:000[0] == 'breakmaster'
      call s:BreakMaster(a:000[1:])
    elseif a:000[0] == 'contentmaster'
      call s:ContentMaster(a:000[1:])
    elseif a:000[0] == 'example'
      call s:Example()
    elseif a:000[0] == 'highlight'
      call s:Highlightstyle(a:000[1:])
    elseif a:000[0] == 'settings'
      call s:Settings()
    elseif a:000[0] == 'show'
      call s:Show()
    elseif a:000[0] == 'present'
      call s:Present()
    elseif a:000[0] == 'template'
      echo 'calling Template with ' . join(a:000[1:])
      call s:Template(a:000[1:])
    else
      echo 'Unkown :ShowSlides subcommand, sorry.'
    endif
  endif
endfunction

function s:Complete(ArgLead, CmdLine, Pos)
let l:completions=['autofit', 'breakmaster', 'contentmaster', 'example', 'highlight', 'settings', 'show', 'present', 'template']
if match(a:CmdLine, 'autofit') > 0
  let l:completions=['on', 'off']
endif
if match(a:CmdLine, 'highlight') > 0
  let l:completions=['default', 'emacs', 'friendly', 'colorful' ]
endif
if match(a:CmdLine, 'template') > 0
  let l:completions=glob(a:ArgLead . '*', 1, 1)
endif
if match(a:CmdLine, 'example') > 0 || match(a:CmdLine, 'settings') > 0 || match(a:CmdLine, 'show') > 0 || match(a:CmdLine, 'present') > 0 || match(a:CmdLine, 'breakmaster') > 0 || match(a:CmdLine, 'contentmaster') > 0
  let l:completions=[]
endif
return l:completions
endfunction

if !exists(":ShowSlides")
  command -complete=customlist,s:Complete -nargs=* ShowSlides :call s:ShowSlides(<f-args>)
endif
if !exists(":Odpdown")
  command -complete=customlist,s:Complete -nargs=* Odpdown :call s:ShowSlides(<f-args>)
endif

let &cpo = s:save_cpo
unlet s:save_cpo

" vim: set et sw=2 ts=2:
