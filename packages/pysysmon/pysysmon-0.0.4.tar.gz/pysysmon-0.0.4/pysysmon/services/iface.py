"""Network interface service"""

from os import path
import fcntl
from struct import pack, unpack
import socket

SIOCGIFFLAGS = 0x8913
IFF_UP = 0x1

#struct ifreq32 {
#        union {
#                char    ifrn_name[16];
#        } ifr_ifrn;
#        union {
#                struct  sockaddr ifru_addr;
#                struct  sockaddr ifru_dstaddr;
#                struct  sockaddr ifru_broadaddr;
#                struct  sockaddr ifru_netmask;
#                struct  sockaddr ifru_hwaddr;
#                short   ifru_flags;
#                int     ifru_ivalue;
#                int     ifru_mtu;
#                struct  ifmap32 ifru_map;
#                char    ifru_slave[16];   /* Just fits the size */
#                char    ifru_newname[16];
#                __kernel_caddr_t32 ifru_data;
#        } ifr_ifru;
#};

def _get_flags_for(iface):
    format = "16s H 16x"  # ifrn_name, ifru_flags + padding
    # Useless socket, because Linux wants it.
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    req = pack(format, iface, 0)
    resp = fcntl.ioctl(sock, SIOCGIFFLAGS, req)
    return unpack(format, resp)[1]

def is_up(iface):
    try:
        return _get_flags_for(iface) & IFF_UP > 0
    except IOError:
        return False

class InterfaceUp(object):
    refresh_rate = 60

    def __init__(self, iface, name=None):
        self.name = name or iface
        self.iface = iface

    def ok(self):
        return is_up(self.iface)
