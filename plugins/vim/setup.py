#!/usr/bin/env python3

import os
import os.path
import shutil
import subprocess
import sys

def install_vim_plugin(install_scripts):
    src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..')
    vim_plugin_dir = os.path.join(os.environ['HOME'], '.vim', 'plugin')
    vim_plugin_data_dir = os.path.join(vim_plugin_dir,'odpdown_data')
    vim_doc_dir = os.path.join(os.environ['HOME'], '.vim', 'doc')
    os.makedirs(vim_plugin_data_dir, exist_ok=True)
    os.makedirs(vim_doc_dir, exist_ok=True)
    for demofile in ['demo-advanced.md', 'demo-basics.md', 'demo-full.md', 'discreet-dark.odp']:
        shutil.copyfile(os.path.join(src_dir, 'demo', demofile), os.path.join(vim_plugin_data_dir, demofile))
    with open(os.path.join(src_dir,'plugins', 'vim', 'odpdown.vim'), 'r') as script_template:
        with open(os.path.join(vim_plugin_dir, 'odpdown.vim'), 'w') as scriptfile:
            for line in script_template:
                scriptfile.write(line.replace('***ODPDOWNPATH***', os.path.join(install_scripts, 'odpdown')))
    shutil.copyfile(os.path.join(src_dir, 'plugins', 'vim', 'odpdown.txt'), os.path.join(vim_doc_dir, 'odpdown.txt'))
    shutil.copyfile(os.path.join(src_dir, 'plugins', 'vim', 'odpdownhelper.py'), os.path.join(vim_plugin_data_dir, 'odpdownhelper.py'))
    subprocess.call(['vim', '-s', os.path.join(src_dir, 'plugins', 'vim', 'update-help.vim')])
    #print(src_dir, vim_plugin_dir, install_scripts)

install_vim_plugin(sys.argv[1])
