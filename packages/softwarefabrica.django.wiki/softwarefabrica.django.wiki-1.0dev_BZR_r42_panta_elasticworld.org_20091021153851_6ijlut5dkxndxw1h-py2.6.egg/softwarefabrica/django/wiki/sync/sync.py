#!/usr/bin/env python
# ex:ts=8:sw=4:sts=4:et
# -*- tab-width: 8; c-basic-offset: 4; indent-tabs-mode: t -*-
#
# Copyright (C) 2008 Marco Pantaleoni. All rights reserved

"""
sf-wiki-sync

Tool to synchronize two (or more) softwarefabrica wikis across multiple
machines.
This is almost a more general automatic django database
synchronization tool.

This utility symmetrically synchronizes two (possibily remote) django
databases, bringing both of them to the same state.
It's useful for keeping up to date multiple sites used independently
(for example: a central server and a road warrior used off-line).
For this program to work, the databases must follow some rules:

   * every table must have a 'uuid' field of type UUIDField()
     as its primary key
   * every table must have a 'created' field of type
     models.DateTimeField() with the date and time of record
     creation

To generate documentation for this program, use epydoc.
To perform doctests, invoke with '-t'.
To get help, invoke with '-h'.

@author: Marco Pantaleoni
@contact: Marco Pantaleoni <panta@elasticworld.org>
@contact: Marco Pantaleoni <marco.pantaleoni@gmail.com>
@copyright: Copyright (C) 2008 Marco Pantaleoni. All rights reserved.

@see: ...


@todo: handle deletions
@todo: add attachment/upload processing
@todo: add config file support
@todo: add daemon support
@todo: command-line option parsing
@todo: write doctests
"""

import sys, os, getopt
import datetime
import optparse

import signal as unixsignal
import logging

from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey, types, create_engine
from sqlalchemy.orm import mapper, relation, backref, create_session, sessionmaker


PROGNAME    = "sf-wiki-sync"
__version__ = "1.0.0"
__svnid__   = "$Id$"
__license__ = "GPL"
__author__  = "Marco Pantaleoni <panta@elasticworld.org>"


# # -- calculate project root ----------------------------------------------

# this_mod = __import__(__name__)
# CUR_DIR  = os.path.abspath(os.path.dirname(this_mod.__file__))

from softwarefabrica.django.wiki import version

# # -- Defaults ------------------------------------------------------------

DEFAULT_CONFIG_FILE    = "/etc/sf-wiki-sync.conf"
DEFAULT_DATABASE1_DSN  = 'sqlite:///testproj_1.db'
DEFAULT_DATABASE2_DSN  = 'sqlite:///testproj_2.db'
LOGGING_CONF_FILE      = os.path.join(os.path.dirname(__file__), 'wiki-sync-log.conf')

# -- Constants -----------------------------------------------------------

VERBOSITY_QUIET   = 0
VERBOSITY_NORMAL  = 1
VERBOSITY_VERBOSE = 2
VERBOSITY_DEBUG   = 3

# -- Globals -------------------------------------------------------------

log = logging.getLogger('DjangoSync')
dbg = logging.getLogger('DjangoSync.Debug')

LAST_SYNC = datetime.datetime(2008, 9, 2)

TABLE_NAMES = ['wiki_wiki',
               'wiki_page',
               'wiki_pagecontent',]


#============================================================================#
# Utility functions
#============================================================================#

def sa_record2dict(obj):
    d = {}
    for k, v in obj.items():
        d[k] = v
    return d

#============================================================================#
# Application class
#============================================================================#

class Application(object):
    """
    A singleton class implementing the application.
    """

    _instance = None

    def __init__(self, options, args):
        if self._instance:
            raise "An instance of this singleton has already been created."
        Application._instance = self
        self.options = options
        self.args = args

        self.cwd = None			# original working dir

        self.engine_1 = None
        self.engine_2 = None
        self.metadata = None
        self.table_names = TABLE_NAMES
        self.tables   = None

        self.last_sync = LAST_SYNC

    def Instance(cls):
        return cls._instance
    Instance = classmethod(Instance)

    def log(self, msg, verb=VERBOSITY_VERBOSE):
        if verb <= self.options.verbosity:
            log.info(msg)
        return self

    def dbg(self, msg, verb=VERBOSITY_DEBUG):
        if verb <= self.options.verbosity:
            log.debug(msg)
        return self

    def warn(self, msg):
        m = "WARNING: %s" % msg
        sys.stderr.write("%s\n" % m)
        log.warn(msg)
        return self

    def err(self, msg):
        m = "ERROR: %s" % msg
        sys.stderr.write("%s\n" % m)
        log.error(msg)
        return self

    def wait(self, t_next):
        """
        wait until the specified time.
        
        @type t_next:    datetime.datetime
        @param t_next:   absolute time to wait for
        """
        t_now = datetime.datetime.now()
        if t_now >= t_next:
            return
        td = t_next - t_now
        seconds = td.days * 3600L * 24L + long(td.seconds)
        self.log("waiting for %s (%s minutes)" % (t_next, int(seconds / 60.0)), VERBOSITY_NORMAL)
        if seconds > 0:
            time.sleep(seconds)
        return self

    def Run(self):
        """
        Actual program execution happens here. 
        """

        self.log("Program started.")

        self.cwd = os.getcwd()

        self.engine_1 = create_engine(self.options.database1)
        self.engine_2 = create_engine(self.options.database2)

        self.metadata = MetaData()

        self.sync_all(self.table_names)

        os.chdir(self.cwd)
        self.log("Program terminating...")
        return self

    def sync_table_directed(self, src_engine, dst_engine, table):
        s1 = table.select().where(table.c.created > self.last_sync)
        result = src_engine.execute(s1)
        for r in result:
            s2 = table.select().where(table.c.uuid == r.uuid)
            r2 = dst_engine.execute(s2).fetchone()
            if r2 == None:
                self.warn("record %s found in %s but not in %s" % (r.uuid, src_engine, dst_engine))
                #self.dbg("uuid:%s %s -> %s" % (r.uuid, r, r2))
                p = sa_record2dict(r)
                ins = table.insert(values = p)
                #self.dbg("q: %s" % str(ins))
                self.dbg(ins.compile().params)
        return self

    def sync_table(self, table):
        self.log("\nSYNCING TABLE %s" % table)
        self.sync_table_directed(self.engine_1, self.engine_2, table)
        self.sync_table_directed(self.engine_2, self.engine_1, table)
        return self

    def sync_all(self, table_names = None):
        table_names = table_names or self.table_names
        self.tables = {}

        for table_name in table_names:
            table = Table(table_name, self.metadata, autoload=True, autoload_with=self.engine_1)
            self.tables[table_name] = table

        for table_name in table_names:
            table = self.tables[table_name]
            self.sync_table(table)
        return self

def exithandler(signum, frame):
    """
    Handles (gracefully) termination signals.
    """

    app = Application.Instance()

    log.info('Exiting with signal %s' % signum)

    # handle graceful exit

##    if app.options.daemon:
##        log.info("removing lockfile and PID file")
##        if app.options.lockfile and os.path.exists(app.options.lockfile):
##            os.remove(app.options.lockfile)
##        if app.options.pidfile and os.path.exists(app.options.pidfile):
##            os.remove(app.options.pidfile)

    log.info("exiting.")
    sys.exit(1)

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

    parser = optparse.OptionParser( version = "softwarefabrica Wiki Synchronization (%%prog) version %s (lib %s)" % (__version__, version.get_version()),
                                    usage = """%prog [options]

Synchronizes two softwarefabrica wikis.

Example invocations:

  # %prog -v -1 sqlite:////var/db/wiki.db -2 mysql://user:password@localhost/wiki

  # %prog -v -1 sqlite:///wiki.db -2 mysql://user:password@localhost/wiki
""" )

    parser.add_option( "-c", "--config",
                       help = "use FILE as the configuration file (default: %s)" % repr(DEFAULT_CONFIG_FILE),
                       action = "store", dest = "configfile",
                       default = DEFAULT_CONFIG_FILE, metavar = "FILE" )
    parser.add_option( "-1", "--dsn-1", "--dsn-one", "--database-1", "--database-one",
                       help = "specify DSN as the first database (default: %s)" % repr(DEFAULT_DATABASE1_DSN),
                       action = "store", dest = "database1",
                       default = DEFAULT_DATABASE1_DSN, metavar = "DSN" )
    parser.add_option( "-2", "--dsn-2", "--dsn-two", "--database-2", "--database-two",
                       help = "specify DSN as the second database (default: %s)" % repr(DEFAULT_DATABASE2_DSN),
                       action = "store", dest = "database2",
                       default = DEFAULT_DATABASE2_DSN, metavar = "DSN" )
    parser.add_option("-q", "--quiet",
                      action="store_const", dest="verbosity", const=VERBOSITY_QUIET, default=VERBOSITY_NORMAL,
                      help="don't print anything on stdout")
    parser.add_option("-v", "--verbose",
                      action="store_const", dest="verbosity", const=VERBOSITY_VERBOSE,
                      help="be verbose")
    parser.add_option("-d", "--debug",
                      action="store_const", dest="verbosity", const=VERBOSITY_DEBUG,
                      help="be too verbose (debugging only)")
    parser.add_option( "-t", "--test", help = "perform internal testing.",
                       action = "store_true", dest = "test", default = False )

    options, args = parser.parse_args( sys.argv )

    if options.test:
        _test()
        sys.exit()

    import logging.config

    #logging.basicConfig()
    logging.config.fileConfig(LOGGING_CONF_FILE)
    log.info('Starting %s...' % PROGNAME)

    try:
        unixsignal.signal(unixsignal.SIGINT,  exithandler)
    except:
        pass
    try:
        unixsignal.signal(unixsignal.SIGQUIT, exithandler)
    except:
        pass
    try:
        unixsignal.signal(unixsignal.SIGTERM, exithandler)
    except:
        pass
    try:
        unixsignal.signal(unixsignal.SIGKILL, exithandler)
    except:
        pass

    if not options.database1:
        sys.stderr.write("ERROR: specify the first database\n")
        sys.exit(1)

    if not options.database2:
        sys.stderr.write("ERROR: specify the second database\n")
        sys.exit(1)

    app = Application(options, args)
    app.Run()
    return 0                            # make setuptools application wrapper happy

if __name__ == '__main__':
    main()

#wiki_table        = Table('wiki_wiki', metadata, autoload=True, autoload_with=engine_1)
#page_table        = Table('wiki_page', metadata, autoload=True, autoload_with=engine_1)
#pagecontent_table = Table('wiki_pagecontent', metadata, autoload=True, autoload_with=engine_1)
#
#sync_table(engine_1, engine_2, wiki_table)
