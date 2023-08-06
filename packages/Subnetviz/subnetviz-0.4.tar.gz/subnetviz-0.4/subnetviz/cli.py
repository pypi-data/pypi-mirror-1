from __future__ import with_statement

import os, sys, copy
import IPy
import subnetviz.network, subnetviz.format, subnetviz.format.html
from subnetviz.address_utils import *

_DEFAULT_FORMAT = "html"

def print_usage (file):
    print >>file, \
        ("usage: %s INPUT_FILE [OUTPUT_FILE [OUTPUT_FORMAT [ROOT_NETWORK]]]" %
         (os.path.basename (sys.argv[0]),))
    print >>file, "INPUT_FILE may be '-' to denote standard input."
    print >>file, "OUTPUT_HTML defaults to '-', denoting standard output."
    print >>file, "OUTPUT_FORMAT defaults to %r." % (_DEFAULT_FORMAT,)
    print >>file, "ROOT_NETWORK defaults to :: (all IPv6 addresses), or 0.0.0.0/0 (all IPv4 addresses) when all the input addresses are IPv4 addresses.  Networks outside of ROOT_NETWORK are ignored."
    print >>file
    print >>file, subnetviz.network.input_format_description
    print >>file
    print_formats (file)

def print_formats (file):
    print >>file, "Available output formats:"
    formats = subnetviz.format.registered_formats ()
    name_width = max ((len (name) for (name, doc) in formats))
    for name, doc in formats:
        print >>file, "  %*s  %s" % (name_width, name,
                                     doc if doc is not None else "")

def main (args):
    subnetviz.format.initialize ()
    if len (args) == 0:
        print_usage (sys.stdout)
        return 1
    args = copy.copy (args)
    default_args = ["-", "-", _DEFAULT_FORMAT, None]
    if len (args) <= len (default_args):
        args += default_args[len (args):]
    else:
        print >>sys.stderr, "Too many arguments."
        print
        print_usage (sys.stdout)
        return 1
    
    opened_files = []
    in_fn, out_fn, out_format, root_network = args
    if root_network is not None:
        root_network = IPy_to_network (IPy.IP (root_network))
    if not subnetviz.format.format_exists (out_format):
        print >>sys.stderr, "No such format %r." % (out_format,)
        print_formats (sys.stderr)
        return 2
    
    with (sys.stdin if in_fn == "-"
          else open (in_fn)) as in_f:
        addrs = subnetviz.network.read_addresses (in_f)
    net_tree = subnetviz.network.network_tree (addrs, root_network)
    pruned_tree = subnetviz.format.prune_tree (net_tree)
    with (sys.stdout if out_fn == "-"
          else open (out_fn, "w")) as out_f:
        subnetviz.format.print_tree (out_format, pruned_tree, out_f)
    return 0

if __name__ == "__main__":
    sys.exit (main (sys.argv[1:]))
