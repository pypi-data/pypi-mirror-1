#!/usr/bin/python
# -*- coding: utf-8 -*-
# Generic Paste-based script

try:
    import subprocess
except ImportError:
    from paste.util import subprocess24 as subprocess
from paste.script.command import Command, BadCommand
from paste.deploy.loadwsgi import _loadconfig, _ObjectType
import threading
import atexit
import logging
import sys
import re
import os

class BotApp(_ObjectType):
    name = 'bot'
    config_prefixes = ['bot']
    egg_protocols = ['loader']

APP = BotApp()

class ConfigWrapper(object):
    """
    Hack for keeping config data. Native one is fugly
    """
    def __init__(self, app, base, options, log):
        self.app = app
        self.options = options
        self.global_conf = app.global_conf
        self.local_conf = app.local_conf
        self.base = base
        self.log = log

    def get(self, param, default=None, section=None, qual=None):
        simple = param.rsplit('.', 1)[-1]

        if simple in self.options.__dict__:
            val = self.options.__dict__[simple]
            if not val is None:
                return val

        if param in self.local_conf:
            return self.local_conf[param]

        if default:
            return default
        
        return None


class SimpleBot(Command):
    usage = 'CONFIG_FILE'
    summary = "Pylons script"
    description = """\
    This class provides support for scripts with db/logging routines
    """
    app_name = "simplebot"
    min_args = 0
    takes_config_file = 1
    default_config_file = 'test.conf'
    requires_config_file = True
    default_verbosity = 1
    parser = Command.standard_parser(quiet=True)
    parser.add_option('-d', '--debug',
                      dest='debug',
                      action='store_true',
                      metavar='DEBUG',
                      help="Enable debug output.")

    parser.add_option('--log-file',
                      dest='log_file',
                      metavar='LOG_FILE',
                      help="Save output to the given log file (redirects stdout)")

    parser.add_option('--daemon',
                      dest='daemon',
                      action='store_true',              
                      help="Run in daemon mode")

   
    possible_subcommands = ()
    _scheme_re = re.compile(r'^[a-z][a-z]+:', re.I)
    
    def __init__(self):
        Command.__init__(self, 'SimpleBot')
    
    def command(self):
        if self.requires_config_file:
            if not self.args:
                app_spec = self.default_config_file
                #raise BadCommand('You must give a config file')
            app_spec = self.args[0]
            if (len(self.args) > 1
                and self.args[1] in self.possible_subcommands):
                cmd = self.args[1]
                restvars = self.args[2:]
            else:
                cmd = None
                restvars = self.args[1:]
        else:
            app_spec = ""
            if (self.args
                and self.args[0] in self.possible_subcommands):
                cmd = self.args[0]
                restvars = self.args[1:]
            else:
                cmd = None
                restvars = self.args[:]
                
        vars = self.parse_vars(restvars)
        if not self._scheme_re.search(app_spec):
            app_spec = 'config:' + app_spec            

        base = os.getcwd()

        if self.options.log_file:
            try:
                writeable_log_file = open(self.options.log_file, 'a')
            except IOError, ioe:
                msg = 'Error: Unable to write to log file: %s' % ioe
                raise BadCommand(msg)
            writeable_log_file.close()

        conf_path = app_spec
        if conf_path.startswith('config:'):
            conf_path = app_spec[len('config:'):]
        elif conf_path.startswith('egg:'):
            conf_path = None
        if conf_path:
            conf_path = os.path.join(base, conf_path)
            self.logging_file_config(conf_path)

        self.log = logging.getLogger(__name__)
        self.app = _loadconfig(APP, '', path=conf_path, name=self.app_name, relative_to=None, global_conf=vars)
        self.config = ConfigWrapper(self.app, base, self.options, self.log)
        
        try:
            self.main()
        except (SystemExit, KeyboardInterrupt), e:
            self.cleanup()
            if self.verbose > 1:
                raise
            if str(e):
                msg = ' '+str(e)
            else:
                msg = ''
            print 'Exiting%s (-v to see traceback)' % msg

    def main(self):
        self.log.info("This is stub method, you should implement it for subclass")

    def cleanup(self):
        """
        Stub, should be subclassed if cleanup is needed.
        """
        return True

    @classmethod
    def run_script(cls, args=None):
        command = cls()
        if args is None:
            args = sys.argv[1:]
        exit_code = command.run(args)
        

if __name__ == "__main__":
    SimpleBot.run_script()
