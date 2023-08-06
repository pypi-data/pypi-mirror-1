import types
import subnetviz.format
from subnetviz.format \
    import DisplayNode, Network_DisplayNode, Unallocated_DisplayNode
from subnetviz.address_utils import *

def format_net (net, indent, file):
    """Formats net (a DisplayNode) as plaintext to file."""
    
    indent_s = " " * (indent * 2)
    if isinstance (net, Network_DisplayNode):
        print >>file, "%-50s %s" % ((indent_s +
                                     str (network_to_IPy (net.address))),
                                    net.label if net.label is not None else "")
    elif isinstance (net, Unallocated_DisplayNode):
        print >>file, "%s# unallocated" % (indent_s,)

@subnetviz.format.registered_format ("text")
def print_tree (net, file, format_net_fn = format_net):
    """Plaintext output (same format as input)."""
    
    net.offset = net.depth = 0
    subnetviz.format.annotate (net)
    
    def visit (net, level):
        format_net (net, level, file)
        for subnet in net.children:
            visit (subnet, level + 1)
    
    if net.label is None and len (net.children) > 0:
        for subnet in net.children:
            visit (subnet, 0)
    else:
        visit (net, 0)
