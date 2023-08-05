def validateVLSM(vlsm):
    '''
    >>> validateVLSM(50)
    Traceback (most recent call last):
    ValueError: The variable length subnet mask, or "prefix length" must be between 0 and 32, inclusive.
    >>> validateVLSM('45')
    Traceback (most recent call last):
    ValueError: The variable length subnet mask, or "prefix length" must be between 0 and 32, inclusive.
    >>> validateVLSM(32)
    >>> validateVLSM('27')
    >>> validateVLSM(17)
    >>> validateVLSM('0')
    >>> validateVLSM(-1)
    Traceback (most recent call last):
    ValueError: The variable length subnet mask, or "prefix length" must be between 0 and 32, inclusive.
    >>> validateVLSM('-10')
    Traceback (most recent call last):
    ValueError: The variable length subnet mask, or "prefix length" must be between 0 and 32, inclusive.
    '''
    
    if 0 > int(vlsm)  or int(vlsm) > 32:
        raise ValueError, "The variable length subnet mask, or " + \
            '"prefix length" must be between 0 and 32, inclusive.'

class CIDR(object):
    '''
    VLSM stands for variable length subnet mask and is the data
    after the slash. It is also called the "prefix length"

    # Let's make sure our globbing works
    >>> CIDR('10.4.1.2')
    10.4.1.2
    >>> CIDR('10.4.1.x')
    10.4.1.0/24
    >>> CIDR('10.4.x.2')
    10.4.0.0/16
    >>> CIDR('10.4.x.x')
    10.4.0.0/16
    >>> CIDR('10.*.*.*')
    10.0.0.0/8

    # Now let's check out the zeros anf get some host counts
    # while we're at it
    # 
    # Since there may very well be many circumstances were one
    # would have a valid single address ending in one or more
    # zeros, I don't think it's a good idea to force this
    # behavior. I will comment out for now and may completely
    # remove sometime in the future.
    #>>> CIDR('10.4.1.0')
    #10.4.1.0/24
    #>>> c = CIDR('10.4.0.0')
    #>>> c
    #10.4.0.0/16
    #>>> c.getHostCount()
    #65536
    #>>> c = CIDR('10.0.0.0')
    #>>> c
    #10.0.0.0/8
    #>>> c.getHostCount()
    #16777216
    #>>> CIDR('0.0.0.0')
    #0.0.0.0/0
    #>>> CIDR('10.0.0.2')
    #10.0.0.2/32

    # How about manual CIDR entries?
    >>> c = CIDR('172.16.4.28/31')
    >>> c
    172.16.4.28/31
    >>> c.getHostCount()
    2
    >>> c.getOctetTuple()
    (172, 16, 4, 28)
    >>> c = CIDR('172.16.4.28/27')
    >>> c
    172.16.4.28/27
    >>> c.getHostCount()
    32
    >>> c = CIDR('172.16.4.28/15')
    >>> c
    172.16.4.28/15
    >>> c.getHostCount()
    131072

    # What about some silly errors:
    >>> c = CIDR('10.100.2.4/12/11')
    Traceback (most recent call last):
    ValueError: There appear to be too many '/' in your network notation.
    '''
    def __init__(self, cidr_string):
        net = cidr_string.split('/')
        vlsm = 32
        if len(net) == 2:
            net, vlsm = net
            vlsm = int(vlsm)
            validateVLSM(vlsm)
        elif len(net) > 2:
            raise ValueError, "There appear to be too many '/' in " + \
                "your network notation."
        else:
            net = net[0]
        self.vlsm = vlsm
        self.net = net
        self.octets = net.split('.')
        #if vlsm != 32:
        #    if not self.zeroCheck():
        self.globCheck()
        self.raw = None

    def __repr__(self):
        if self.vlsm == 32:
            return self.net
        return "%s/%s" % (self.net, self.vlsm)        

    def getOctetTuple(self):
        return tuple([ int(x) for x in self.octets ])

    def globCheck(self):
        # check to see if any octext is '*', 'x'
        net_globs = ['*', 'x', 'X']
        check = False
        for char in net_globs:
            if char in self.net:
                check = True
        if not check:
            return False
        glob_index = None
        # Now let's look at the octets in reverse order, starting
        # at the "back", since the glob closest to the "front" will 
        # determine how big the network really is
        for index in range(len(self.octets)-1,-1,-1):
            if self.octets[index] in net_globs:
                glob_index = index

        # Let's zero out the netblock portion                
        for index in range(glob_index, 4):
            self.octets[index] = '0'

        # Now we need to get the CIDR for the glob
        if not (glob_index is None and self.vlsm is None):
            self.vlsm = (glob_index) * 8

        # Let's rebuild our new net address:
        self.net = '.'.join(self.octets)

    def zeroCheck(self):
        if not self.octets[3] == '0':
            return False
        zeros = [1,1,1,0]
        if self.octets[2] == '0':
            zeros[2] = 0
            if self.octets[1] == '0':
                zeros[1] = 0
                if self.octets[0] == '0':
                    zeros[0] = 0

        # Set the netmask by the first zero found
        self.vlsm = zeros.index(0)*8
        return True

    def getHostCount(self):
        return 2**(32 - self.vlsm)

    def _getOctetRange(self, position, chunk_size):
        divide_by = 256 / chunk_size
        for i in xrange(divide_by):
            start = i*chunk_size
            end = i*chunk_size+chunk_size-1
            if start <= position <= end:
                return (start, end)
            
    def getHostRange(self):
        '''
        This is a lazy way of doing binary subnet math ;-)

        The first thing we do is make two copies of the CIDR octets
        stored in self.octets. We have one copy each for the address
        representing the first host in the range and then the last
        host in the range.

        Next, we check to see what octet we will be dealing with
        by looking at the netmask (self.vlsm). Then we get the list
        index for that octet and calculate the octet number from
        this. 

        The next bit is a little strange and really deserves a
        description: chunk_size. This really means "how many times
        is the current octect divided up?" We use that number and
        the CIDR value for the octet in question to determine the
        netblock range.

        # Let's try the first octet
        >>> CIDR('172.16.4.28/31').getHostRange()
        (172.16.4.28, 172.16.4.29)
        >>> CIDR('172.16.4.27/31').getHostRange()
        (172.16.4.26, 172.16.4.27)

        >>> CIDR('172.16.4.28/30').getHostRange()
        (172.16.4.28, 172.16.4.31)
        >>> CIDR('172.16.4.27/30').getHostRange()
        (172.16.4.24, 172.16.4.27)

        >>> CIDR('172.16.4.28/29').getHostRange()
        (172.16.4.24, 172.16.4.31)
        >>> CIDR('172.16.4.31/29').getHostRange()
        (172.16.4.24, 172.16.4.31)
        >>> CIDR('172.16.4.32/29').getHostRange()
        (172.16.4.32, 172.16.4.39)

        >>> CIDR('172.16.4.27/28').getHostRange()
        (172.16.4.16, 172.16.4.31)
        >>> CIDR('172.16.4.27/27').getHostRange()
        (172.16.4.0, 172.16.4.31)
        >>> CIDR('172.16.4.27/26').getHostRange()
        (172.16.4.0, 172.16.4.63)
        >>> CIDR('172.16.4.27/25').getHostRange()
        (172.16.4.0, 172.16.4.127)
        >>> CIDR('172.16.4.27/24').getHostRange()
        (172.16.4.0, 172.16.4.255)

        # Let's work on the next octet
        >>> CIDR('172.16.4.27/23').getHostRange()
        (172.16.4.0, 172.16.5.255)
        >>> CIDR('172.16.4.27/22').getHostRange()
        (172.16.4.0, 172.16.7.255)
        >>> CIDR('172.16.4.27/21').getHostRange()
        (172.16.0.0, 172.16.7.255)
        >>> CIDR('172.16.4.27/20').getHostRange()
        (172.16.0.0, 172.16.15.255)
        >>> CIDR('172.16.4.27/19').getHostRange()
        (172.16.0.0, 172.16.31.255)
        >>> CIDR('172.16.4.27/18').getHostRange()
        (172.16.0.0, 172.16.63.255)
        >>> CIDR('172.16.4.27/17').getHostRange()
        (172.16.0.0, 172.16.127.255)
        >>> CIDR('172.16.4.27/16').getHostRange()
        (172.16.0.0, 172.16.255.255)

        # Now the next octet
        >>> CIDR('172.16.4.27/15').getHostRange()
        (172.16.0.0, 172.17.255.255)
        >>> CIDR('172.16.4.27/14').getHostRange()
        (172.16.0.0, 172.19.255.255)
        >>> CIDR('172.16.4.27/13').getHostRange()
        (172.16.0.0, 172.23.255.255)
        >>> CIDR('172.16.4.27/12').getHostRange()
        (172.16.0.0, 172.31.255.255)
        >>> CIDR('172.16.4.27/11').getHostRange()
        (172.0.0.0, 172.31.255.255)
        >>> CIDR('172.16.4.27/10').getHostRange()
        (172.0.0.0, 172.63.255.255)
        >>> CIDR('172.16.4.27/9').getHostRange()
        (172.0.0.0, 172.127.255.255)
        >>> CIDR('172.16.4.27/8').getHostRange()
        (172.0.0.0, 172.255.255.255)

        # Now the final octet
        >>> CIDR('172.16.4.27/7').getHostRange()
        (172.0.0.0, 173.255.255.255)
        >>> CIDR('172.16.4.27/6').getHostRange()
        (172.0.0.0, 175.255.255.255)
        >>> CIDR('172.16.4.27/5').getHostRange()
        (168.0.0.0, 175.255.255.255)
        >>> CIDR('172.16.4.27/4').getHostRange()
        (160.0.0.0, 175.255.255.255)
        >>> CIDR('172.16.4.27/3').getHostRange()
        (160.0.0.0, 191.255.255.255)
        >>> CIDR('172.16.4.27/2').getHostRange()
        (128.0.0.0, 191.255.255.255)
        >>> CIDR('172.16.4.27/1').getHostRange()
        (128.0.0.0, 255.255.255.255)
        >>> CIDR('172.16.4.27/0').getHostRange()
        (0.0.0.0, 255.255.255.255)
        '''
        # Setup the starting and ending octets
        so = [ int(x) for x in self.octets ]
        eo = [ int(x) for x in self.octets ]

        if self.vlsm >= 24:
            sidx = 3
        elif self.vlsm >= 16:
            so[3] = 0
            eo[3] = 255
            sidx = 2
        elif self.vlsm >= 8:
            so[2] = so[3] = 0
            eo[2] = eo[3] = 255
            sidx = 1
        elif self.vlsm < 8:
            so[1] = so[2] = so[3] = 0
            eo[1] = eo[2] = eo[3] = 255
            sidx = 0
        octet_number = 4 - (sidx + 1)
        chunk_size = 2**(32-self.vlsm) / (256**octet_number)
        start, end = self._getOctetRange(so[sidx], chunk_size)
        so[sidx] = start
        eo[sidx] = end

        # Convert the octects back to strings
        so = [ str(x) for x in so ]
        eo = [ str(x) for x in eo ]
        return (CIDR('.'.join(so)), CIDR('.'.join(eo)))

class Networks(list):
    '''
    >>> net_cidr = CIDR('192.168.4.0/24')
    >>> corp_cidr = CIDR('10.5.0.0/16')
    >>> vpn_cidr = CIDR('172.16.9.5/27')

    >>> mynets = Networks([net_cidr, corp_cidr, vpn_cidr])

    >>> home_router = CIDR('192.168.4.1')
    >>> laptop1 = CIDR('192.168.4.100')
    >>> webserver = CIDR('10.5.10.10')
    >>> laptop2 = CIDR('172.16.9.17')
    >>> google = CIDR('64.233.187.99')

    >>> home_router in mynets
    True
    >>> laptop1 in mynets
    True
    >>> webserver in mynets
    True
    >>> laptop2 in mynets
    True
    >>> google in mynets
    False


    '''
    def __contains__(self, cidr_obj):
        for network in self:
            if self.isInRange(cidr_obj, cidr_netblock=network):
                return True
        return False

    def isInRange(self, cidr_obj, cidr_tuple=(), cidr_netblock=None):
        '''
        This might normally be a prive method, but since it will 
        probably generally useful, we'll make it "public."

        >>> net_cidr = CIDR('192.168.4.0/24')
        >>> mynet = Networks([net_cidr])
        >>> router = CIDR('192.168.4.1')
        >>> fileserver = CIDR('192.168.4.10')
        >>> laptop = CIDR('192.168.4.100')
        >>> mynet.isInRange(router, (fileserver, laptop))
        False
        >>> mynet.isInRange(fileserver, (router, laptop))
        True
        >>> mynet.isInRange(fileserver, cidr_tuple=(router, laptop))
        True
        >>> mynet.isInRange(router, cidr_netblock=net_cidr)
        True

        >>> mynet.isInRange(router)
        Traceback (most recent call last):
        ValueError: You must provide either a tuple of CIDR objects or a CIDR object that represents a netblock.
        '''
        #raise str(cidr_tuple)
        if not (cidr_tuple or cidr_netblock):
            raise ValueError, 'You must provide either a tuple of ' + \
                'CIDR objects or a CIDR object that represents a ' + \
                'netblock.'
        if cidr_tuple:
            start, end = cidr_tuple
        else:
            start, end = cidr_netblock.getHostRange()
        if (start.getOctetTuple() < cidr_obj.getOctetTuple()
            < end.getOctetTuple() ):
            return True
        return False


def _test():
    import doctest, network
    return doctest.testmod(network)

if __name__ == '__main__':
    _test()
