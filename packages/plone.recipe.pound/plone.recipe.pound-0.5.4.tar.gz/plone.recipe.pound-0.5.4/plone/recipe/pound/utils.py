import os

_SYS_USER = None
_SYS_GRP = None


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

def get_sysgroup():
    global _SYS_GRP

    if _SYS_GRP:
        return _SYS_GRP
    user = get_sysuser()
    try:
        import pwd
        import grp
        grpid = pwd.getpwuid(user)[3]
        _SYS_GRP = grp.getgrgid(grpid)[0]
        return _SYS_GRP
    except:
        try:
            import grp
            grpid = os.getgid()
            _SYS_GRP = grp.getgrgid(grpid)[0]
            return _SYS_GRP
        except:
            pass
    _SYS_USER = user
    return user
