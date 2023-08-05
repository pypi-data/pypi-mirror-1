# -*- mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4; -*-
# vim:ft=python:et:sw=4:ts=4

"""
Program startup functions and wrappers.
"""

from log import *
from environ import *
from interp import *
import os, signal, sys

class UnsetError( Exception ): pass

def get_arg_or_env( var, argv, error_name = None ):
    """
    Get a value based from C{argv[1]}; if that is unavailable, try
    looking at the corresponding environment variable C{var}.

    @todo: This is a weird, weird function. Do I really use it
    anywhere?
    """
    try:
        value = argv[ 1 ]
    except IndexError:
        try:
            value = os.environ[ var ]
        except KeyError:
            if error_name is not None:
                raise UnsetError, interp( '$error_name must be specified' )
            else:
                raise UnsetError
    return value

def config_psyco():
    """
    Try to enable Psyco profiling if the C{USE_PSYCO} environment
    variable is non-empty.
    """
    if 'USE_PSYCO' in os.environ:
        try:
            import psyco
        except ImportError:
            pass
        else:
            psyco.profile()

###########################################################

# TODO implement @deprecated
# @deprecated( get_usr_conf )
def get_config_path(
        file_env,
        file_default,
        dir_env = 'ASSORTED_CONF',
        dir_default = '.assorted' ):
    """
    Get the path to a configuration file. This tries the following:
        1. C{environ[file_env]}
        2. C{environ[dir_env]/file_default}
        3. C{$HOME/dir_default/file_default}
    """
    try:
        try:
            path = os.environ[ file_env ]
        except KeyError:
            try:
                path = paths.path( os.environ[ dir_env ] ) / \
                        file_default
            except KeyError:
                path = paths.path( os.environ[ 'HOME' ] ) / \
                        dir_default / \
                        file_default
        return path
    except:
        raise #return None

def get_usr_conf( *args, **kwargs ):
    """Gets a config file from $HOME."""
    return get_config_path( *args, **kwargs )

def get_sys_conf( env, default ):
    """Gets a config file from /etc/."""
    try:
        path = os.environ[ env ]
    except KeyError:
        path = paths.path( '/etc' ) / default
    return path

###########################################################

def run_main():
    """
    A feature-ful program starter. Configures logging and psyco, then
    runs the C{main} function defined in the caller's module, passing
    in L{sys.argv}.  If the C{PYDBG} environment variable is set, then
    runs C{main} in L{pdb}.  If the C{PYPROF} environment variable is
    set, then runs C{main} in L{profile}.  Finally, exits with
    C{main}'s return value.

    For example::

        def main(argv):
            print "Hello " + argv[1]
        run_main()
    """
    # TODO figure out a better solution for this
    config_logging()
    config_psyco()
    frame = sys._getframe( 1 )
    try:
        name = frame.f_globals[ '__name__' ]
    except KeyError:
        pass
    else:
        if name == '__main__':
            main = frame.f_globals[ 'main' ]
            do_debug = is_environ_set( 'PYDBG' )
            do_profile = is_environ_set( 'PYPROF' )

            if do_debug:
                import pdb
                signal.signal(signal.SIGINT, lambda *args: pdb.set_trace())
                status = pdb.runcall( main, sys.argv )
            elif do_profile:
                import cProfile as profile
                container = {}
                output_path = os.environ[ 'PYPROF' ]
                profile.runctx( 'container[ "status" ] = main( sys.argv )',
                        globals(), locals(), filename = output_path )
                status = container[ 'status' ]
            else:
                status = main( sys.argv )

            ## watchdog timer commits suicide if after 3 seconds we
            ## still have not exited
            #timer = threading.Timer( 3, suicide )
            #timer.start()
            debug( 'commons.run_main', 'terminating cleanly' )
            sys.exit( status )
