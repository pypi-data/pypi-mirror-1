minOct = 0
maxOct = 2**8 - 1 # 256
maxTotal = 256**4 - 1 # 4294967295L

def int2octets(num):
    """
    >>> int2octets(1)
    '0.0.0.1'
    >>> int2octets(256**1 - 1)
    '0.0.0.255'
    >>> int2octets(256**2 - 1)
    '0.0.255.255'
    >>> int2octets(256**3 - 1)
    '0.255.255.255'
    >>> int2octets(256**4 - 1)
    '255.255.255.255'

    # test invalid values
    >>> int2octets(256**4)
    Traceback (most recent call last):
    ValueError: IPv4 addresses must be between 0 and 256**4 - 1.
    >>> int2octets(-1)
    Traceback (most recent call last):
    ValueError: IPv4 addresses must be between 0 and 256**4 - 1.
    >>> int2octets(256**4 + 1)
    Traceback (most recent call last):
    ValueError: IPv4 addresses must be between 0 and 256**4 - 1.
    """
    if num < minOct or num > maxTotal:
        msg = 'IPv4 addresses must be between 0 and 256**4 - 1.'
        raise ValueError, msg
    octets = []
    for i in range(4):
        octets.append(str(num & 255))
        num >>= 8
    octets.reverse()
    return ".".join(octets)

def octets2int(octs):
    """
    >>> octets2int('0.0.0.0')
    0
    >>> octets2int('0.0.0.1')
    1
    >>> octets2int('0.0.0.255') == 256**1 - 1
    True
    >>> octets2int('0.0.255.255') == 256**2 - 1
    True
    >>> octets2int('0.255.255.255') == 256**3 - 1
    True
    >>> octets2int('255.255.255.255') == 256**4 - 1
    True

    # test invalid values
    >>> octets2int('0.0.0.-1')
    Traceback (most recent call last):
    ValueError: Each octect must have a value between 0 and 2**8-1, inclusive.
    >>> octets2int('-1.0.0.0')
    Traceback (most recent call last):
    ValueError: Each octect must have a value between 0 and 2**8-1, inclusive.
    >>> octets2int('0.0.0.256')
    Traceback (most recent call last):
    ValueError: Each octect must have a value between 0 and 2**8-1, inclusive.
    >>> octets2int('256.0.0.0')
    Traceback (most recent call last):
    ValueError: Each octect must have a value between 0 and 2**8-1, inclusive.
    """
    octs = [int(x) for x in octs.split('.')]
    num = 0
    for octet in octs:
        if not minOct <= octet <= maxOct:
            msg = ('Each octect must have a value between 0 and 2**8-1, ' +
                'inclusive.')
            raise ValueError, msg
        num <<= 8
        num += octet
    return num

def incrementIP(ip):
    '''
    >>> ip = '192.168.4.1'
    >>> incrementIP(ip)
    '192.168.4.2'
    >>> ip = '10.0.5.255'
    >>> incrementIP(ip)
    '10.0.6.0'
    '''
    current = octets2int(ip) + 1
    return int2octets(current)


def _test():
    import doctest
    return doctest.testmod()

if __name__ == '__main__':
    _test()
