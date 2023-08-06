# We only use IPy for parsing and printing.  Its internal operations
# are horrendously and needlessly slow--lots of string
# manipulation/serialization/deserialization where quick numeric
# operations will do.  When we manipulate IP addresses using bitwise
# operations instead of string operations--and don't forget that
# they're all IPv6 addresses, in naively-represented 128-bit
# big-integer glory--we get an approximate speedup to 27.7, or 5s
# vs. 0.18.
import IPy

# We represent IPv6 addresses as longs, and IPv6 networks as
# (base_address, prefix_length) tuples.  We represent IPv4 address as
# IPv4-mapped IPv6 addresses.

ipv4_net = (0x00000000000000000000FFFF00000000L, 96)

def is_address_in_network (address, network):
    return is_network_in_network ((address, 128), network)

def is_network_in_network (network1, network2):
    base1, prefix1 = network1
    base2, prefix2 = network2
    suffix = 128 - prefix2
    return prefix2 <= prefix1 and (base1 >> suffix) == (base2 >> suffix)

def is_address_ipv4_mapped (address):
    return is_address_in_network (address, ipv4_net)

def is_network_ipv4_mapped (network):
    return is_network_in_network (network, ipv4_net)

def address_to_IPy (address):
    if is_address_ipv4_mapped (address):
        return IPy.IP (address & 0xFFFFFFFFL, ipversion = 4)
    else:
        return IPy.IP (address, ipversion = 6)

def network_to_IPy (network):
    base, prefix = network
    if is_network_ipv4_mapped (network):
        return (IPy.IP (base & 0xFFFFFFFFL, ipversion = 4)
                .make_net (prefix - 96))
    else:
        return IPy.IP (base, ipversion = 6).make_net (prefix)

def IPy_to_network (ip):
    if ip.version () == 4:
        return ipv4_net[0] | ip.int (), ip.prefixlen () + 96
    elif ip.version () == 6:
        return ip.int (), ip.prefixlen ()
    else:
        raise ValueError, ("Given an address that doesn't seem to be "
                           "IPv4 or IPv6: %r (version %r)") % (ip, ip.version ())

def IPy_to_address (ip):
    if ip.version == 4:
        if ip.prefixlen () != 32:
            raise ValueError, "Given an IP network, but need an IP address."
        return ipv4_net[0] | ip.int ()
    elif ip.version == 6:
        if ip.prefixlen () != 128:
            raise ValueError, "Given an IP network, but need an IP address."
        return ip.int ()
    else:
        raise ValueError, \
            "Given an address that doesn't seem to be IPv4 or IPv6: %r" % (ip,)

def child_addresses (network):
    """Given an IP network, returns the networks of its two
    subdivisions: the lower division (where the new network bit is 0),
    and the upper division (where the new network bit is 1).
    
    If the IP network has no subdivisions, ValueError is raised."""
    
    base, prefix = network
    child_prefix = prefix + 1
    if child_prefix > 128:
        raise ValueError, "%s has no subdivisions." % (network_to_IPy (network),)
    child_0_base = base
    child_1_base = base | (1 << (128 - child_prefix))
    return ((child_0_base, child_prefix),
            (child_1_base, child_prefix))

def parent_address (network):
    """Given an IP network, returns two values: its parent network,
    and the bit that identifies the given network in relation to the
    parent network (0 when the given network is the lower subdivision
    of its parent, and 1 when the given network is the upper
    subdivision)."""
    
    base, prefix = network
    if prefix == 0 or (is_network_ipv4_mapped (network) and prefix <= 96):
        raise ValueError, \
            "%s has no parent network." % (network_to_IPy (network),)
    suffix = 128 - prefix
    bit = 1 & (base >> suffix)
    parent_base = base ^ (1 << suffix)
    parent_prefix = prefix - 1
    return (parent_base, parent_prefix), parent_bit

def address_bounds (network, exclusive = False):
    """Given an IP network, returns the first and last addresses of
    the network.
    
    When exclusive is True, the "end" of the network (the last address
    plus 1) is used, rather than the last address."""
    
    return (address_lower_bound (network),
            address_upper_bound (network, exclusive))

def address_lower_bound (network):
    """Given an IP network, returns the first address of the network."""
    
    base, prefix = network
    return base

def address_upper_bound (network, exclusive = False):
    """Given an IP network, returns the last address of the network.
    
    When exclusive is True, the "end address" of the network (the last
    address plus 1) is used, rather than the actual last address."""
    
    base, prefix = network
    return base + address_count (network) - (0 if exclusive else 1)

def address_count (network):
    """Returns the number of addresses in the given IP network.
    
    In the case of IPv4-mapped addresses, base and broadcast addresses
    are also counted."""
    
    return 1 << address_count_log2 (network)

def address_count_log2 (network):
    """Returns the base-2 logarithm of the number of addresses in the
    given IP network, as an integer.  (Commonly known as the number of
    host bits.)
    
    In the case of IPv4-mapped addresses, base and broadcast addresses
    are also counted."""
    
    base, prefix = network
    return 128 - prefix
