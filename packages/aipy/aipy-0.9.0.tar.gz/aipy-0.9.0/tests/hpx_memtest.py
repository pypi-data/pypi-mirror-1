#! /usr/bin/env python

import aipy, sys, numpy as n

uv = aipy.miriad.UV(sys.argv[-1])
aa = aipy.loc.get_aa('pgb564', uv['sdf'], uv['sfreq'], uv['nchan'])
print aa.ants[0].beam.afreqs[60]
print aa.ants[0].beam.afreqs[180]
aa.set_jultime(2454564.0)
del(uv)

src = aipy.ant.RadioFixedBody('0', '0')
src.compute(aa)
top = aipy.coord.azalt2top((src.az, src.alt))
top = [aipy.healpix.mk_arr(c, dtype=n.double) for c in top]

h = aipy.healpix.HealpixMap(nside=32)

cnt = 0
while True:
    uv = aipy.miriad.UV(sys.argv[-1])
    for i in range(1000):
        px = h.crd2px(*top, **{'interpolate':1})
        #px = h.crd2px(*top, **{'interpolate':0})
        cnt +=1
    print cnt
