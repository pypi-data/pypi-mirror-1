#!/usr/bin/env python
"""
Informational data on various network address types.
"""
import pprint

from netaddr.address import CIDR, Wildcard

#-----------------------------------------------------------------------------
def ipv4_cidr_prefixes():
    """
    Returns a recordset (list of dicts) of host/network breakdown for IPv4
    using all of the various CIDR prefixes.
    """
    table = []
    prefix = 32
    while prefix >= 0:
        cidr = CIDR('0.0.0.0/%d' % prefix)
        table.append(dict(prefix=str(cidr), hosts=cidr.size(),
            networks=2 ** cidr.prefixlen()))
        prefix -= 1
    return table

#-----------------------------------------------------------------------------
def ipv6_cidr_prefixes():
    """
    Returns a recordset (list of dicts) of host/network breakdown for IPv6
    using all of the various CIDR prefixes.
    """
    table = []
    prefix = 128
    while prefix >= 0:
        cidr = CIDR('::/%d' % prefix)
        table.append(dict(prefix=str(cidr), hosts=cidr.size(),
            networks=2 ** cidr.prefixlen()))
        prefix -= 1
    return table

#-----------------------------------------------------------------------------
def print_ipv4_cidr_prefixes():
    """
    Prints a table to stdout of host/network breakdown for IPv4 using CIDR
    notation.
    """
    print '%-10s %-15s %-15s' % ('Prefix', 'Hosts', 'Networks')
    print '-'*10, '-'*15, '-'*15
    for record in ipv4_cidr_prefixes():
        print '%(prefix)-10s %(hosts)15s %(networks)15s' % record

#-----------------------------------------------------------------------------
def print_ipv6_cidr_prefixes():
    """
    Prints a table to stdout of host/network breakdown for IPv6 using CIDR
    notation.
    """
    print '%-10s %-40s %-40s' % ('Prefix', 'Hosts', 'Networks')
    print '-'*10, '-'*40, '-'*40
    for record in ipv6_cidr_prefixes():
        print '%(prefix)-10s %(hosts)40s %(networks)40s' % record

#-----------------------------------------------------------------------------
def ipv4_iana_dict(fname):
    """
    Parses the IANA IPv4 address space text file.

    Returns a dictionary in the format :-

    { '<status>' : { '<designation>' : ['<prefix>'] } }
    """
    d = {}
    for line in open(fname):
        line = line.strip()
        if line == '':
            continue
        prefix = line[0:8].strip()
        designation = line[8:45].strip()
        date = line[45:55].strip()
        whois = line[55:75].strip()
        status = line[75:94].strip().lower()
        if '/' in prefix:
            #print prefix, designation, whois, status
            d.setdefault(status, {})
            d[status].setdefault(designation, [])
            d[status][designation].append(prefix)
    return d

#-----------------------------------------------------------------------------
def ipv4_wildcard_lookup(d):
    """
    Returns a lookup that provides
    """
    #   FIXME - this whole bit of code is bugged!
    for status in d:
        designations = d[status]
        for designation in designations:
            prefixes = designations[designation]
            wildcards = []
            if len(prefixes) == 0:
                continue
            elif len(prefixes) == 1:
                (octet, masklen) = prefix.split('/')
                wc = Wildcard('%d.*.*.*' % int(octet))
                wildcards.append(str(wc))
            else:
                for i, prefix in enumerate(prefixes):
                    (octet, masklen) = prefix.split('/')
                    if i == 0:
                        wc = Wildcard('%d.*.*.*' % int(octet))
                    else:
                        if wc[0][0] == int(octet) - 1:
                            wc[-1][0] = int(octet)
                        else:
                            wildcards.append(str(wc))
                            wc = Wildcard('%d.*.*.*' % int(octet))

            designations[designation] = wildcards

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    import pprint
    #pprint.pprint(ipv4_cidr_prefixes())
    #pprint.pprint(ipv6_cidr_prefixes())
    #print_ipv4_cidr_prefixes()
    #print_ipv6_cidr_prefixes()

    ipv4_db = r'Z:\src\python\my_modules\netaddr\trunk\data\databases\iana-ipv4-address-space.txt'
    iana_dict = ipv4_iana_dict(ipv4_db)

    pprint.pprint(iana_dict)
    print '-'*80

    ipv4_wildcard_lookup(iana_dict)
    pprint.pprint(iana_dict)

#    for block in sorted(r_lookup):
#        print block

