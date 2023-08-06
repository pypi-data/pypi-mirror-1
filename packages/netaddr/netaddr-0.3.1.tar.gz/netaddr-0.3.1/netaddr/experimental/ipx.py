#!/usr/bin/env python
"""
This module contains implementation details on protocol's that have pretty much
been resigned to history by the de facto Internet Protocol.

It is more a bit of playfulness for us old timers and to prove netaddr's basic flexibility via the use of strategies rather than something that is deemed to
be entirely meaningful or even useful.

Think of it as a mere curiousity.
"""
from netaddr.strategy import AddrStrategy
from netaddr.address import Addr, EUI

AT_IPX = 0x50
AT_APPLETALK = 0x18

#-----------------------------------------------------------------------------
class IPXStrategy(AddrStrategy):
    """
    Implements the operations that can be performed on a Novell Netware IPX
    address.
    """
    def __init__(self):
        super(self.__class__, self).__init__(addr_type=AT_IPX, width=80,
              word_size=8, word_fmt='%02x', delimiter=':', to_upper=True)

#-----------------------------------------------------------------------------
class AppleTalkStrategy(AddrStrategy):
    """
    Implements the operations that can be performed on an AppleTalk address.
    """
    def __init__(self):
        super(self.__class__, self).__init__(addr_type=AT_APPLETALK, width=24,
              word_size=8, word_fmt='%02x', delimiter=':', to_upper=True)

#-----------------------------------------------------------------------------
class IPX(Addr):
    """
    A class whose objects represent Novell Netware IPX addresses.
    """
    def __init__(self, addr):
        """
        Constructor.

        addr - the string form of an IPX address or a network byte order
        int/long value.
        """
        if not isinstance(addr, (str, unicode, int, long)):
            raise Exception("addr must be an address in string form or a " \
                "positive int/long!")

        self.value = None
        self.strategy = IPXStrategy()

        if addr is None:
            addr = 0

        self.addr_type = self.strategy.addr_type
        self.setvalue(addr)

    def network_id(self):
        """
        Returns the OUI (Organisationally Unique Identifier for this
        EUI-48/MAC address.
        """
        delimiter = self.strategy.delimiter
        return delimiter.join(["%02x" % i for i in self[0:4]]).upper()

    def host_id(self):
        """
        Returns the host identifier as an EUI object (MAC address).
        """
        mac = '-'.join(["%02x" % i for i in self[4:]])
        return EUI(mac)

#-----------------------------------------------------------------------------
class ATalk(Addr):
    """
    A class whose objects represent Appletalk addresses.
    """
    def __init__(self, addr):
        """
        Constructor.

        addr - the string form of an IPX address or a network byte order
        int/long value.
        """
        if not isinstance(addr, (str, unicode, int, long)):
            raise Exception("addr must be an address in string form or a " \
                "positive int/long!")

        self.value = None
        self.strategy = AppleTalkStrategy()

        print self.strategy

        if addr is None:
            addr = 0

        self.addr_type = self.strategy.addr_type
        self.setvalue(addr)

    def network_id(self):
        """
        Returns the 16-bit router assigned network identifier.
        """
        delimiter = self.strategy.delimiter
        word_fmt = self.strategy.word_fmt
        return delimiter.join([word_fmt % i for i in self[3:]])

    def host_id(self):
        """
        Returns the 8-bit host identifier (randomly assigned).
        """
        return self[-1]


#-----------------------------------------------------------------------------
if __name__ == '__main__':
    ipx = IPX('01:02:03:04:00:13:A9:FB:B7:11')
    print ipx
    print ipx.network_id()
    print ipx.host_id()

    atalk = ATalk(0)
    print atalk
    print atalk.network_id()
    print atalk.host_id()
