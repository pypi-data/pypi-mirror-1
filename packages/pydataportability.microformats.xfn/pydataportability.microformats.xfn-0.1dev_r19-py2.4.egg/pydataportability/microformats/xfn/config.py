# list of the known values for XFN grouped according to http://www.gmpg.org/xfn/11
XFN_TAGS = {
    'friendship'    : set(('contact','acquaintance','friend',)),
    'physical'      : set(('met',)),
    'professional'  : set(('co-worker','colleague',)),
    'geographical'  : set(('co-resident','neighbour',)),
    'family'        : set(('child','parent','sibling','spouse','kin',)),
    'romantic'      : set(('muse','crush','date','sweetheart',)),
    'identity'      : set(('me',))
}

# all tags in one flat list
FLAT_XFN_TAGS = set(reduce(lambda x,y: x|y,[item for item in XFN_TAGS.values()]))
