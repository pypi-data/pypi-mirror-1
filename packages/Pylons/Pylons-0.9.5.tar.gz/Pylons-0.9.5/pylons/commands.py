"""Paster Commands, for use with paster in your project

The command(s) listed here are for use with Paste to enable easy creation of
various core Pylons templates.

Currently available commands are::

    controller, restcontroller, shell
"""
import os
import sys

import paste.fixture
import paste.registry
import paste.deploy.config
from paste.deploy import loadapp, appconfig
from paste.script.command import Command, BadCommand
from paste.script.filemaker import FileOp
from paste.script.pluginlib import find_egg_info_dir

import pylons.util as util

def can_import(name):
    """Attempt to __import__ the specified package/module, returning True when
    succeeding, otherwise False"""
    try:
        __import__(name)
        return True
    except ImportError:
        return False

def validate_name(name):
    """Validate that the name for the controller isn't present on the
    path already"""
    if not name:
        # This happens when the name is an existing directory
        raise BadCommand('Please give the name of a controller.')
    if can_import(name):
        raise BadCommand(
            "\n\nA module named '%s' is already present in your "
            "PYTHON_PATH.\nChoosing a conflicting name will likely cause "
            "import problems in\nyour controller at some point. It's "
            "suggested that you choose an\nalternate name, and if you'd "
            "like that name to be accessible as\n'%s', add a route "
            "to your projects config/routing.py file similar\nto:\n"
            "    map.connect('%s', controller='my_%s')" \
            % (name, name, name, name))
    return True

class ControllerCommand(Command):
    """Create a Controller and accompanying functional test
    
    The Controller command will create the standard controller template
    file and associated functional test to speed creation of controllers.
    
    Example usage::
    
        yourproj% paster controller comments
        Creating yourproj/yourproj/controllers/comments.py
        Creating yourproj/yourproj/tests/functional/test_comments.py
    
    If you'd like to have controllers underneath a directory, just include
    the path as the controller name and the necessary directories will be
    created for you::
    
        yourproj% paster controller admin/trackback
        Creating yourproj/controllers/admin
        Creating yourproj/yourproj/controllers/admin/trackback.py
        Creating yourproj/yourproj/tests/functional/test_admin_trackback.py
    """
    summary = __doc__.splitlines()[0]
    usage = '\n' + __doc__
    
    min_args = 1
    max_args = 1
    group_name = 'pylons'
    
    default_verbosity = 3
    
    parser = Command.standard_parser(simulate=True)
    parser.add_option('--no-test',
                      action='store_true',
                      dest='no_test',
                      help="Don't create the test; just the controller")

    def command(self):
        """Main command to create controller"""
        try:
            file_op = FileOp(source_dir=os.path.join(
                os.path.dirname(__file__), 'templates'))
            try:
                name, directory = file_op.parse_path_name_args(self.args[0])
            except:
                raise BadCommand('No egg_info directory was found')
            
            # Check the name isn't the same as the package
            base_package = file_op.find_dir('controllers', True)[0]
            if base_package.lower() == name.lower():
                raise BadCommand(
                    'Your controller name should not be the same as '
                    'the package name %r.'% base_package
            )
            # Validate the name
            name = name.replace('-', '_')
            validate_name(name)
            
            # Check to see if PROJ.lib.base exists
            try:
                __import__(base_package + '.lib.base')
                importstatement = "from %s.lib.base import *" % base_package
            except:
                # Assume its the minimal template
                importstatement = "from %s.controllers import *" % base_package
            
            # Setup the controller
            fullname = os.path.join(directory, name)
            controller_name = util.class_name_from_module_name(
                name.split('/')[-1])
            if not fullname.startswith(os.sep):
                fullname = os.sep + fullname
            testname = fullname.replace(os.sep, '_')[1:]
            file_op.template_vars.update({'name': controller_name,
                                          'fname': os.path.join(directory, name),
                                          'importstatement': importstatement})
            file_op.copy_file(template='controller.py_tmpl',
                         dest=os.path.join('controllers', directory), 
                         filename=name)
            if not self.options.no_test:
                file_op.copy_file(template='test_controller.py_tmpl',
                             dest=os.path.join('tests', 'functional'),
                             filename='test_'+testname)
        except BadCommand, e:
            raise BadCommand('An error occurred. %s' % e)
        except:
            msg = str(sys.exc_info()[1])
            raise BadCommand('An unknown error occurred. %s' % msg)

class RestControllerCommand(Command):
    """Create a REST Controller and accompanying functional test
    
    The RestController command will create a REST-based Controller file for use
    with the map.resource REST-based dispatching. This template includes the
    methods that map.resource dispatches to in addition to doc strings for
    clarification on when the methods will be called.
    
    The first argument should be the singular form of the REST resource. The 
    second argument is the plural form of the word. If its a nested controller,
    put the directory information in front as shown in the second example
    below.
    
    Example usage::
    
        yourproj% paster restcontroller comment comments
        Creating yourproj/yourproj/controllers/comments.py
        Creating yourproj/yourproj/tests/functional/test_comments.py
    
    If you'd like to have controllers underneath a directory, just include
    the path as the controller name and the necessary directories will be
    created for you::
    
        yourproj% paster restcontroller admin/tracback admin/trackbacks
        Creating yourproj/controllers/admin
        Creating yourproj/yourproj/controllers/admin/trackbacks.py
        Creating yourproj/yourproj/tests/functional/test_admin_trackbacks.py
    """
    summary = __doc__.splitlines()[0]
    usage = '\n' + __doc__
    
    min_args = 2
    max_args = 2
    group_name = 'pylons'
    
    default_verbosity = 3
    
    parser = Command.standard_parser(simulate=True)
    parser.add_option('--no-test',
                      action='store_true',
                      dest='no_test',
                      help="Don't create the test; just the controller")

    def command(self):
        """Main command to create controller"""
        try:
            file_op = FileOp(source_dir=os.path.join(
                os.path.dirname(__file__), 'templates'))
            try:
                singularname, singulardirectory = \
                    file_op.parse_path_name_args(self.args[0])
                pluralname, pluraldirectory = \
                    file_op.parse_path_name_args(self.args[1])
            except:
                raise BadCommand('No egg_info directory was found')
            
            # Check the name isn't the same as the package
            base_package = file_op.find_dir('controllers', True)[0]
            if base_package.lower() == pluralname.lower():
                raise BadCommand(
                    'Your controller name should not be the same as '
                    'the package name %r.'% base_package
            )
            # Validate the name
            for name in [singularname, pluralname]:
                name = name.replace('-', '_')
                validate_name(name)

            # Setup the controller
            fullname = os.path.join(pluraldirectory, pluralname)
            controller_name = util.class_name_from_module_name(
                pluralname.split('/')[-1])
            if not fullname.startswith(os.sep):
                fullname = os.sep + fullname
            testname = fullname.replace(os.sep, '_')[1:]
            
            nameprefix = ''
            if pluraldirectory:
                nameprefix = pluraldirectory.replace(os.path.sep, '_') + '_'
            
            controller_c = ''
            if nameprefix:
                controller_c = ", controller='%s', \n\t" % \
                    '/'.join([pluraldirectory, pluralname])
                controller_c += "path_prefix='/%s', name_prefix='%s_'" % \
                    (pluraldirectory, pluraldirectory)
            command = "map.resource('%s', '%s'%s)\n" % \
                (singularname, pluralname, controller_c)
            
            file_op.template_vars.update(
                {'classname': controller_name,
                 'pluralname': pluralname,
                 'singularname': singularname,
                 'name': controller_name,
                 'nameprefix': nameprefix,
                 'resource_command': command.replace('\n\t', '\n%s#%s' % \
                                                         (' '*4, ' '*9)),
                 'fname': os.path.join(pluraldirectory, pluralname)}
            )
            
            resource_command = ("\nTo create the appropriate RESTful mapping, "
                                "add a map statement to your\n")
            resource_command += ("config/routing.py file near the top like "
                                 "this:\n\n")
            resource_command += command
            file_op.copy_file(template='restcontroller.py_tmpl',
                         dest=os.path.join('controllers', pluraldirectory), 
                         filename=pluralname)
            if not self.options.no_test:
                file_op.copy_file(template='test_controller.py_tmpl',
                             dest=os.path.join('tests', 'functional'),
                             filename='test_'+testname)
            print resource_command
        except BadCommand, e:
            raise BadCommand('An error occurred. %s' % e)
        except:
            msg = str(sys.exc_info()[1])
            raise BadCommand('An unknown error occurred. %s' % msg)


class ShellCommand(Command):
    """Open an interactive shell with the Pylons app loaded
    
    The optional CONFIG_FILE argument specifies the config file to use for
    the interactive shell. CONFIG_FILE defaults to 'development.ini'.
    
    This allows you to test your mapper, models, and simulate web requests
    using ``paste.fixture``.
    
    Example::
        
        $ paster shell my-development.ini
    """
    summary = __doc__.splitlines()[0]
    usage = '\n' + __doc__
    
    min_args = 0
    max_args = 1
    group_name = 'pylons'
    
    parser = Command.standard_parser(simulate=True)

    def command(self):
        """Main command to create a new shell"""
        self.verbose = 3
        if len(self.args) == 0:
            # Assume the .ini file is ./development.ini
            config_file = 'development.ini'
            if not os.path.isfile(config_file):
                raise BadCommand('%sError: CONFIG_FILE not found at: .%s%s\n'
                                 'Please specify a CONFIG_FILE' % \
                                 (self.parser.get_usage(), os.path.sep,
                                  config_file))
        else:
            config_file = self.args[0]
            
        config_name = 'config:%s' % config_file
        here_dir = os.getcwd()
        locs = dict(__name__="pylons-admin")

        # Load app config into paste.deploy to simulate request config
        conf = appconfig(config_name, relative_to=here_dir)
        conf = dict(app_conf=conf.local_conf,
                    global_conf=conf.global_conf)
        paste.deploy.config.CONFIG.push_thread_config(conf)
        
        # Load locals and populate with objects for use in shell
        sys.path.insert(0, here_dir)
        
        # Load the wsgi app first so that everything is initialized right
        wsgiapp = loadapp(config_name, relative_to=here_dir)
        test_app = paste.fixture.TestApp(wsgiapp)
        
        # Query the test app to setup the environment
        tresponse = test_app.get('/_test_vars')
        request_id = int(tresponse.body)

        # Disable restoration during test_app requests
        test_app.pre_request_hook = lambda self: \
            paste.registry.restorer.restoration_end()
        test_app.post_request_hook = lambda self: \
            paste.registry.restorer.restoration_begin(request_id)

        # Restore the state of the Pylons special objects
        # (StackedObjectProxies)
        paste.registry.restorer.restoration_begin(request_id)

        # Determine the package name from the .egg-info top_level.txt.
        egg_info = find_egg_info_dir(here_dir)
        f = open(os.path.join(egg_info, 'top_level.txt'))
        packages = [l.strip() for l in f.readlines()
                    if l.strip() and not l.strip().startswith('#')]
        f.close()

        # Start the rest of our imports now that the app is loaded
        found_base = False
        for pkg_name in packages:
            # Import all objects from the base module
            base_module = pkg_name + '.lib.base'
            found_base = can_import(base_module)
            if not found_base:
                # Minimal template
                base_module = pkg_name + '.controllers'
                found_base = can_import(base_module)

            if found_base:
                models_package = pkg_name + '.models'
                # The Minimal template lacks an official models package
                has_models = can_import(models_package)
                break

        if not found_base:
            raise ImportError("Could not import base module. Are you sure this "
                              "is a Pylons app?") 

        base = sys.modules[base_module]
        base_public = [__name for __name in dir(base) if not \
                       __name.startswith('_') or __name == '_']
        for name in base_public:
            locs[name] = getattr(base, name)
        locs.update(
            dict(
                mapper=tresponse.pylons_config.map,
                wsgiapp=wsgiapp,
                app=test_app,
            )
        )
        if has_models:
            locs['model'] = sys.modules[models_package]

        banner = "  All objects from %s are available\n" % base_module
        banner += "  Additional Objects:\n"
        banner += "  %-10s -  %s\n" % ('mapper', 'Routes mapper object')
        if has_models:
            banner += "  %-10s -  %s\n" % ('model',
                                           'Models from models package')
        banner += "  %-10s -  %s\n" % ('wsgiapp', 
            'This projects WSGI App instance')
        banner += "  %-10s -  %s\n" % ('app', 
            'paste.fixture wrapped around wsgiapp')

        try:
            # try to use IPython if possible
            from IPython.Shell import IPShellEmbed
            
            shell = IPShellEmbed(user_ns=locs)
            shell.set_banner(shell.IP.BANNER + '\n\n' + banner)
            try:
                shell()
            finally:
                paste.registry.restorer.restoration_end()
        except ImportError:
            import code
            
            class CustomShell(code.InteractiveConsole):
                """Custom shell class to handle raw input"""
                def raw_input(self, *args, **kw):
                    """Capture raw input in exception wrapping"""
                    try:
                        return code.InteractiveConsole.raw_input(
                            self, *args, **kw)
                    except EOFError:
                        # In the future, we'll put our own override as needed 
                        # to save models, TG style
                        raise EOFError
            
            newbanner = "Pylons Interactive Shell\nPython %s\n\n" % sys.version
            banner = newbanner + banner
            shell = CustomShell(locals=locs)
            try:
                import readline
            except ImportError:
                pass
            try:
                shell.interact(banner)
            finally:
                paste.registry.restorer.restoration_end()

__all__ = ['ControllerCommand', 'RestControllerCommand', 'ShellCommand']
