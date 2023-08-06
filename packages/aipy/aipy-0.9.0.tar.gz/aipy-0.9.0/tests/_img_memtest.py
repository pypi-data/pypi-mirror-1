#! /usr/bin/env python

import aipy._img as _img, numpy as n
import os, re

re_mem = re.compile(r'VmSize:\s*(\d+)\s', re.IGNORECASE)
def memory(pid=os.getpid()):
    data = open('/proc/%d/status' % pid).read()
    m = re_mem.search(data)
    return int(m.groups()[0])
    
uv = n.zeros((1000,1000), dtype=n.complex)
bm = n.zeros((1000,1000), dtype=n.complex)
u = n.zeros((1000,), dtype=n.float)
v = n.zeros((1000,), dtype=n.float)
w = n.zeros((1000,), dtype=n.float)
data = n.zeros((1000,), dtype=n.complex)
wgt = n.zeros((1000,), dtype=n.complex)

start_mem = memory()
cnt = 0
while True:
    _img.put(uv.copy(),bm.copy(),
        u.copy(),v.copy(),w.copy(),
        data.copy(),wgt.copy())
    if cnt % 1000 == 0: print memory() - start_mem, 'kB'
        
    
