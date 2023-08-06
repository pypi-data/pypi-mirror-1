import os

_SYS_USER = None


def get_sysuser():
    global _SYS_USER
    if _SYS_USER:
        return _SYS_USER

    envvars = ('LOGNAME', 'USER', 'USERNAME')
    for x in envvars:
        v = os.environ.get(x, None)
        if v:
            _SYS_USER = v
            return _SYS_USER

    try:
        import pwd
        _SYS_USER = pwd.getpwuid(os.getuid())[0]
        return _SYS_USER
    except:
        pass

    _SYS_USER = os.getlogin()
    return _SYS_USER
