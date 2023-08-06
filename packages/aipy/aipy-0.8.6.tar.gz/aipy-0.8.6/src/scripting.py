"""
Module containing utilities (like parsing of certain command-line arguments) 
for writing scripts.
"""

import miriad, ant, sim, fit, src, numpy as n, re

def add_standard_options(optparser, ant=False, pol=False, chan=False, 
        loc=False, loc2=False, src=False, dec=False, cmap=False, max=False,
        drng=False):
    """Add standard command-line options to an optparse.OptionParser() on an 
    opt in basis (i.e. specify =True for each option to be added)."""
    if ant: optparser.add_option ('-a', '--ant', dest='ant', default='cross',
         help='Select ants/baselines to include.  Examples: all (all baselines) auto (of active baselines, only i=j) cross (only i!=j) 0,1,2 (any baseline involving listed ants) 0_2,0_3 (only listed baselines) "(0,1)_(2,3)" (same as 0_2,0_3,1_2,2_3. Quates help bash deal with parentheses) "(-0,1)_(2,-3)" (exclude 0_2,0_3,1_3 include 1_2).')
    if pol: optparser.add_option('-p', '--pol', dest='pol', 
        help='Choose polarization (xx, yy, xy, yx) to include.')
    if chan: optparser.add_option('-c', '--chan', dest='chan', default='all',
        help='Select channels (taken after any delay/fringe transforms) to include.  Options are "all", "<chan1 #>,..." (a list of channels), or "<chan1 #>_<chan2 #>" (a range of channels).  Default is "all".')
    if loc: optparser.add_option('-l', '--loc', dest='loc', 
        help='Use specified <loc>.py for location-specific calibration.')
    elif loc2: optparser.add_option('-l', '--loc', dest='loc', action='append',
        help='Use specified <loc>.py for location-specific calibration.  Can intersperse locations with UV files to use different calibrations for different files.')
    if src: optparser.add_option('-s', '--src', dest='src',
        help='Phase centers/source catalog entries to use.  Options are "all", "<src_name1>,...", or "<ra XX[:XX:xx]>_<dec XX[:XX:xx]>".')
    if dec:
        optparser.add_option('-x', '--decimate', dest='decimate', 
            default=1, type='int',
            help='Use only every Nth integration.  Default is 1.')
        optparser.add_option('--dphs', dest='decphs', 
            default=0, type='int',
            help='Offset to use when decimating (i.e. start counting integrations at this number for the purpose of decimation).  Default is 0.')
    if cmap: optparser.add_option('--cmap', dest='cmap', default='jet',
        help='Colormap for plotting.  Can be gist_earth, gist_heat, gist_stern, gist_yarg, hot, cool, gray, bone, spectral, copper, jet to name a few.  For a more complete list, see pylab.cm.datad.keys().  Default is jet.')
    if max: optparser.add_option( '--max',dest='max',type='float',default=None,
    help='Manually set the maximum color level, in units matching plotting mode.  Default max(data).')
    if drng:
        optparser.add_option('--drng', dest='drng', type='float', default=None,
    help="Dynamic range in color of image, in units matching plotting mode.  Default max(data)-min(data).")

def _strarg_to_range(strarg):
    """Split command-line lists/ranges into a list of numbers."""
    strarg = strarg.split(',')
    return [map(float, option.split('_')) for option in strarg]

ant_re = r'(\(((-?\d+,?)+)\)|-?\d+)'
bl_re = '(^(%s_%s|%s),?)' % (ant_re, ant_re, ant_re)
def parse_ants(ant_str, nants):
    """Generate list of (baseline, inlude) tuples based on parsing of the
    string associated with the 'ants' command-line option."""
    rv,cnt = [], 0
    while cnt < len(ant_str):
        m = re.search(bl_re, ant_str[cnt:])
        if m is None:
            if ant_str[cnt:].startswith('all'): rv = []
            elif ant_str[cnt:].startswith('auto'): rv.append(('auto',1))
            elif ant_str[cnt:].startswith('cross'): rv.append(('auto',0))
            else: raise ValueError('Unparsible ant argument "%s"' % ant_str)
            c = ant_str[cnt:].find(',')
            if c >= 0: cnt += c + 1
            else: cnt = len(ant_str)
        else:
            m = m.groups()
            cnt += len(m[0])
            if m[2] is None:
                ais = [m[8]]
                ajs = range(nants)
            else:
                if m[3] is None: ais = [m[2]]
                else: ais = m[3].split(',')
                if m[6] is None: ajs = [m[5]]
                else: ajs = m[6].split(',')
            for i in ais:
                for j in ajs:
                    if type(i) == str and i.startswith('-') or \
                            type(j) == str and j.startswith('-'):
                        include = 0
                    else: include = 1
                    bl = miriad.ij2bl(abs(int(i)),abs(int(j)))
                    rv.append((bl,include))
    return rv

def uv_selector(uv, ants, pol_str):
    """Call uv.select with appropriate options based on string argument for
    antennas (can be 'all', 'auto', 'cross', '0,1,2', or '0_1,0_2') and
    string for polarization ('xx','yy','xy','yx')."""
    if type(ants) == str: ants = parse_ants(ants, uv['nants'])
    for bl,include in ants:
        if bl == 'auto': uv.select('auto', 0, 0, include=include)
        else:
            i,j = miriad.bl2ij(bl)
            uv.select('antennae', i, j, include=include)
    try: polopt = miriad.str2pol[pol_str]
    except(KeyError): raise ValueError('--pol argument invalid or absent')
    uv.select('polarization', polopt, 0)

def parse_chans(chan_str, nchan):
    """Return array of active channels based on number of channels and
    string argument for chans (can be 'all', '20_30', or '55,56,57')."""
    if chan_str.startswith('all'): chans = n.arange(nchan)
    else:
        chanopt = _strarg_to_range(chan_str)
        if len(chanopt[0]) != 1:
            chanopt = [n.arange(x,y, dtype=n.int) for x,y in chanopt]
        chans = n.concatenate(chanopt)
    return chans.astype(n.int)

def parse_srcs(src_str):
    """Return (src_list,flux_cutoff) based on string argument for src.
    Can be "all", "<src_name1>,...", or "<ra XX[:XX:xx]>_<dec XX[:XX:xx]>"."""
    if src_str.startswith('all'): return None, None
    try:
        cutoff = float(src_str)
        return None, cutoff
    except(ValueError): pass
    src_opt = src_str.split(',')
    if len(src_opt) == 1:
        src_opt = src_opt[0].split('_')
        if len(src_opt) == 1: return src_opt, None
        ra,dec = src_opt
        s = fit.RadioFixedBody(ra, dec, name=src_str)
        return [s], None
    else:
        return src_opt, None

def files_to_locs(locations, uvfiles, sysargv):
    import optparse
    o = optparse.OptionParser(); add_standard_options(o, loc2=True)
    locs = {}
    pos = [sysargv.index(uv) for uv in uvfiles]
    curloc = locations[0]
    for i in range(len(pos)):
        locs[curloc] = locs.get(curloc, []) + [sysargv[pos[i]]]
        if i < len(pos)-1 and pos[i+1] - pos[i] > 1:
            opts,args = o.parse_args(sysargv[pos[i]+1:pos[i+1]])
            if not opts.loc is None:
                if curloc is None:
                    locs[opts.loc[-1]] = locs[None]
                    del(locs[None])
                curloc = opts.loc[-1]
    return locs

