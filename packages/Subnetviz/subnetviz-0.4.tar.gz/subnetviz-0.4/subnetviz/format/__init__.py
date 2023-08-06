import math, re
import IPy
from subnetviz.address_utils import *

class DisplayNode (object):
    def iter_breadth_first (self):
        queue = [self]
        while len (queue) > 0:
            subnet = queue.pop (0)
            queue.extend (subnet.children)
            yield subnet
    
    def height (self):
        """Returns the height of the subtree rooted at this node.  The
        result will be 1 (representing just this node) or greater."""
        
        if len (self.children) > 0:
            children_height = max ((subnet.height ()
                                    for subnet in self.children))
        else:
            children_height = 0
        return 1 + children_height


class Network_DisplayNode (DisplayNode):
    def __init__ (self, label, address):
        self.label = label
        self.address = address
        self.children = []
    
    @property
    def start (self):
        return address_lower_bound (self.address)
    
    @property
    def end (self):
        return address_upper_bound (self.address)
    
    @property
    def length (self):
        return address_count (self.address)
    
    @property
    def length_log2 (self):
        return address_count_log2 (self.address)

class Unallocated_DisplayNode (DisplayNode):
    """Represents a contiguous range of unallocated addresses.  Its
    boundaries are not restricted to fit a legal subnet block."""
    def __init__ (self, start, end):
        self.start = start
        self.end = end
    
    @property
    def label (self):
        return None
    
    @property
    def address (self):
        raise ValueError, ("%s instances do not have normal network "
                           "addresses.") % (self.__class__.__name__)
    
    @property
    def children (self):
        return []
    
    @property
    def length (self):
        return self.end - self.start + 1
    
    @property
    def length_log2 (self):
        length = self.length
        out = math.log (length, 2)
        if 2**int (out) == length:
            return int (out)
        else:
            return out

def prune_tree (net):
    """Prunes the given Network tree, removing and promoting the
    children of uninteresting nodes.  The tree is transformed from
    being composed of Network instances (a binary tree) to being
    composed to DisplayNode instances (with variable children per
    node).  The resulting tree is a tree of dictionaries, with each
    dictionary containing "label", "address", and "children" keys."""
    
    if net is None:
        return None
    out = Network_DisplayNode (net.label, net.address)
    if address_count_log2 (net.address) == 0:
        assert net.get_children () == (None, None)
    else:
        for child in net.get_children ():
            out_child = prune_tree (child)
            if out_child is not None:
                if (out_child.label is None and
                    len (out_child.children) > 0):
                    out.children.extend (out_child.children)
                else:
                    out.children.append (out_child)
    return out

def annotate (net):
    """Recursively adds information to the given Network as the final
    stage before printing.

    Preconditions:

      * "offset" and "depth" are set for net.

    Postconditions:

      * "width" is set for net and its descendants.

      * "offset" and "depth" are set for descendants of net.

      * Unallocated-region nodes are inserted into the children of net
        and the children of its descendants, as necessary.
    """

    # Insert Unallocated_DisplayNode instances.
    if len (net.children) > 0:
        net_start, net_end = address_bounds (net.address, True)
        next_subnet_start = net_end
        net_netbase, net_prefix = net.address
        net_base_addr = net_broadcast_addr = None
        if is_network_ipv4_mapped (net.address):
            net_base_addr, net_broadcast_addr = address_bounds (net.address)
        elif net_prefix == 64:
            # I don't think there really are "base addresses" with
            # IPv6, but radvd and Linux treat the first address
            # specially and give unexpected results for me, so I never
            # use them, and consider them to be reserved in the same
            # way that IPv4 base and broadcast addresses are.
            net_base_addr = address_lower_bound (net.address)
        end_i = len (net.children) - 1
        for i, subnet in reversed ([(-1, None)] + # Sentinel.
                                   list (enumerate (net.children))):
            if subnet is None:
                subnet_start, subnet_end = None, net_start
            else:
                subnet_start, subnet_end = \
                    address_bounds (subnet.address, True)
            unalloc_len = next_subnet_start - subnet_end
            assert unalloc_len >= 0
            if unalloc_len > 0:
                start, end = subnet_end, next_subnet_start - 1
                if ((i == -1 and start == end == net_base_addr) or
                    (i == end_i and start == end == net_broadcast_addr)):
                    pass
                else:
                    net.children.insert \
                        (i + 1, Unallocated_DisplayNode (start, end))
            next_subnet_start = subnet_start

    child_offset = net.offset
    for subnet in net.children:
        subnet.offset = child_offset
        subnet.depth = net.depth + 1
        annotate (subnet)
        child_offset += subnet.width
    if len (net.children) == 0:
        net.width = 1
    else:
        net.width = sum ((subnet.width for subnet in net.children))

    assert (len (net.children) == 0 or net.start <= net.children[0].start)
    assert (len (net.children) == 0 or net.children[-1].end <= net.end)
    assert all ((net.children[i - 1].end < net.children[i].start
                 for i in xrange (1, len (net.children))))

# A map from format names to functions that conform to a particular
# interface to print a Network tree.  (The interface is simply that of
# print_tree, without the "format" paramater; see its docstring.)
_print_functions = {}
def register_format (name, function):
    """Registers function as a tree-formatting function under the
    given name."""
    _print_functions[name] = function
def registered_formats ():
    """Returns the list of (name, doc) tuples for each registered tree
    format.  doc is a brief description string derived from the
    docstring of the underlying function, or None."""
    
    out = []
    for name, function in sorted (_print_functions.items ()):
        doc = None
        if hasattr (function, "__doc__") and function.__doc__ is not None:
            m = _docstring_first_para.search (function.__doc__)
            if m is not None and len (m.group (1)) > 0:
                doc = _docstring_linebreak_ws.sub (" ", m.group (1))
        out.append ((name, doc))
    return out
# FIXME: real library to do this the right way?
_docstring_first_para = re.compile (r"^[ \t]*(.*?)[ \t]*(?:\n\n|$)", re.S)
_docstring_linebreak_ws = re.compile (r"\n[ \t]*", re.S)
def registered_format (name):
    def decorator (function):
        register_format (name, function)
        return function
    return decorator
def format_exists (name):
    return _print_functions.has_key (name)

def print_tree (format, net, file):
    """Prints a DisplayNode tree (whose root is given in net) to the
    given file open for writing.
    
    format is the format to print the tree in.  The parameter may be a
    callable that conforms to the same interface as this function (but
    without the format parameter), or it may be a string naming a
    registered format."""
    
    if hasattr (format, "__call__"):
        format (net, file)
    elif format in _print_functions:
        _print_functions[format] (net, file)
    else:
        raise ValueError, "Unknown tree output format %r." % (format,)

def initialize ():
    """Performs initialization.  Should be called at the top level,
    before any functions involving output formats are called."""
    
    # We need to ensure these modules execute in order for them to
    # register their tree-printing functions.
    # 
    # FIXME: is there a way to dynamically find and load these?
    import subnetviz.format.html
    import subnetviz.format.text
