#!/usr/bin/env python

import os

info = os.uname()
opsys = info[0].lower()
arch = info[4].lower()
if len(arch) >= 4 and arch[0] == 'i' and arch[2:4] == '86':
    arch = 'i386'
print '_' + opsys + '_' + arch

