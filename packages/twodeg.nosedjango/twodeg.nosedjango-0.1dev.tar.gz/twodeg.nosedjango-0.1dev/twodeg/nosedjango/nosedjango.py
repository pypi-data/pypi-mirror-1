import doctest
import logging
import os
import re

from django.conf import settings
from django.db import connection
from django.test.utils import setup_test_environment, teardown_test_environment

from ConfigParser import SafeConfigParser
from nose.plugins import Plugin

log = logging.getLogger('nose.plugins.nosedjango')

EMAIL_ADDITION = 'test'
SERVER = 'localhost'

class NoseDjango(Plugin):
    """
    Enable to set up django test environment before running all tests, and
    tear it down after all tests.

    Note that your django project must be on PYTHONPATH for the settings file
    to be loaded. The plugin will help out by placing the nose working dir
    into sys.path if it isn't already there, unless the -P
    (--no-path-adjustment) argument is set.
    """
    
    name = 'django'
    ignoreDjangoFiles = re.compile(r'^(manage\.py|.*settings\.py)$')
    
    def add_options(self, parser, env=os.environ):
        # keep copy so we can make our setting in the env we were passed
        self.env = env
        Plugin.add_options(self, parser, env)
        parser.add_option('--django-settings', action='store',
                          dest='django_settings', default=None,
                          help="Set module as the DJANGO_SETTINGS_MODULE"
                          " environment variable.")
        parser.add_option('--no-db', action='store_false',
                          dest='initial_db',
                          help="Do not use a test database - BE CAREFUL")
        
    def configure(self, options, conf):
        from nose.tools import set_trace; set_trace()
        self.verbosity = options.verbosity
        options.enable_plugin_doctest = True
        if not options.doctestExtension:
            options.doctestExtension = ['txt']
        
        Plugin.configure(self, options, conf)
        
        if options.django_settings and self.env is not None:
            self.env['DJANGO_SETTINGS_MODULE'] = options.django_settings

    def begin(self):
        """Create the test database and schema, if needed, and switch the
        connection over to that database. Then call install() to install
        all apps listed in the loaded settings module.
        """

        if self.conf.addPaths:
            from nose.importer import add_path
            map(add_path, self.conf.where)
            old_name = settings.DATABASE_NAME
        
        self.old_name = settings.DATABASE_NAME
        setup_test_environment()
        connection.creation.create_test_db(self.verbosity,
                                           autoclobber=True)#not interactive)
    
    def finalize(self, result=None):
        """Clean up any created database and schema.
        """
        teardown_test_environment()
        connection.creation.destroy_test_db(self.old_name, self.verbosity)
        
    def beforeTest(self, test):
        from django.db import transaction
        transaction.enter_transaction_management()
        transaction.managed(True)
        
    def afterTest(self, test):
        from django.db import transaction
        if transaction.is_dirty():
            transaction.rollback()
        transaction.leave_transaction_management()
    
    def wantDirectory(self, dir):
        """By default we keep doctests and documentation in <app>/doctest"""
        if dir.find('doctest'):
            return True
            
    def wantFile(self, file):
        if self.ignoreDjangoFiles.match(file):
            return False
        
    def wantModule(self, module):
        pass#if hasattr(module, 'models'):
            #return True
    
    def prepareTestCase(self, test):
        """The tests that are found might need some modifcation
        
        Add some handy options to doctests found,
        
        .. todo:: Find out how django.test.testcases.TestCase works now:
            I think transactions are used now, whereas before it flush/restored
        """
        
        if isinstance(test.test, doctest.DocTestCase):
            test.test._dt_optionflags += doctest.ELLIPSIS | \
                                         doctest.REPORT_ONLY_FIRST_FAILURE