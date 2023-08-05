"""
Package :O
"""

version = 0, 2, "pre"
version_str = lambda: "%d.%02d-%s" % version
__version__ = "$Id: __init__.py 20 2007-07-27 17:08:58Z toxik $"

class pymktorrentException(BaseException): pass
class TorrentFormatError(pymktorrentException): pass

prefixes = {
    "iec": (1024,
        ("kibi", "mebi", "gibi", "tebi", "pebi", "exbi", "zebi", "yobi"),
        ("Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi", "Yi")),
    "si": (1000,
        ("kilo", "mega", "giga", "tera", "peta", "exa", "zetta", "yotta"),
        ("k", "M", "G", "T", "P", "E", "Z", "Y"))
}

def bytes_to_human(bytes, short=True, iec_prefixes=True):
    if iec_prefixes:
        prefix_type = "iec"
    else:
        prefix_type = "si"
    divisor, long_prefixes, short_prefixes = prefixes[prefix_type]
    i = 0
    while bytes >= divisor:
        bytes /= float(divisor)
        i += 1
    prefix = ""
    if i:
        i -= 1
        if short:
            prefix = short_prefixes[i]
        else:
            prefix = long_prefixes[i]
        prefix = " " + prefix
    return "%.2f%s" % (bytes, prefix)
