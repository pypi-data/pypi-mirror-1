#!/usr/bin/env python
# ex:ts=8:sw=4:sts=4:et
# -*- tab-width: 8; c-basic-offset: 4; indent-tabs-mode: t -*-
#
# Copyright (C) 2009 Marco Pantaleoni. All rights reserved

"""Django HTTP(S) application server

Inspired in part by DjangoCerise
(http://xhtml.net/scripts/Django-CherryPy-server-DjangoCerise)

It handles both the HTTP and HTTPS schemes.
For more info on this aspect, see:
  http://www.fairviewcomputing.com/blog/2008/10/23/django-wsgi-handler-ssl-proxies/

In case of HTTPS, the request should indicate to Django that the request is
secure. To do so, in nginx, add the directive:

    proxy_set_header X-Url-Scheme $scheme;

@see: http://xhtml.net/scripts/Django-CherryPy-server-DjangoCerise
@see: http://www.fairviewcomputing.com/blog/2008/10/23/django-wsgi-handler-ssl-proxies/

@author: Marco Pantaleoni
@copyright: Copyright (C) 2008-2009 Marco Pantaleoni
"""

__author__ = "Marco Pantaleoni"
__copyright__ = "Copyright (C) 2008-2009 Marco Pantaleoni"
__license__ = "GPLv2"

__contributors__ = [
]

PROGNAME    = "djangoserve"
__version__ = "0.1"

import os               # Miscellaneous OS interfaces.
import sys              # System-specific parameters and functions.
import getopt, glob, re, string, time
import optparse
import datetime
import logging
import signal
#import signal as unixsignal

from softwarefabrica.django.appserver.wsgiserver import CherryPyWSGIServer as Server
from django.core.handlers.wsgi import WSGIHandler

from sflib import daemonize

# Django related import are performed after the loading of the
# configuration as we need to set the DJANGO_SETTINGS_MODULE
# environment variable which comes from the config.

this_mod = __import__(__name__)
CUR_DIR       = os.path.abspath(os.path.dirname(this_mod.__file__))

# -- Defaults ------------------------------------------------------------

DEFAULT_CONFIG_FILE   = "/etc/djangoserve.conf"
DEFAULT_LOGFILE       = '/var/log/djangoserve.log'
DEFAULT_PIDFILE       = '/var/run/djangoserve.pid'
DEFAULT_LOCKFILE      = '/var/lock/subsys/djangoserve'
DEFAULT_DAEMON_USER   = 'nobody'
DEFAULT_DAEMON_GROUP  = 'nogroup'

LOGGING_CONF_FILE     = os.path.join(CUR_DIR, "djangoserve-logging.conf")

# -- Constants -----------------------------------------------------------

VERBOSITY_QUIET   = 0
VERBOSITY_NORMAL  = 1
VERBOSITY_VERBOSE = 2
VERBOSITY_DEBUG   = 3

# -- Globals -------------------------------------------------------------


#============================================================================#
# Utility functions
#============================================================================#

#============================================================================#
# Application class
#============================================================================#

class Application(object):
    """
    A singleton class implementing the application.
    """

    _instance = None

    def __init__(self, options, args, log, dbg_log):
        if self._instance:
            raise "An instance of this singleton has already been created."
        Application._instance = self
        self.options = options
        self.args = args

        self.l_log = log
        self.l_dbg = dbg_log

        self.cwd    = None		# original working dir
        self.do_run = True
        self.server = None		# WSGI server

    def Instance(cls):
        return cls._instance
    Instance = classmethod(Instance)

    def setup(self):
        """
        Perform setup.
        """
        signal.signal(signal.SIGUSR1,  self.signal_handler)
        signal.signal(signal.SIGHUP,  self.signal_handler)
        try:
            signal.signal(signal.SIGINT,  self.signal_handler)
        except:
            pass
        try:
            signal.signal(signal.SIGQUIT, self.signal_handler)
        except:
            pass
        try:
            signal.signal(signal.SIGTERM, self.signal_handler)
        except:
            pass
        try:
            signal.signal(signal.SIGKILL, self.signal_handler)
        except:
            pass
        return self

    def cleanup(self):
        """
        Perform cleanup.

        Remove PID file and lockfile.
        """

        if self.options.RUN_AS_DAEMON:
            self.log("removing lockfile and PID file")
            if self.options.PIDFILE and os.path.exists(self.options.PIDFILE):
                os.remove(self.options.PIDFILE)
            if self.options.LOCKFILE and os.path.exists(self.options.LOCKFILE):
                os.remove(self.options.LOCKFILE)
        return self

    def log(self, msg, verb=VERBOSITY_VERBOSE):
        """
        Log a message ``msg`` with verbosity ``verb``.
        """
        if verb <= self.options.VERBOSITY:
            if verb == VERBOSITY_DEBUG:
                self.l_log.debug(msg)
                sys.stderr.write(msg + "\n")
                sys.stderr.flush()
            else:
                self.l_log.info(msg)
            sys.stdout.flush()
            sys.stderr.flush()
        return self

    def dbg(self, msg, verb=VERBOSITY_DEBUG):
        """
        Log a debug message ``msg`` with verbosity ``verb``.
        """
        if verb <= self.options.VERBOSITY:
            self.l_log.debug(msg)
            sys.stdout.flush()
            sys.stderr.flush()
        return self

    def devdbg(self, msg, verb=VERBOSITY_DEBUG):
        """
        Log a development debug message ``msg`` with verbosity ``verb``.
        """
        if verb <= self.options.VERBOSITY:
            self.l_dbg.debug(msg)
            sys.stdout.flush()
            sys.stderr.flush()
        return self

    def Run(self):
        """
        Actual program execution happens here. 
        """
        from softwarefabrica.django.appserver.translogger import TransLogger

        self.log("Program started.")

        self.setup()

        # UID/GID change here is redundant (because it's handled by daemonize.daemonize())
        # but... better safe than sorry!
        if self.options.RUN_AS_DAEMON:
            if (self.options.SERVER_USER) or (self.options.SERVER_GROUP):
                daemonize.change_uid_gid(self.options.SERVER_USER, self.options.SERVER_GROUP)
        if self.options.DJANGO_SERVE_ADMIN:
            from django.core.servers.basehttp import AdminMediaHandler
            app = AdminMediaHandler(WSGIHandler())
        else:
            app = WSGIHandler()

        # this handles both the HTTP and HTTPS schemes
        # for more info, see:
        #    http://www.fairviewcomputing.com/blog/2008/10/23/django-wsgi-handler-ssl-proxies/
        # In case of HTTPS, the request should indicate to Django that the request
        # is secure. To do so, in nginx, add the directive:
        #   proxy_set_header X-Url-Scheme $scheme;
        def schemed_app(environ, start_response):
            environ['wsgi.url_scheme'] = environ.get('HTTP_X_URL_SCHEME', 'http')
            return app(environ, start_response)

        # http://pythonpaste.org/modules/translogger.html
        logged_app = TransLogger(schemed_app, logger = self.l_log)

        self.server = Server((self.options.IP_ADDRESS, self.options.PORT),
                             logged_app,
                             self.options.SERVER_THREADS, self.options.SERVER_NAME)
        if self.options.SSL:
            self.server.ssl_certificate = self.options.SSL_CERTIFICATE
            self.server.ssl_private_key = self.options.SSL_PRIVATE_KEY
        try:
            self.log("Starting the server on %s:%s" % (self.options.IP_ADDRESS, str(self.options.PORT)), verb=VERBOSITY_NORMAL)
            self.server.start()
        except KeyboardInterrupt:
            self.log("KeyboardInterrupt: stopping the server", verb=VERBOSITY_NORMAL)
            self.server.stop()
            self.cleanup()

        self.log("Program terminated.")
        return self

    def signal_handler(self, sig, stack):
        """Handle the signal sent to the daemon."""

        if sig == signal.SIGUSR1:
            pass
        elif sig == signal.SIGHUP:
            # TODO - perform a reload
            self.dbg("Should perform a reload.")
        elif sig == signal.SIGINT:
            self.log("SIGINT: stop the server")
            self.do_run = False
            self.server.stop()
            self.cleanup()
            sys.exit(1)
        elif sig == signal.SIGQUIT:
            self.log("SIGQUIT: stop the server")
            self.do_run = False
            self.server.stop()
            self.cleanup()
            sys.exit(1)
        elif sig == signal.SIGTERM:
            self.log("SIGTERM: stop the server")
            self.do_run = False
            self.server.stop()
            self.cleanup()
            sys.exit(0)
        else:
            self.log("Signal %s caught." % str(sig))

#============================================================================#
# main - program entry point
#============================================================================#

def _test():
    """
    Test entry point
    """
    import doctest
    doctest.testmod()

def main():
    """
    Program entry point
    """

    parser = optparse.OptionParser( version = "Django App Server (%%prog) version %s" % __version__,
                                    usage = """%prog [options]

Serve a Django application.
""" )

    parser.add_option( "-c", "--conf", "--config", "--configfile",
                       help = "use FILE as the configuration file (default: %s)" % DEFAULT_CONFIG_FILE,
                       action = "store", dest = "configfile",
                       default = DEFAULT_CONFIG_FILE, metavar = "FILE" )
    parser.add_option( "-l", "--logfile",
                       help = "use FILE as log file (default: %s)" % DEFAULT_LOGFILE,
                       action = "store", dest = "LOGFILE",
                       default = DEFAULT_LOGFILE, metavar = "FILE" )
    parser.add_option("-D", "--deamonize",
                      action="store_true", dest="RUN_AS_DAEMON", default = False,
                      help="become a daemon")
    parser.add_option( "-p", "--pidfile",
                       help = "save the daemon PID into PIDFILE (default: %s)" % DEFAULT_PIDFILE,
                       action = "store", dest = "PIDFILE",
                       default = DEFAULT_PIDFILE, metavar = "PIDFILE" )
    parser.add_option( "-L", "--lockfile",
                       help = "use LOCKFILE as the daemon lock file (default: %s)" % DEFAULT_LOCKFILE,
                       action = "store", dest = "LOCKFILE",
                       default = DEFAULT_LOCKFILE, metavar = "LOCKFILE" )
    parser.add_option( "-u", "--user", "--serveruser", "--server_user",
                       help = "run server as USER (default: %s)" % DEFAULT_DAEMON_USER,
                       action = "store", dest = "SERVER_USER",
                       default = DEFAULT_DAEMON_USER, metavar = "USER" )
    parser.add_option( "-g", "--group", "--servergroup", "--server_group",
                       help = "run server as group GROUP (default: %s)" % DEFAULT_DAEMON_GROUP,
                       action = "store", dest = "SERVER_GROUP",
                       default = DEFAULT_DAEMON_GROUP, metavar = "GROUP" )
    parser.add_option("-q", "--quiet",
                      action="store_const", dest="VERBOSITY", const=VERBOSITY_QUIET, default=VERBOSITY_NORMAL,
                      help="don't print anything on stdout")
    parser.add_option("-v", "--verbose",
                      action="store_const", dest="VERBOSITY", const=VERBOSITY_VERBOSE,
                      help="be verbose")
    parser.add_option("-d", "--debug",
                      action="store_const", dest="VERBOSITY", const=VERBOSITY_DEBUG,
                      help="be too verbose (debugging only)")
    parser.add_option( "-t", "--test", help = "perform internal testing.",
                       action = "store_true", dest = "TEST", default = False )

    # processing order is:
    #  def_values -> config file -> cmd line
    # (latter has precedence)

    # we pass an empty optparse.Values to parse_args to avoid getting default
    # values, since we process those separately
    (cmd_options, args) = parser.parse_args(sys.argv, values=optparse.Values())

    # here we get default values
    def_options = parser.get_default_values()

    cfg_file = def_options.configfile
    if hasattr(cmd_options, 'configfile'):
        cfg_file = cmd_options.configfile

    options = optparse.Values(defaults=def_options.__dict__)
    try:
        options.read_file(cfg_file, mode="loose")
        #options.read_module(cfg_file, mode="loose")
        options._update(cmd_options.__dict__, mode="loose")
    except ImportError, e:
        raise EnvironmentError, "Could not import configuration file '%s' (Is it on sys.path? Does it have syntax errors?): %s" % (options.configfile, e)

    # sys.path manipulation
    if hasattr(options, 'SYSPATH') and (options.SYSPATH is not None):
        sys.path = list(options.SYSPATH)
    if hasattr(options, 'SYSPATH_PREPEND') and (options.SYSPATH_PREPEND is not None):
        sys.path = list(options.SYSPATH_PREPEND) + sys.path
    if hasattr(options, 'SYSPATH_APPEND') and (options.SYSPATH_APPEND is not None):
        sys.path += list(options.SYSPATH_APPEND)
    #print sys.path

    # set django environment variable
    os.environ["DJANGO_SETTINGS_MODULE"] = options.DJANGO_SETTINGS

    #import pprint
    #pprint.pprint(options.__dict__)

    if options.TEST:
        _test()
        sys.exit()

    import logging.config

    #logging.basicConfig()
    logging.basicConfig(filename=options.LOGFILE,
                        format='%(asctime)s %(levelname)s %(message)s')
    #logging.config.fileConfig(LOGGING_CONF_FILE)

    log = logging.getLogger('djangoserve')
    dbg = logging.getLogger('djangoserve.Debug')

    if options.DEBUG:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(getattr(logging, options.LOGLEVEL.upper()))
    dbg.setLevel(logging.DEBUG)

    log.info('Starting %s...' % PROGNAME)

    if options.RUN_AS_DAEMON:
        run_as_user  = None
        run_as_group = None
        if options.SERVER_USER:
            run_as_user = options.SERVER_USER
        if options.SERVER_GROUP:
            run_as_group = options.SERVER_GROUP
        daemonize.daemonize(pidfile      = options.PIDFILE,
                            lockfile     = options.LOCKFILE,
                            run_as_user  = run_as_user,
                            run_as_group = run_as_group,
                            workdir      = options.DAEMON_RUN_DIR,
                            log          = log,
                            loggers      = [log, dbg, logging.getLogger()],
                            stdout_log   = log,
                            stderr_log   = log)
        log.info('Daemonized.')

    app = Application(options, args, log = log, dbg_log = dbg)
    app.Run()

if __name__ == '__main__':
    main()
