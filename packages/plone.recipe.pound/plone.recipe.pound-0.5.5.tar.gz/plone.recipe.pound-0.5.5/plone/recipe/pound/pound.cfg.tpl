# pound.cfg
# created by plone.recipe.pound

# global options:
User        "$owner"
Group       "$group"

Daemon $daemon

# Logging: (goes to syslog by default)
#    0    no logging
#    1    normal
#    2    extended
#    3    Apache-style (common log format)
LogLevel   $log_level

# Log facility -- the manpage for syslog.conf(5) lists valid values.
LogFacility  $log_facility

# check backend every X secs:
Alive        $alive

# Enable or disable the dynamic rescaling code (default: 0)
DynScale $dynscale

# After this long has passed without the client sending any data Pound will close connection (default 10)
Client $client

# How long should Pound wait for a response from the back-end (in seconds). Default: 15 seconds.
TimeOut $timeout

# How long should Pound continue to answer existing connections after a receiving and INT or HUP signal
Grace $grace

# Socket
Control "$socket"

# listen, redirect and ... to:
#for $balancer in $balancers
# balancer for $balancer.name
ListenHTTP
    Address $balancer.adress
    Port    $balancer.port
    # for webdav
    xHTTP    2
    Service
    #for $backend in $balancer.backends
    BackEnd
        Address $backend.host
        Port    $backend.port
        #if $backend.timeout
        TimeOut $backend.timeout
        #end if
        #if $backend.priority
        Priority $backend.priority
        #end if

    End
    #end for

    #if $sticky == 'on'
    # for session cookies
    Session
        Type $sessiontype
        ID "$sessioncookie"
        TTL $sessiontimeout
    End
    #end if

    End
End
#end for


