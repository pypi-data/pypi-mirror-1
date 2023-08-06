"""Skeleton script for use as a TG paster command base"""
import os, sys,time
from datetime import datetime
import logging, traceback
from paste.script.command import Command
from paste.deploy import appconfig
from sqlalchemy import engine_from_config
import transaction

log = logging.getLogger( 'commands.basecommand' )
log.setLevel( logging.INFO )

class TGCommand(Command):
    """Provides SQLAlchemy session and TurboGears config setup 
    """
    # Parser configuration
    summary = "" # override this...
    usage = "" # override this if you don't want auto-generated
    group_name = "local" # you can override this if you want to separate your commands out in the paster help listing
    
    # Many "simple" commands can just use this parser, but 
    # sub-classes can create new parsers and call 
    # standard_options( parser ) to get the basic option parsing 
    # code working.
    parser = Command.standard_parser(verbose=False)
    def standard_options( parser, default_config='development.ini', default_pid='' ):
        parser.add_option(
            '--config', 
            action='store', 
            dest='config', 
            help='Specify the config file to use for the command',
            default=default_config,
        )
        parser.add_option(
            '--verbose-log', 
            action='store_true', 
            default = False,
            dest='verbose_log', 
            help='Use verbose logging',
        )
        parser.add_option(
            '--pidfile', 
            action='store', 
            dest='pidfile', 
            help='Specify the pidfile to check/write (intended for use in cron scripts to prevent "cron-bombs")', 
            default=default_pid
        )
    # Staticmethods aren't callable directly...
    standard_options( parser )
    # so we wrap it here...
    standard_options = staticmethod( standard_options )
    
    log_level = logging.WARN
    verbose_log_level = logging.INFO
    with_session = True
    _temp_connection = None
    
    def import_model( self ):
        """Import our project's "model" module
        
        Override this (once) for your entire project, then use the 
        class that overrides it as your base-class for commands.
        
        model module must have:
        
            init_model
            metadata
            DBSession
        
        attributes.
        """
        
        # from project import model
        # return model 
    
    def get_session( self, engine ):
        """Imports project schema and binds to the engine"""
        model = self.import_model()
        # Hack to get package name
        self.config['pylons.package'] = model.__name__.split('.')[0]
        model.init_model( engine )
        model.metadata.bind = engine
        return model.DBSession
    def temp_connection( self, engine=None ):
        """Create a temporary (side) connection (w/ trans) to the database
        
        returns connection,transaction
        """
        if engine is None:
            engine = engine_from_config(self.config, 'sqlalchemy.')
        conn = engine.connect()
        trans = conn.begin()
        return conn, trans
    
    def create_pid( self ):
        """Create PID file for our process"""
        if self.options.pidfile:
            if os.path.exists( self.options.pidfile ):
                log.error( 
                    "Exiting, pidfile %s exists", 
                    self.options.pidfile 
                )
                sys.exit( 1 )
                return 
            # Technically a race condition here...
            log.debug( 'Creating PID: %s', self.options.pidfile )
            pidfile = open( self.options.pidfile, 'w')
            pidfile.write( str(os.getpid()))
            pidfile.flush()
            return pidfile
        return None
    
    def get_config( self ):
        """Retrieve our TurboGears configuration file from opts/args"""
        if self.options.config:
            config = self.options.config
        elif self.args:
            config = self.args[0]
        else:
            config = None
        if not config:
            log.error(
                "Missing config file. Please supply it."
            )
            sys.stderr.write( self.parser.format_help() )
            sys.stderr.write( '\n' )
            sys.exit(1)
        cfgpath = os.path.abspath(config)
        if not os.path.exists(config):
            log.error(
                "Config file %s does not exist. Please supply it.",
                cfgpath
            )
            sys.stderr.write( self.parser.format_help() )
            sys.stderr.write( '\n' )
            sys.exit(1)
        cfg = self.config = appconfig('config:%s' % (cfgpath))
        import tg
        tg.config.update( cfg )
        return cfg
    def command(self):
        """Our core command operation"""
        if self.options.verbose_log:
            logging.basicConfig( level=self.verbose_log_level )
            log.debug( 'Verbose log enabled' )
        else:
            logging.basicConfig( level=self.log_level )
        start = time.time()
        pidfile = self.create_pid()
        try:
            cfg = self.get_config()
            engine = engine_from_config(cfg, 'sqlalchemy.')
            self.setup_il8n( cfg )
            if self.with_session:
                DBSession = self.get_session( engine )
            else:
                DBSession = None
            try:
                self.db_command( engine )
            except Exception, err:
                if DBSession:
                    DBSession.rollback()
                    log.warn( 'Rollback of transaction' )
                raise
            else:
                if self.with_session:
                    transaction.commit()
                    log.info( 'Transaction committed' )
            if DBSession:
                DBSession.close()
        finally:
            if pidfile:
                pidfile.close()
                log.debug( 'Removing PID lock-file' )
                os.remove( self.options.pidfile )
            log.info( 'Total time: %0.1fs', time.time()-start )
        
    def setup_il8n( self, config ):
        """Setup internationalization parameters"""
        if 'lang' in config:
            # Get a translator up to make i18n work
            log.debug( 'Setting up i18n ' )
            kw = {
                'pylons_config': { 
                    'pylons.paths' : {
                        'root': os.path.join(
                            config['here'], 
                            config['pylons.package']
                        ) 
                    }, 
                    'pylons.package': config['pylons.package']
                }
            }
            # This assumes that lang is set in the .ini
            import pylons
            from pylons.i18n.translation import _get_translator
            pylons.translator._push_object(
                _get_translator(config['lang'], **kw)
            )

    def db_command( self, engine ):
        """Override to perform our DB-requiring operation here
        
        Exceptions will rollback otherwise will commit on 
        return.  Note that you should *not* import your project's
        model until you enter this method.  That is, your sub-class
        should not import the model objects at the top of their 
        modules, as that would attempt to create a DBSession.
        """
        raise NotImplemented( """db_command not implemented""" )
