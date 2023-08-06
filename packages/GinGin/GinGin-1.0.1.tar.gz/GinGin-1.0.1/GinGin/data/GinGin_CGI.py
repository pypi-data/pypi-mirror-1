#!/usr/local/bin/python
from GinGin import GinGin_CGI

if __name__ == '__main__':
    import fcgi
    import socket
    import config
    from GinGin import GinGin_db

    ggdb = GinGin_db.GGDB(config.GINGIN_DB)
    config.GINGIN_USER.set_db(ggdb)
    
    try:
        while fcgi.isFCGI():
            req = fcgi.Accept()
            GinGin_CGI.GinGin(req, ggdb)
            req.Finish()
            pass
    except socket.error:
        pass
    pass

