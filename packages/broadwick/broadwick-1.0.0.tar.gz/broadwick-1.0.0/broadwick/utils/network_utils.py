import socket

def get_unused_port(bind_address = "0.0.0.0"):
    """
    ripped off from http://mail.python.org/pipermail/python-checkins/2009-January/078089.html
    """
    tempsock = socket.socket()
    tempsock.bind((bind_address, 0))
    host, port = tempsock.getsockname()
    tempsock.close()
    del tempsock
    return port
    
def get_ip_address():
    """
    We can't just use socket.gethostbyname(socket.gethostname())
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # hm, dunno what to do if bitsy is down
    s.connect(('18.72.0.3', 0))
    ip = s.getsockname()[0]
    s.close()
    del s
    return ip

def can_connect(ip_or_host):
    """
    just try and open a socket to it. Return true if we can. 
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # hm, dunno what to do if bitsy is down
    try:
        s.connect((ip_or_host, 0))
        return True
    except socket.gaierror:
        return False
    finally:
        s.close()
        del s
