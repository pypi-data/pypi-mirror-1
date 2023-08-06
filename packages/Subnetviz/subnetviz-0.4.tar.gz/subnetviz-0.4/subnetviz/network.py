import types
import IPy
from subnetviz.address_utils import *

input_format_description = \
"""Each line of the input file should contain a network address.  An
optional label may follow the address, delimited with linear
whitespace.

A network address is the base address and the network prefix length,
separated by a slash (e.g. "172.16.0.0/12" or "2002::/16".).  IPv4 and
IPv6 addresses are supported, but mixing them doesn't make sense.

A network address may appear only once.  The order of networks does
not matter.  Leading and following whitespace is stripped.  Blank
lines and lines starting with a pound sign are ignored."""

def read_addresses (file):
    """Given a file open for text reading, returns a list of
    (network_address, label) tuples.
    
    See subnetviz.network.input_format_description (a string)."""
    
    out = []
    for line in file:
        line = line.strip ()
        if line.startswith ("#"):
            continue
        fields = line.strip ().split (None, 1)
        if len (fields) == 0:
            continue
        elif len (fields) == 1:
            fields.append (None)
        addr_s, label = fields
        out.append ((IPy_to_network (IPy.IP (addr_s)), label))
    return out

def network_tree (labelled_addrs, root_addr = None):
    """Creates a Network tree representing the given iterable of
    (network_address, label) tuples.  Returns the root Network
    instance."""
    
    only_include = root_addr if root_addr is not None else (0, 0)
    out = Network ((0, 0))
    seen = set ()
    for address, label in labelled_addrs:
        if not is_network_in_network (address, only_include):
            continue
        if address in seen:
            raise ValueError, \
                "%s appears more than once." % (network_to_IPy (address),)
        seen.add (address)
        net = out.find (address)
        net.label = label
    if root_addr is None:
        if len (seen) > 0 and all ((is_network_ipv4_mapped (addr)
                                    for addr in seen)):
            out = out.find (ipv4_net)
    else:
        out = out.find (root_addr)
    return out

class Network (object):
    """Represents an IP subnet, containing the network address, a
    string label, and up to two child subnets.
    
    Each child subnet may either be None (meaning that nothing is
    present), or another Network instance initially sharing the same
    network bits as this Network.  Children Networks must have one
    additional bit--that is, its prefix length will be one greater
    than this Network.  That additional bit equals the child's index
    into the sequence of children of this Network."""
    
    # FIXME: it might be faster and/or simpler to not include the
    # address: a path through a tree to a particular Network instance
    # from its root is in fact the address of the Network--the network
    # address is the sequence of child-indices chosen, and the prefix
    # length is the length of that sequences of indices.  So, the path
    # [1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1] equals 172.16.0.0/12.  I
    # have my doubts about IPy performance and correctness, so maybe I
    # should just use it for parsing.
    def __init__ (self, address, label = None):
        self._address = address
        self._label = label
        self._children = [None, None]
    
    def __repr__ (self):
        out = self.__class__.__name__
        out += "("
        out += repr (self.address)
        if self.label is not None:
            out += ", " + repr (self.label)
        out += ")"
        return out
    
    def __str__ (self):
        if self.label is None:
            return str (network_to_IPy (self.address))
        else:
            return str (self.label)
    
    def __unicode__ (self):
        if self.label is None:
            return unicode (network_to_IPy (self.address))
        else:
            return unicode (self.label)
    
    @property
    def address (self):
        return self._address
    
    def _get_label (self):
        return self._label
    def _set_label (self, new_label):
        if not isinstance (new_label, (basestring, types.NoneType)):
            raise TypeError, "New label must be a string or None."
        self._label = new_label
    label = property (_get_label, _set_label)
    
    def get_children (self):
        """Returns a sequence of the children of this Network.  See
        the class docstring for what constitutes a child."""
        return tuple (self._children)
    def get_child (self, index):
        """Returns the child of this Network at the given index.  See
        the class docstring for what constitutes a child."""
        return self._children[index]
    def set_child (self, index, subnet):
        """Assigns the given Network instance (or None) to become the
        new child of this Network at the given index.  See the class
        docstring for what constitutes a child."""
        if subnet is not None:
            if not isinstance (subnet, Network):
                raise TypeError, "Not an instance of Network: %r" % (subnet,)
            if child_addresses (self.address)[index] != subnet.address:
                raise ValueError, ("%s is not the %s subnet of %s." %
                                   (subnet.address,
                                    "lower" if index == 0 else "upper",
                                    self.address))
        self._children[index] = subnet
    
    def find (self, subnet_addr):
        """Returns a Network instance representing the given network
        address.  The address given must be contained within this
        Network--it must equal this Network's address or one of its
        possible descendants.  If there is no matching Network, one is
        created, connected to this Network (directly or indirectly),
        and returned, as long as it would be legal for a Network of
        that address to exist in this Network."""
        
        if not is_network_in_network (subnet_addr, self.address):
            raise ValueError, ("%s is not contained within %s." %
                               (network_to_IPy (subnet_addr),
                                network_to_IPy (self.address)))
        self_base, self_prefix = self.address
        subnet_base, subnet_prefix = subnet_addr
        subnet_suffix = 128 - subnet_prefix
        # Iterate through those bits of subnet_base that are
        # positionally part of the network prefix of both subnet_addr
        # and self.address, from most-significant to least.  This
        # subsequence of network bits, in that order, forms a path
        # through the tree from here to the target node.
        path_bits = (reverse_bits (subnet_base >> subnet_suffix,
                                   subnet_prefix) >>
                     self_prefix)
        node = self
        for i in xrange (subnet_prefix - self_prefix):
            child_index = path_bits & 1
            path_bits = path_bits >> 1
            child = node.get_child (child_index)
            if child is None:
                child_addr = child_addresses (node.address)[child_index]
                child = self.__class__ (child_addr)
                node.set_child (child_index, child)
            node = child
        assert node.address == subnet_addr
        return node

def reverse_bits (n, bits):
    """Reverses the bits in n (an int or long).  bits is the number of
    bits to reverse."""
    
    out = 0
    for i in xrange (bits):
        out = out << 1
        out = out | (n & 1)
        n = n >> 1
    return out
