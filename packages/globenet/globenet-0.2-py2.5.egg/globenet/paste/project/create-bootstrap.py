#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import virtualenv, textwrap
output = virtualenv.create_bootstrap_script(textwrap.dedent("""
import os, subprocess
def after_install(options, home_dir):
    subprocess.call([join(home_dir, 'bin', 'easy_install'),'--always-unzip','globenet'])
"""))
f = open('bootstrap.py', 'w')
f.write(output)
f.close()


