#!/usr/local/bin/python
from GinGin import GinGin_CGI

if __name__ == '__main__':
    import fcgi
    import socket

    try:
        while fcgi.isFCGI():
            req = fcgi.Accept()
            GinGin_CGI.GinGin(req)
            req.Finish()
            pass
    except socket.error:
        pass
    pass

