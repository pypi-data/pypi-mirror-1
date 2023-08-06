# -*- coding: utf-8 -*-

# This file is part of the "Cleverbox" program.
#
# Cleverbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Cleverbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Cleverbox.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2008, Tristan Rivoallan

import shutil
import cmd
import os
import shlex
import sys
import traceback
import re
from trac import util
from trac.scripts.admin import TracAdmin
import ConfigParser
from pkg_resources import parse_version

_defaults = {
    'env_dir_layout'    : ('clients-available', 'clients-enabled',
                           'projects-available', 'projects-enabled',
                           'profiles/default'),
    'client_dir_layout' : ('htdocs', 'logs', 'tmp', 'uploads',
                           'var/svn', 'var/trac'),
    'profile_files'     : ('project.apache.conf', 'trac-defaults.ini', 'permissions.ini')
}

_version = '0.4.4'

class CleverboxAdmin(cmd.Cmd):
    intro = ''
    license = ''
    doc_header = 'Cleverbox Admin Console \n' \
                 'Available Commands:\n'
    ruler = ''
    prompt = "Cleverbox > "
    envname = None
    __env = None
    _date_format = '%Y-%m-%d'
    _datetime_format = '%Y-%m-%d %H:%M:%S'
    _date_format_hint = 'YYYY-MM-DD'

    _config = None

    def __init__(self, envdir = None):
        cmd.Cmd.__init__(self)
        if envdir:
            self.env_set(os.path.abspath(envdir))
        self.interactive = False

    ##
    ## Environment methods
    ##

    def env_set(self, envname, env=None):
        self.envname = envname
        self.prompt = "Cleverbox [%s] > " % self.envname

        # Check if environment needs an upgrade
        #  - open VERSION
        try:
            import trac
            if trac.__version__ == '0.10.3':
                print
                print "A bug in trac-0.10.3 prevents the cleverbox from working correctly."
                print "Please upgrade or downgrade your trac installation."
                print

                sys.exit(1)

            env_version = open(os.path.join(self.envname, 'VERSION')).read().strip()

            #  - compare with self._version
            #  - if VERSION < self._version :
            if parse_version(env_version) < parse_version(_version):
                print "\nCleverbox environment needs to be upgraded. Please run :"
                print "  cleverbox-admin %s upgrade\n" % self.envname
                sys.exit(1)
        except IOError, e:
            # no VERSION file means user wants to create an environment
            pass

        if env is not None:
            self.__env = env

        # Read configuration
        self._config = ConfigParser.SafeConfigParser()
        self._config.read(os.path.join(self.envname, 'cleverbox.ini'))


    def env_check(self):
        try:
            pass
            #self.__env = Environment(self.envname)
        except:
            return 0
        return 1

    def env_open(self):
        try:
            if not self.__env:
                #self.__env = Environment(self.envname)
                return self.__env
        except Exception, e:
            print 'Failed to open environment.', e
            traceback.print_exc()
            sys.exit(1)

    def emptyline(self):
        pass

    def onecmd(self, line):
        try:
            rv = cmd.Cmd.onecmd(self, line) or 0
        except SystemExit:
            raise
        except Exception, e:
            print >> sys.stderr, 'Command failed: %s' % e
            rv = 2
        if not self.interactive:
            return rv

    def run(self):
        self.interactive = True
        print 'Welcome to cleverbox-admin v%s\n'                \
              'Interactive Cleverbox administration console.\n'       \
              "Type:  '?' or 'help' for help on commands.\n" % _version
        self.cmdloop()

    #
    # Configuration related methods
    #
    def getConfig(self, directive, section):
        try:
            val = self._config.get(section, directive)
        except ConfigParser.NoOptionError, exception:
            val = ''
        return val

    #
    # Commands
    #

    ## Environment
    _help_initenv = [('initenv', 'Environment initialisation')]
    def do_initenv(self, line=None):
        print "Environment initialisation in %(env_dir)s" % {'env_dir' : self.envname}

        # Collect local configuration info
        collected_infos = {}

        # Path to client dir
        default_root = '/var/cleverbox'
        collected_infos['clients_root'] = raw_input('Projects directory [%s]> ' % default_root).strip() or default_root

        # Path to cleverbox assets
        default_assets_dir = '/usr/share/cleverbox'
        collected_infos['assets_dir'] = raw_input('Cleverbox assets directory [%s]> ' % default_assets_dir).strip() or default_assets_dir

        try :
            os.makedirs(collected_infos['clients_root'], 0775)
        except IOError, ioexception :
            print ioexception
            print "** Projects storage dir could not be created."

        # Apache user & group
        d_uid = 33
        d_gid = 33
        collected_infos['apache_user'] = raw_input('Webserver user id [%d]> ' % d_uid).strip() or d_uid
        collected_infos['apache_group'] = raw_input('Webserver group id [%d]> ' % d_gid).strip() or d_gid

        # root user & group
        # we keep the ssh_user notion for backward compatibility.
        # this will have to disappear in a future release
        collected_infos['ssh_user'] = 0
        collected_infos['ssh_group'] = 0

        # Host server domain name
        collected_infos['domain'] = raw_input('Domain name > ').strip()

        # Authentication backend password (if any)
        collected_infos['authbackend_pass'] = raw_input('Authentication backend password (if any) []> ').strip() or ''

        # Default configuration profile
        dcp = 'default'
        collected_infos['default_profile'] = raw_input('Default configuration profile [%s]> ' % dcp).strip() or dcp

        # Write ini file
        self._config.add_section('general')
        for directive, value in collected_infos.items() :
            self._config.set('general', directive, str(value))

        trac_infos = {}
        d_lib_dir = '/usr/share/python-support/trac'
        trac_infos['lib_dir'] = raw_input('Trac libs directory [%s]> ' % d_lib_dir).strip() or d_lib_dir

        d_assets_dir = '/usr/share/trac'
        trac_infos['assets_dir'] = raw_input('Trac assets directory [%s]> ' % d_assets_dir).strip() or d_assets_dir

        self._config.add_section('trac')
        for directive, value in trac_infos.items() :
            self._config.set('trac', directive, str(value))

        fh_config = open(os.path.join(self.envname, 'cleverbox.ini'), 'w+')
        self._config.write(fh_config)

        # Create directory structure
        try:
            print "\n\tCreating directory layout\n"
            env_dirs = []
            for dirname in _defaults['env_dir_layout']:
                env_dirs.append( os.path.join(self.envname, dirname) )
            map( os.makedirs, env_dirs )
        except IOError, ioexception :
            print ioexception
            print "** Environment couldn't be initialized in %(env_dir)s\n" % {'env_dir' : self.envname}

        # Create VERSION file
        try:
            print "\n\tCreating VERSION file\n"
            fd = open( os.path.join(self.envname, 'VERSION'), 'w' )
            fd.write(_version)
        finally:
            fd.close()

        # Default configuration profile
        print "\n\tCreating default configuration profile\n"
        for filename in _defaults['profile_files']:
            shutil.copy(collected_infos['assets_dir'] + '/' + filename, os.path.join(self.envname, 'profiles', 'default'))


        print
        print "Environment successfully initialized\n"
        print "You need to add this statement to your apache configuration : \n" \
            "\t'Include %(env_dir)s/clients-enabled/*'\n" % {'env_dir' : self.envname}

    _help_upgrade = [('upgrade', 'Executes necessary operation to make environment up to date')]
    def do_upgrade(self, line=None):
        env_version = open(os.path.join(self.envname, 'VERSION')).read()
        if parse_version(env_version) < parse_version(_version):
            from cleverbox.upgrades import upgrades
            i = 1
            while i:
                try:
                    upgrade_func = getattr(upgrades, 'do_upgrade_' + str(i))
                    upgrade_func.__call__(self.envname, env_version)
                except AttributeError, e:
                    break
                i = i + 1


    ## help
    def do_help(self, line=None):
        arg = self._arg_tokenize(line)

        if arg[0]:
            try:
                doc = getattr(self, "_help_" + arg[0])
                TracAdmin.print_doc(doc)
            except AttributeError:
                print "No documentation found for %s" % arg[0]
        else:
            docs = (self._help_client + self._help_project + self._help_initenv + self._help_upgrade)
            print 'cleverbox-admin - The Cleverbox Administration Console v%s' % _version
            if not self.interactive:
                print
                print "Usage: cleverbox-admin env_dir [command [subcommand] [option ...]]\n"
                print "Invoking cleverbox-admin without command starts "\
                      "interactive mode."
            TracAdmin.print_doc(docs)


    #
    # "Client" command set
    #
    _help_client = [('client list', 'Lists available clients'),
                    ('client add <name>', 'Adds a client'),
                    ('client remove <name>', 'Deletes a client'),
                    ('client enable <name>', 'Enables a client'),
                    ('client disable <name>', 'Disables a client')]
    def do_client(self, line):
        args = self._arg_tokenize(line)
        if args[0] == 'list':
            self._do_client_list()
        elif args[0] == 'add' and len(args) == 2:
            self._do_client_add(args[1])
        elif args[0] == 'remove' and len(args) == 2:
            self._do_client_remove(args[1])
        elif args[0] == 'enable' and len(args) == 2:
            self._do_client_enable(args[1])
        elif args[0] == 'disable' and len(args) == 2:
            self._do_client_disable(args[1])
        else:
            self.do_help('client')


    def complete_client(self, text, line, begidx, endidx):
        '''
        Completions for the client command.
        Each client subcommand has its own completion command, named _complete_client_<subcommand>
        '''

        comp = ['list', 'add', 'remove', 'enable', 'disable']
        parts = self._arg_tokenize(line)

        if len(parts) > 1 and parts[1] in comp:
            complete_func = getattr(self, '_complete_client_' + parts[1])
            if (float(sys.version[:3]) < 2.4):
                comp = complete_func.__call__(self)
            else:
                comp = complete_func.__call__()

        return self.word_complete( text, comp )


    def _do_client_list(self):
        '''
        Displays enabled and disabled clients.
        '''

        print "Enabled :\n" \
              "%s\n\n" \
              "Disabled : \n" \
              "%s\n" % (self._get_clients('enabled'), self._get_clients('disabled'))

    def _do_client_add(self, client_name):
        """
        Creates a new client.
          * Checks if client not already exists.
          * Collects informations about client
          * Checks informations are correct
          * Create clients environment directory layout
          * Creates apache conf for apache
          * Inserts client into LDAP
        """

        if not self._client_exists(client_name):

            # Client name cannot contain strokes
            if client_name.count('-') != 0:
                print "** Client's identifier can not contain the '-' character."
                return

            # Information collection
            collected_infos = { 'full_name'    : None,
                                'home_dir'     : None,
                                'ftp_password' : None }

            collected_infos['home_dir'] = os.path.join(self.getConfig('clients_root', 'general'), client_name)

            # A few checks before effectively creating client
            # -- homedir
            parent_dir = os.path.normpath(os.path.join(collected_infos['home_dir'], os.pardir))
            dir_is_ok = os.access(parent_dir, os.W_OK) and not os.access(collected_infos['home_dir'], os.R_OK)
            if not dir_is_ok:
                print "Directory %s is not writable or already exists, aborting." % collected_infos['home_dir']
                raise os.error


            print
            print "Creating a new client."
            print "Let's collect some informations about him : "
            print
            print "  Please enter client's full name."
            print "  This will be used in several interface screens and in emails."
            print

            dfn = client_name.capitalize()
            collected_infos['full_name'] = raw_input('Full Name [%s]> ' % dfn).strip() or dfn

            print
            print "Supplied informations verified."
            print "Let's proceed with client creation :"
            print

            # Client creation
            # -- Homedir layout
            homedir_layout = []
            for d in _defaults['client_dir_layout']:
                homedir_layout.append( os.path.join(collected_infos['home_dir'], d) )
            map( os.makedirs, homedir_layout )

            print "  Directory layout created in %s\n" % collected_infos['home_dir']

            # -- Apache configuration
            apache_conf = """
# -- Include enabled projects configuration files
Include %(env_dir)s/projects-enabled/%(client_name)s-*
""" % { 'client_name' : client_name,
        'home_dir'    : collected_infos['home_dir'],
        'env_dir'     : self.envname }

            # -- Write conf to filesystem
            apache_conf_filepath = os.path.join( self.envname, 'clients-available', client_name )
            f = file(apache_conf_filepath, 'w+')
            f.write(apache_conf)
            f.close()

            print "  Apache configuration written to %s\n" % apache_conf_filepath

            # -- Fix permissions
            """
            chown -R dev:dev /$CLIENTSROOT/$CLIENTNAME
            chown dev:www-data /$CLIENTSROOT/$CLIENTNAME/logs
            chmod g+w /$CLIENTSROOT/$CLIENTNAME/logs
            chown dev:www-data /$CLIENTSROOT/$CLIENTNAME/uploads
            chmod g+w /$CLIENTSROOT/$CLIENTNAME/uploads
            """
            self._rchown( collected_infos['home_dir'],
                         int(self.getConfig('ssh_user', 'general')),
                         int(self.getConfig('ssh_group', 'general')) )
            os.chown( os.path.join(collected_infos['home_dir'], 'logs'),
                     int(self.getConfig('ssh_user', 'general')), int(self.getConfig('apache_group', 'general')) )
            os.chmod( os.path.join(collected_infos['home_dir'], 'logs'), 0775 )
            os.chown( os.path.join(collected_infos['home_dir'], 'uploads'),
                     int(self.getConfig('ssh_user', 'general')), int(self.getConfig('apache_group', 'general')) )
            os.chmod( os.path.join(collected_infos['home_dir'], 'uploads'), 0775 )
            os.chown( os.path.join(collected_infos['home_dir'], 'tmp'),
                     int(self.getConfig('ssh_user', 'general')), int(self.getConfig('apache_group', 'general')) )
            os.chmod( os.path.join(collected_infos['home_dir'], 'tmp'), 0775 )

            print "  Fixed permissions in %s\n" % collected_infos['home_dir']

            #  Final steps
            # -- Enable client ?
            print "Client has been created. Do you want to enable it ?"
            print
            enable_client = raw_input('Enable client ? [y/N]> ').strip() or False

            if enable_client == 'y':
                self._do_client_enable(client_name)

            print
            print "Client %s was successfully created." % collected_infos['full_name']
            print "Apache configuration need to be reloaded for this to be effective."
            print
            print "You may want create some projects now. Try 'help project' for some documentation."
            print

        else:
            print "This client already exists !"

    def _do_client_remove(self, client_name):
        """
        Suppression d'un client.
        Un client actif ne peut être supprimé.
        TODO : suppression du répertoire du client. (bof)
        """

        if self._client_exists(client_name):
            continue_removal = False
            print "You are about to remove client '%s'." % client_name
            confirm_removal = raw_input('Remove client ? [y/N]> ').strip() or False
            if confirm_removal == 'y':
                continue_removal = True

            if not continue_removal:
                print "Client '%s' was *not* removed" % client_name
                return

            # Client is enabled, propose disabling it
            client_disabled = True
            if client_name in self._get_clients('enabled'):
                client_disabled = False
                print "You can not remove an enabled client. Disabling it."
                try:
                    self._do_client_disable(client_name)
                except Exception, e:
                    print e

            # Disable client's projects
            for project_name in self._get_projects(client_name, 'enabled'):
                self._do_project_disable((client_name, project_name))

            # Disable client
            client_apacheconf = os.path.join( self.envname, 'clients-available', client_name )
            os.unlink(client_apacheconf)
            print "Client '%s' has been removed." % client_name
            print "Apache configuration needs to be reloaded for this to be effective."
        else:
            print "This client does not exist !"

    def _do_client_enable(self, client_name):
        enable_client = True
        if not self._client_exists(client_name):
            print "This client does not exist !"
            enable_client = False

        if client_name in self._get_clients('enabled'):
            print "This client is already enabled !"
            enable_client = False

        if enable_client:
            target = os.path.join( self.envname, 'clients-available', client_name )
            linkname = os.path.join( self.envname, 'clients-enabled', client_name )
            os.symlink( target, linkname )
            print "Client '%s' has been enabled" % client_name
            print "Apache configuration needs to be reloaded for this to be effective."
        else:
            print "Client '%s' was *not* enabled" % client_name

    def _do_client_disable(self, client_name):
        """
        Disables a client.
        TODO : disable client's projects.
        """
        disable_client = True
        if not self._client_exists(client_name):
            print "This client does not exist !"
            disable_client = False

        if client_name in self._get_clients('disabled'):
            print "This client is already disabled !"
            disable_client = False

        if disable_client:
            linkname = os.path.join( self.envname, 'clients-enabled', client_name )
            os.unlink( linkname )
            print "Client '%s' has been disabled" % client_name
            print "Apache configuration needs to be reloaded for this to be effective."
        else:
            print "Client '%s' was *not* disabled" % client_name


    def _complete_client_remove(self):
        return self._get_clients()

    def _complete_client_enable(self):
        return self._get_clients('disabled')

    def _complete_client_disable(self):
        return self._get_clients('enabled')


    def _client_exists(self, name):
        """
        Tells whether or not a client exists.
        return bool
        """
        return name in self._get_clients()

    def _get_clients(self, only = False):
        '''
        Returns a list of clients.
        The "only" parameter is used to restrict returned clients list. Recognized values are "enabled" and "disabled".
        '''

        list_clients = []

        # Each client
        if not only:
            list_clients = os.listdir(os.path.join(self.envname, 'clients-available'))

        # Only enabled clients
        elif only == 'enabled':
            list_clients = os.listdir(os.path.join(self.envname, 'clients-enabled'))

        # Only disabled clients (ie. not enabled)
        elif only == 'disabled':

            disabled_clients = []
            available_clients = os.listdir(os.path.join(self.envname, 'clients-available'))
            enabled_clients = os.listdir(os.path.join(self.envname, 'clients-enabled'))

            # Expect poor performances for this intersection algorithm
            # see http://python.project.cwi.nl/search/hypermail/python-recent/0159.html
            for e in available_clients:
                if e not in enabled_clients:
                    disabled_clients.append(e)

            list_clients = disabled_clients

        return list_clients


    #
    # Project command set
    #

    _help_project = [('project list', 'Lists available projects'),
                    ('project add <client> <name>', 'Adds a project'),
                    ('project remove <client> <name>', 'Deletes a project'),
                    ('project enable <client> <name>', 'Enables a project'),
                    ('project disable <client> <name>', 'Disables a project')]
    def do_project(self, line):
        parts = self._arg_tokenize(line)
        try:
            do_func = getattr(self, '_do_project_' + parts[0])
            # Python __call__() signature changed in Python2.4
            if ( sys.version[:3] == '2.4'):
                do_func.__call__(parts[1:])
            else:
                do_func.__call__(self, parts[1:])
        except AttributeError, e:
            print e
            self.do_help('project')

    def _do_project_list(self, line=None):
        """
        TODO : Nicer formatting
        """

        print
        print "Available projects :"
        print "--------------------"

        client_projects = {}

        clients = self._get_clients()
        for client_name in clients:
            client_projects[client_name] = self._get_projects(client_name)

        print client_projects


    def _project_exists(self, client_name, project_name, project_status = None):
        return project_name in self._get_projects(client_name, project_status)

    def _get_projects(self, client_name = None, status = None):
        """
        TODO : Extend command options in order to provide better filtering (client, enabled / disabled)
        """
        list_projects = []

        # -- List of requested projects
        enabled_projects_dir = 'projects-enabled'
        all_projects_dir     = 'projects-available'

        list_enabled_projects = os.listdir(os.path.join(self.envname, enabled_projects_dir))
        list_all_projects = os.listdir(os.path.join(self.envname, all_projects_dir))

        list_projects = []
        if (status == None):
            list_projects = list_all_projects
        if (status == 'enabled'):
            list_projects = list_enabled_projects
        if (status == 'disabled'):
            for p in list_all_projects:
                if p not in list_enabled_projects:
                    list_projects.append(p)

        # Restrict to requested client
        pattern = re.compile('(\w+)-(.*)')
        if (client_name):
            client_projects = []
            for project_name in list_projects:
                matches = pattern.findall(project_name)
                if (client_name == matches[0][0]):
                    client_projects.append(matches[0][1])
            list_projects = client_projects

        return list_projects

    def _do_project_disable(self, args):
        if len(args) == 2:
            (client_name, project_name) = args
            if (self._project_exists(client_name, project_name)):
                try:
                    os.unlink( os.path.join(self.envname, 'projects-enabled', '%s-%s' % (client_name, project_name)) )
                    print "Project '%s' has been disabled. Apache needs to be reloaded." % project_name
                except (IOError, os.error), exception:
                        print "** Project '%s' is already disabled." % project_name

            else:
                print "** Client '%s' has no project '%s'" % (client_name, project_name)
        else:
            print "** Invalid syntax"
            self.do_help('project')

    def _do_project_enable(self, args):
        if len(args) == 2:
            (client_name, project_name) = args
            if self._project_exists(client_name, project_name):
                try:
                    target = os.path.join( self.envname,
                                          'projects-available',
                                          '%s-%s' % (client_name, project_name) )
                    linkname = os.path.join( self.envname,
                                          'projects-enabled',
                                          '%s-%s' % (client_name, project_name) )
                    os.symlink( target, linkname )
                    print "Project '%s' has been enabled. Apache needs to be reloaded." % project_name
                except Exception, e:
                    print e

            else:
                print "** Client '%s' has no project '%s'" % (client_name, project_name)
        else:
            print "** Invalid syntax"
            self.do_help('project')

    def _do_project_remove(self, args):
        print "** TODO : This command has yet to be implemented."

        (client_name, project_name) = args

        # Confirm deletion
        continue_removal = False
        print "You are about to remove project '%s'." % project_name
        confirm_removal = raw_input('Remove project ? [y/N]> ').strip() or False
        if confirm_removal == 'y':
            continue_removal = True

        if not continue_removal:
            print "Project '%s' was *not* removed\n" % project_name
            return

        # Disable project
        if self._project_exists(client_name, project_name, 'enabled'):
            print "You cannot remove an enabled project. Disabling it."
            self._do_project_disable(args)

        # Delete apache config file
        try:
            linkname = os.path.join( self.envname, 'projects-available', '%s-%s'% (client_name, project_name) )
            os.unlink( linkname )
            print "Project '%s' has been removed" % project_name
            print "Apache configuration needs to be reloaded for this to be effective."
        except (IOError, os.error), exception:
            print "** An error occured. Project was NOT removed. Report the following message to the sysadmin."
            print exception

    def _do_project_add(self, args):
        if len(args) == 2:
            client_name = args[0]
            project_name = args[1]

            # Make sure client exists
            if not self._client_exists(client_name):
                print "Client '%s' does not exist !" % client_name
                return
            # Make sure project does not already exists
            if self._project_exists(client_name, project_name):
                print "Client '%s' already has a project named '%s'" % (client_name, project_name)
                return

            # Information collection
            collected_infos = {
                'client'     : client_name,
                'short_name' : project_name,
                'full_name'  : None
                }

            print
            print "Creating a new project for client '%s'" % client_name
            print "Let's collect some informations about the project :"
            print
            print "  Please enter project's full name."
            print "  This will be displayed in various places and emails."
            print

            dfn = project_name.capitalize()
            collected_infos['full_name'] = raw_input('Full Name [%s]> ' % dfn).strip() or dfn

            print
            print "  What configuration profile should be used ?"
            print "  Those reside in %s/profiles/" % self.envname
            print

            dp = self.getConfig('default_profile', 'general')
            collected_infos['profile'] = raw_input('Configuration profile [%s]> ' % dp).strip() or dp

            # Project creation
            print
            print "Supplied informations verified."
            print "Let's proceed with project creation :"
            print

            try:
                # -- Apache configuration file
                self._project_write_apache_conf( collected_infos )

                # -- Create required dirs
                self._project_create_dirs( collected_infos )

                # -- SVN repository creation
                self._project_create_svn_repos( collected_infos )

                # -- Trac environment initialisation
                self._project_trac_initenv( collected_infos )

                # -- Revoke all permissions in trac
                self._project_trac_revoke_all_perms( collected_infos )

                # -- Trac initial permissions
                self._project_trac_setperms( collected_infos )

                # -- Modifies Trac default conf
                self._project_trac_defaultconf( collected_infos )

                # -- Fix perms
                self._project_fix_perms( collected_infos )

            except Exception, e:
                print "An error occured :"
                print e
                traceback.print_exc()

            # -- Enable client ?
            print "Project has been created. Do you want to enable it ?"
            print
            enable_project = raw_input('Enable project ? [y/N]> ').strip() or False

            if enable_project.find('y') == 0:
                self._do_project_enable((client_name, project_name))

        else:
            self.do_help('project')

    def _project_create_dirs(self, infos):
        os.makedirs(os.path.join(self.getConfig('clients_root', 'general'),
                                 infos['client'],
                                 'htdocs',
                                 infos['short_name']), 0775)

        print "  Creating project's directory layout\n"

    def _project_write_apache_conf(self, infos):
        """
        TODO : clients may not be stored in 'clients_root', be careful with that.
        """
        conf_template = open(os.path.join(self.envname, 'profiles', infos['profile'], 'project.apache.conf'))
        conf_data = conf_template.read() % {'client_name'      : infos['client'],
                                            'project_name'     : infos['short_name'],
                                            'clients_root'     : self.getConfig('clients_root', 'general'),
                                            'authbackend_pass' : self.getConfig('authbackend_pass', 'general'),
                                            'trac_install_dir' : self.getConfig('lib_dir', 'trac'),
                                            'domain_name'      : self.getConfig('domain', 'general')}

        apache_conf_filepath = os.path.join( self.envname, 'projects-available', '%s-%s' % (infos['client'], infos['short_name']) )
        f = file(apache_conf_filepath, 'w+')
        f.write(conf_data)
        f.close()

        print "  Apache configuration written to %s\n" % apache_conf_filepath

    def _project_create_svn_repos(self, infos):
        repos_path = os.path.join( self.getConfig('clients_root', 'general'), infos['client'], 'var/svn', infos['short_name'] )
        create_cmd = 'svnadmin create %s' % repos_path
        (stdin, stdout, stderr) = os.popen3( create_cmd )

        err = stderr.read()
        if err:
            raise Exception( err )

        print "  Subversion repository created in %s\n" % repos_path

    def _project_trac_initenv(self, infos):

        trac_env_path = os.path.join( self.getConfig('clients_root', 'general'),
                                     infos['client'],
                                     'var/trac',
                                     infos['short_name'] )

        svn_path = os.path.join( self.getConfig('clients_root', 'general'),
                                infos['client'],
                                'var/svn',
                                infos['short_name'] )

        cmd_data = { 'env_path'         : trac_env_path,
                     'title'            : '"%s - %s - Trac"' % (infos['client'], infos['short_name']),
                     'db_dsn'           : 'sqlite:db/trac.db',
                     'svn_path'         : svn_path,
                     'templates_path'   : '%s/templates' % self.getConfig('assets_dir', 'trac'),
                     'trac_install_dir' : self.getConfig('lib_dir', 'trac')}

        trac_cmd = 'trac-admin %(env_path)s initenv %(title)s %(db_dsn)s svn %(svn_path)s %(templates_path)s' % cmd_data

        (stdin, stdout, stderr) = os.popen3( trac_cmd )

        err = stderr.read()
        if err:
            err = stdout.read()
            raise Exception( err )

        print "  Trac project initialized in %s\n" % trac_env_path

    def _project_trac_setperms(self, infos):
        trac_env_path = os.path.join( self.getConfig('clients_root', 'general'),
                                     infos['client'],
                                     'var/trac',
                                     infos['short_name'] )

        trac_perms_cmd = 'trac-admin %(env_path)s permission %(subcommand)s %(subject)s %(perms)s'

        # Grant default permissions
        perms_config = ConfigParser.SafeConfigParser()
        perms_config.read(os.path.join(self.envname, 'profiles', infos['profile'], 'permissions.ini'))
        for profile in perms_config.options('trac'):
            os.system( trac_perms_cmd % {'env_path'   : trac_env_path,
                                         'subcommand' : 'add',
                                         'subject'    : profile,
                                         'perms'      : perms_config.get('trac', profile)} )

        # Let user choose who gets admin rights
        print "  Please enter trac administrator username."
        print "  This user will be granted full privileges on project's Trac instance."
        print

        dan = infos['short_name'] + '-admin'
        admin_login = raw_input('Admin Login [%s]> ' % dan).strip() or dan

        os.system( trac_perms_cmd % {'env_path'   : trac_env_path,
                                     'subcommand' : 'add',
                                     'subject'    : admin_login,
                                     'perms'      : 'TRAC_ADMIN'} )
        print
        print "  Trac initial permissions set (admin rights given to '%s')\n" % admin_login

    def _project_trac_revoke_all_perms(self, infos):
        import trac.env

        trac_env_path = os.path.join( self.getConfig('clients_root', 'general'),
                                     infos['client'],
                                     'var/trac',
                                     infos['short_name'] )

        # Revoke all permissions
        trac_env = trac.env.open_environment(trac_env_path)
        trac_db = trac_env.get_db_cnx()
        db_cursor = trac_db.cursor()
        db_cursor.execute('DELETE FROM permission')
        trac_db.commit()

        print "  Revoked Trac default permissions\n"

    def _project_fix_perms(self, infos):
        """
        chown -R dev:www-data /$CLIENTSROOT/$CLIENTNAME/var/svn/$PROJECTNAME
        chmod g+w /$CLIENTSROOT/$CLIENTNAME/var/svn/$PROJECTNAME
        chown -R www-data:dev /$CLIENTSROOT/$CLIENTNAME/var/trac/$PROJECTNAME/db
	    chown dev:www-data /$CLIENTSROOT/$CLIENTNAME/var/trac/conf/trac.ini
	    chmod g+w /$CLIENTSROOT/$CLIENTNAME/var/trac/conf/trac.ini
        """

        # Trac DB
        trac_db_path   = os.path.join( self.getConfig('clients_root', 'general'),
                                      infos['client'],
                                      'var/trac',
                                      infos['short_name'],
                                      'db' )
        self._rchown( trac_db_path , int(self.getConfig('apache_user', 'general')), int(self.getConfig('ssh_group', 'general')) )

        # Trac attachments
        trac_attachments_path = os.path.join( self.getConfig('clients_root', 'general'),
                                             infos['client'],
                                             'var/trac',
                                             infos['short_name'],
                                             'attachments' )

        self._rchown( trac_attachments_path , int(self.getConfig('apache_user', 'general')), int(self.getConfig('ssh_group', 'general')) )

        # Trac conf
        trac_ini_path   = os.path.join( self.getConfig('clients_root', 'general'),
				       infos['client'],
				       'var','trac',
				       infos['short_name'],
				       'conf','trac.ini' )
        os.chmod( trac_ini_path, 0777 )

        # Subversion repository
        svn_repos_path = os.path.join( self.getConfig('clients_root', 'general'),
                                      infos['client'],
                                      'var/svn',
                                      infos['short_name'] )

        self._rchown( svn_repos_path, int(self.getConfig('apache_user', 'general')), int(self.getConfig('ssh_group', 'general')) )
        os.chmod( svn_repos_path, 0775 )

        # Htdocs directory
        htdocs_path = os.path.join( self.getConfig('clients_root', 'general'),
                                    infos['client'],
                                    'htdocs',
                                    infos['short_name'] )

        self._rchown( htdocs_path, int(self.getConfig('apache_user', 'general')), int(self.getConfig('ssh_group', 'general')) )
        os.chmod( htdocs_path, 0775 )

        print "  Perms fixed\n"

    def _project_trac_defaultconf(self, infos):
        """
        Overrides project's default trac.ini with values provided in configuration profile.
        """

        # New defaults
        tracdefaults_config = ConfigParser.SafeConfigParser()
        tracdefaults_config.read(os.path.join(self.envname, 'profiles', infos['profile'], 'trac-defaults.ini'))

        # Trac base config file
        project_config_path = os.path.join(self.getConfig('clients_root', 'general'), infos['client'], 'var', 'trac', infos['short_name'], 'conf', 'trac.ini')
        tracproject_config = ConfigParser.SafeConfigParser()
        tracproject_config.read(project_config_path)

        # Overriding
        for section in tracdefaults_config.sections():
            if not tracproject_config.has_section(section):
                tracproject_config.add_section(section)
            for option in tracdefaults_config.options(section):
                # Perform variable substituion in each default option
                # It is probably not very good in term of performances, but we'll wait until someone complains to fix it
                default_option = tracdefaults_config.get(section, option) % {'client_name'      : infos['client'],
                                                                             'project_name'     : infos['short_name'],
                                                                             'clients_root'     : self.getConfig('clients_root', 'general'),
                                                                             'authbackend_pass' : self.getConfig('authbackend_pass', 'general'),
                                                                             'trac_install_dir' : self.getConfig('lib_dir', 'trac'),
                                                                             'domain_name'      : self.getConfig('domain', 'general')}
                tracproject_config.set(section, option, default_option)

        fp = open(project_config_path, 'w+')
        tracproject_config.write(fp)

    def complete_project(self, text, line, begidx, endidx):
        comp = ['list', 'add', 'remove', 'enable', 'disable']
        parts = self._arg_tokenize(line)

        if len(parts) > 1 and parts[1] in comp:
            complete_func = getattr(self, '_complete_project_' + parts[1])
            if (float(sys.version[:3]) < 2.4):
                comp = complete_func.__call__(self, parts[2:])
            else:
                comp = complete_func.__call__(parts[2:])

        return self.word_complete(text, comp)

    def _complete_project_add(self, args):
        comp = []

        # "add" subcommand's first argument is client's name
        if not args or (len(args) <= 1 and args[0] not in self._get_clients()):
            comp = self._get_clients()

        return comp

    def _complete_project_enable(self, args):
        comp = []

        # "enable" subcommand's first argument is client's name
        if not args or (len(args) <= 1 and args[0] not in self._get_clients()):
            comp = self._get_clients()
        # "enable" subcommand second argument is project's name
        else :
            comp = self._get_projects(args[0], 'disabled')

        return comp

    def _complete_project_disable(self, args):
        comp = []

        # "disable" subcommand's first argument is client's name
        if not args or (len(args) <= 1 and args[0] not in self._get_clients()):
            comp = self._get_clients()
        # "disable" subcommand second argument is project's name
        else :
            comp = self._get_projects(args[0], 'enabled')

        return comp

    def _complete_project_remove(self, args):
        comp = []

        # "remove" subcommand's first argument is client's name
        if not args or (len(args) <= 1 and args[0] not in self._get_clients()):
            comp = self._get_clients()
        # "remove" subcommand second argument is project's name
        else :
            comp = self._get_projects(args[0])

        return comp

    ## Quit / EOF
    def do_quit(self, line):
        print
        sys.exit()

    do_exit = do_quit # Alias
    do_EOF = do_quit # Alias



    #
    # Helpers
    #

    def word_complete (self, text, words):
        """
        Word completion helper.
        """
        return [a for a in words if a.startswith (text)]

    def _rchown(self, directory, uid, gid):
        """
        Recursive chown.
        """
        try:
            if (os.path.isdir(directory)):
                os.chown(directory, uid, gid)
                direntries = os.listdir(directory)
                for direntry in direntries:
                    direntry = os.path.join(directory, direntry)
                    if (os.path.isdir(direntry)):
                        os.chown(direntry, uid, gid)
                        os.chdir(direntry)
                        self._rchown(direntry, uid, gid)
                    else:
                        os.chown(direntry, uid, gid)
            else:
                os.chown(directory, uid, gid)
        except (IOError, os.error), why:
            print "rchown %s: %s" % (str(directory), str(why))

    def _arg_tokenize (self, argstr):
        """
        Command line parameters tokenizer
        """
        argstr = util.to_utf8(argstr, sys.stdin.encoding)
        return shlex.split(argstr) or ['']

def run(args):
    """Main entry point."""
    admin = CleverboxAdmin()

    if len(args) > 0:
        if len(args) > 1:
            if args[1] in ('-h', '--help', 'help'):
                return admin.onecmd("help")
            elif args[1] in ('-v','--version','about'):
                return admin.onecmd("about")
            elif args[1] in ('-u', '--upgrade', 'upgrade'):
                admin.envname = args[0]
                return admin.onecmd("upgrade")
        else:
            admin.env_set(os.path.abspath(args[0]))
            if len(args) > 1:
                s_args = ' '.join(["'%s'" % command_parts for command_parts in args[2:]])
                command = args[1] + ' ' +s_args
                return admin.onecmd(command)
            else:
                while True:
                    admin.run()
    else:
        return admin.onecmd("help")

