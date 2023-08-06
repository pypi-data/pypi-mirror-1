import os
import subprocess
import shutil
import logging

from zc.buildout import UserError
import zc.recipe.egg
import djangorecipe.recipe
import setuptools

djangorecipe.recipe.settings_template = '''
import os

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'    # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = '%(project)s.db'
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

TIME_ZONE = 'America/Chicago'

LANGUAGE_CODE = 'en-us'

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '%(media-directory)s'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '%(media-root)s'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '%(admin-media-url)s'

# Don't share this with anybody.
SECRET_KEY = '%(secret)s'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
)

ROOT_URLCONF = '%(project)s.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), "templates"),
)

'''

djangorecipe.recipe.production_settings = '''
from %(project)s.settings import *
from %(project)s.local_settings import *
'''

djangorecipe.recipe.development_settings = '''
from %(project)s.settings import *
from %(project)s.local_settings import *
DEBUG=True
TEMPLATE_DEBUG=DEBUG
'''

CONTROL_SCRIPT_FORMAT = "%(project)s-%(settings)s"

LIGHTTPD_INIT = '''#!/bin/bash

# Set this to your lighttpd configuration file and PID

CONFIG=%(lighttpd-directory)s/lighttpd.conf
PIDFILE=%(lighttpd-directory)s/lighttpd.pid

# Do not change anything below unless you know what you do

DAEMON=%(lighttpd-bin)s
NAME="lighttpd"
PATH=/sbin:/bin:/usr/sbin:/usr/bin
OPTS="-f $CONFIG"

fail () {
	echo "failed!"
	exit 1
}

success () {
	echo "$NAME."
}

case "$1" in
	start)
			echo -n "Starting $NAME: "
			if start-stop-daemon --start --quiet --pidfile $PIDFILE --exec $DAEMON -- $OPTS ; then
				success
			else
				fail
			fi
		;;
	stop)
			echo -n "Stopping $NAME: "
			if start-stop-daemon --stop --quiet --oknodo --retry 30 --pidfile $PIDFILE --exec $DAEMON ; then
				success
			else
				fail
			fi
		;;
	reload)
			echo -n "Reloading $NAME configuration: "
			if ! eval "$DAEMON -t $OPTS" > /dev/null 2>&1; then
				eval "$DAEMON -t $OPTS"
				fail
			fi
			if start-stop-daemon --stop --signal 2 --oknodo --retry 30 --quiet --pidfile $PIDFILE --exec $DAEMON; then
				if start-stop-daemon --start --quiet --pidfile $PIDFILE --exec $DAEMON -- $OPTS ; then
					success
				else
					fail
				fi
			else
				fail
			fi
		;;
	restart)
			$0 stop
			[ -r  $PIDFILE ] && while pidof lighttpd |\
				grep -q `cat $PIDFILE 2>/dev/null` 2>/dev/null ; do sleep 1; done
			$0 start
		;;
	*)
		echo "Usage: $0 {start|stop|restart|reload}"
		exit 1
esac
'''

PROJECT_INIT = '''#!/bin/bash

NAME="%(project)s"
PROJECT_DIR="%(project-directory)s"
CONTROL_SCRIPT="%(control-script-location)s"
# Do not change anything below unless you know what you do

PIDFILE="$PROJECT_DIR/$NAME.pid"
SOCKET="$PROJECT_DIR/$NAME.sock"
DAEMON=%(executable)s
PATH=/sbin:/bin:/usr/sbin:/usr/bin
OPTS="$CONTROL_SCRIPT runfcgi socket=$SOCKET pidfile=$PIDFILE method=prefork minspare=1 maxspare=1 maxchildren=10 maxrequests=100"

fail () {
	echo "failed!"
	exit 1
}

success () {
	echo "$NAME."
}

case "$1" in
	start)
			echo -n "Starting $NAME: "
			if start-stop-daemon -d $PROJECT_DIR --start --quiet --pidfile $PIDFILE --exec $DAEMON -- $OPTS ; then
				success
			else
				fail
			fi
		;;
	stop)
			echo -n "Stopping $NAME: "
			if start-stop-daemon -d $PROJECT_DIR --stop --quiet --oknodo --retry 30 --pidfile $PIDFILE --exec $DAEMON ; then
				success
			else
				fail
			fi
		;;
	restart)
			$0 stop
			$0 start
		;;
	*)
		echo "Usage: $0 {start|stop|restart}"
		exit 1
esac
'''

LIGHTTPD_CONF = """var.basedir = "%(lighttpd-directory)s"

############ Options you really have to take care of ####################

## modules to load
# mod_access, mod_accesslog and mod_alias are loaded by default
# all other module should only be loaded if neccesary
# - saves some time
# - saves memory

server.modules			= ( 
			"mod_access",
			"mod_alias",
			"mod_accesslog",
			"mod_extforward",
			"mod_rewrite", 
			"mod_fastcgi", 
			"mod_redirect", 
#			"mod_proxy", 
#			"mod_evhost",
#			"mod_compress",
#			"mod_usertrack",
#			"mod_rrdtool",
#			"mod_webdav",
#			"mod_expire",
#			"mod_flv_streaming",
#			"mod_evasive"
 )

## a static document-root, for virtual-hosting take look at the 
## server.virtual-* options
server.document-root		= "%(public-html-directory)s"

## where to send error-messages to
server.errorlog				= basedir+"/error.log"

## files to check for if .../ is requested
index-file.names			= ( "index.php", "index.html", 
								"index.htm", "default.htm" )

## Use the "Content-Type" extended attribute to obtain mime type if possible
# mimetype.use-xattr = "enable"

#### accesslog module
accesslog.filename			= basedir+"/access.log"

## deny access the file-extensions
#
# ~    is for backupfiles from vi, emacs, joe, ...
# .inc is often used for code includes which should in general not be part
#      of the document-root
url.access-deny				= ( "~", ".inc" )

######### Options that are good to be but not neccesary to be changed #######

## bind to port (default: 80)
include "port.conf"

## bind to localhost only (default: all interfaces)
server.bind					= "127.0.0.1"

## error-handler for status 404
#server.error-handler-404  = "/error-handler.html"
#server.error-handler-404  = "/error-handler.php"

## to help the rc.scripts
server.pid-file				= basedir+"/lighttpd.pid"

## 
## Format: <errorfile-prefix><status>.html
## -> ..../status-404.html for 'File not found'
#server.errorfile-prefix	= "/var/www/"

## virtual directory listings
dir-listing.encoding		= "utf-8"
#server.dir-listing			= "enable"

server.tag = "lighttpd"

#### external configuration files
## mimetype mapping
include_shell "/usr/share/lighttpd/create-mime.assign.pl"

extforward.forwarder = (
	"127.0.0.1" => "trust",
)

"""

PROJECT_CONF = """# Configuration for automatically created Django sites will be listed here
# by the 1-click Django installer.

# %(project)s
$HTTP["host"] =~ "%(host)s" {
	fastcgi.server = (
		"/%(project)s.fcgi" => (
			"main" => (
				"socket" => "%(project-directory)s/megroup.sock",
				"check-local" => "disable",
			)
		),
	)
	alias.url = (
		"%(admin-media-url)s" => "%(admin-media-directory)s",
		"%(media-url)s" => "%(media-directory)s",
	)

	url.rewrite-once = (
		"^(/media.*)$" => "$1",
		"^/favicon\.ico$" => "/media/favicon.ico",
		"^(/.*)$" => "/%(project)s.fcgi$1",
	)
}

"""

PORT_CONF = """# This file will be read by the 1-click Django installer in order to get the
# port number of the lighttpd.

"""

DJANGO_REPOSITORY = 'http://code.djangoproject.com/svn/django/'

class Djangorecipe(djangorecipe.recipe.Recipe):
	"""
	Extends Django Recipe for djangohosting.ch specificity.
	
	It will try to get of djangohosting's working copy of django instead of
	checking it out of djangoproject's server.
	
	It also create control-scripts to start django with the development or production
	script.
	"""

	def create_manage_script(self, extra_paths, ws):
		extra_paths = [x for x in extra_paths if not x in ws.entries]
		project = self.options.get('projectegg', self.options['project'])
		tmp_vars = self.options.copy()
		for settings in ('development', 'production',):
			tmp_vars['settings'] = settings
			zc.buildout.easy_install.scripts(
				[(CONTROL_SCRIPT_FORMAT % tmp_vars, 'djangorecipe.manage', 'main')],
				ws, self.options['executable'], self.options['bin-directory'],
				extra_paths = extra_paths,
				arguments= "'%s.%s'" % (project, settings))

	def install_svn_version(self, version, download_dir, location,
		install_from_cache):
		svn_url = self.version_to_svn(version)
		download_location = os.path.join(
			download_dir, 'django-' +
			self.version_to_download_suffix(version))
		if not install_from_cache:
			if os.path.exists(download_location):
				if self.svn_update(download_location, version):
					raise UserError(
						"Failed to update Django; %s. "
						"Please check your internet connection." % (
							download_location))
			else:
				download_location = self.get_svn_wc(svn_url, download_location)
		else:
			self.log.info("Installing Django from cache: " + download_location)
		shutil.copytree(download_location, location)

	def get_svn_wc(self, url, location):
		wc_loc = self.options.get('django-wc-path')
		if os.path.exists(wc_loc) and url.startswith(DJANGO_REPOSITORY):
			shared_wc = os.path.join(wc_loc, url[len(DJANGO_REPOSITORY):])
			if os.path.exists(shared_wc):
				self.log.info('Getting the django working copy from "%s".' % shared_wc )
				return shared_wc

		self.log.info("Checking out Django from svn: %s" % url)
		if self.command('svn co %s %s' % (url, location)):
			raise UserError("Failed to checkout Django. "
							"Please check your internet connection.")
		return location

class Recipe(object):
	def __init__(self, buildout, name, options):
		# Check required settings
		for x in ('host', 'port',):
			if not options.get(x):
				raise UserError('Your forgot to set "%s" for the %s part' % x)

		# Set properties
		self.log = logging.getLogger(name)
		self.buildout, self.name, self.options = buildout, name, options
		self.recipes = []
		self.created = []

		# Set default		
		options.setdefault('django-wc-path', '/usr/share/django')
		options.setdefault('settings', 'development')
		options.setdefault('project', name)
		options.setdefault('lighttpd-bin', '/usr/local/sbin/lighttpd')
		options.setdefault('media-url', '/media/')
		options.setdefault('media-directory',
							os.path.join(
								buildout['buildout']['directory'],
								options['project'],
								'media/'))
		options.setdefault('admin-media-url', '/admin_media/')
		options.setdefault('admin-media-directory',
							os.path.join(
								buildout['buildout']['parts-directory'],
								'django/django/contrib/admin/media/'))
		options.setdefault('development-port', '8000')
		options.setdefault('development-host', 'localhost')

		# Convert relative to absolute path and set default
		cur_dir = os.getcwd()
		os.chdir(self.buildout['buildout']['directory'])
		for dir in ('public-html', 'private', 'lighttpd', 'init'):
			option_name = dir+'-directory'
			option_value = options.get(option_name, dir.replace('-', '_'))
			options[option_name] = os.path.abspath(option_value)
		os.chdir(cur_dir)

		#Check for lighttpd
		if not os.path.exists(options.get('bin-lighttpd')):
			self.log.warn('Could not find lighttpd at "%s".'
						  'You won\'t be able to test your test your lighttpd configuration.'
						  'You can set the path to lighttpd with the "bin-lighttpd" option.'
						  % options.get('bin-lighttpd'))

		# Add django recipe
		self.djangorecipe = Djangorecipe(buildout, name, options)
		self.recipes.append(self.djangorecipe)

	def install(self):
		try:
			options = self.options
			location = options['location']
			base_dir = self.buildout['buildout']['directory']
			project_dir = os.path.join(base_dir, options['project'])
			download_dir = self.buildout['buildout']['download-cache']

			self.set_folders(directories = {
				options['init-directory']: 0750,
				options['lighttpd-directory']: 0750,
				options['private-directory']: 0700,
				options['public-html-directory']: 0755
				})
			self.check_out_project(project_dir, options.get('project-svn'))
			self.set_init_script(options['init-directory'])
			self.set_conf_file(options['lighttpd-directory'],
							   options['project'])
			self.set_development_server_launcher(
				project_dir,
				options.get('bin-directory'),
				options.get('project') + '-development')

			self.install_recipes()

			if not self.options.get('projectegg'):
				local_settings_loc = os.path.join(project_dir, 'local_settings.py')
				self.set_local_settings(
					local_settings_loc,
					options.get('local-settings-template'))

		except IOError, (errno, strerror):
			for path in self.created:
				if os.path.exists(path):
					if os.path.isdir(path):
						shutil.rmtree(path)
					else:
						os.unlink(path)
			raise UserError( "I/O error(%s): %s" % (errno, strerror) )
		return self.created

	def install_recipes(self):
		for recipe in self.recipes:
			result = recipe.install()
			result_type = type(result).__name__
			if result_type in ('tuple', 'list'):
				self.created.extend(result)
			elif result_type in ('str'):
				self.created.append(result)
				
	def update_recipes(self):
		for recipe in self.recipes:
			result = recipe.update()
			result_type = type(result).__name__
			if result_type in ('tuple', 'list'):
				self.created.extend(result)
			elif result_type in ('str'):
				self.created.append(result)

	def set_folders(self, directories={}):
		for d_path in directories.keys():
			if not os.path.exists(d_path):
				self.log.info('Creating folder "%s".' % d_path)
				os.mkdir(d_path)
				self.created.append(d_path)
			self.log.info('Set %s mode to %o' % (d_path, directories[d_path],))
			try:
				os.chmod(d_path, directories[d_path])
			except OSError:
				pass

	def check_out_project(self, project_dir, project_svn=None):
		if not os.path.exists(project_dir) and project_svn:
			cmd='svn co %s %s' % (project_svn, project_dir)
			self.log.info('Creating project from svn (%s)' % project_svn)
			if self.command(cmd):
				if os.path.exists(project_dir):
					self.created.append(project_dir)
				raise UserError('Failed to create project from svn "%s"' % project_svn)
			self.created.append(project_dir)

	def set_init_script(self, init_dir):
		init_list = {
			'lighttpd': LIGHTTPD_INIT,
			self.options.get('project'): PROJECT_INIT
		}
		tmp_vars = self.get_template_vars()
		for init_name in init_list.keys():
			init_file = os.path.join(init_dir, init_name)
			self.log.info('Creating init file "%s".' % init_file)
			self.create_file(init_file, init_list[init_name], tmp_vars)
			os.chmod(init_file, 0740)

	def set_conf_file(self,conf_dir, project_name):
		conf_list = {'lighttpd': (LIGHTTPD_CONF, 'include "%(project)s.conf"',),
					 project_name: (PROJECT_CONF, ''),
					 'port': (PORT_CONF, 'server.port = %(port)s',)}
		temp_vars = self.get_template_vars()
		for conf in conf_list.keys():
			conf_path = os.path.join(conf_dir, conf + '.conf')
			if not os.path.exists(conf_path):
				self.log.info('creating "%s"...' % conf_path)
				self.create_file(conf_path,
								 '\n'.join((conf_list[conf])),
								 temp_vars)
			elif conf_list[conf][1]:
				f = open(conf_path, 'r')
				code_to_append = conf_list[conf][1] % temp_vars
				if not f.read().count(code_to_append):
					f.close()
					self.log.info('Append "%s" with "%s"...' % (conf_path,code_to_append,))
					f = open(conf_path, 'a')
					f.writelines('\n'+code_to_append)
				f.close()

	def set_local_settings(self, local_settings_file, template_file):
		if template_file and os.path.exists(template_file):
			f = open(template_file, 'r')
			template = f.read()
			f.close()
			self.log.info('Creating "%s".' % local_settings_file)
			self.create_file(local_settings_file, template, self.get_template_vars())

	def set_development_server_launcher(self, project_dir, bin_dir, manage_script):
		launcher = os.path.join(project_dir, 'RUN')
		tmp_vars = self.get_template_vars()
		tmp_vars['development-control-script-location'] = os.path.join(
			bin_dir, manage_script)
		self.log.info('Creating "%s", used to the development server.' % launcher)
		self.create_file(
			launcher,
			'%(development-control-script-location)s runserver %(development-host)s:%(development-port)s',
			tmp_vars)
		try:
			os.chmod(launcher, 0740)
		except:
			self.log.warning('Could not changed the permision of "%s" and make it executable' % launcher)

	def get_template_vars(self, template_vars={}):
		template_vars['secret'] = self.generate_secret()
		template_vars['control-script-location'] = os.path.join(
			 self.options['bin-directory'],
			'%s-%s' % (self.options.get('project', self.name), self.options['settings'],)
		)
		template_vars['directory'] = self.buildout['buildout']['directory']
		template_vars['project-directory'] = os.path.join(
			self.buildout['buildout']['directory'],
			self.options['project'])
		template_vars.update(self.options)
		return template_vars

	def update(self):
		self.update_recipes()
		return self.created

	def command(self, cmd, **kwargs):
		return self.djangorecipe.command(cmd, **kwargs)

	def create_file(self, file, template, options):
		if os.path.exists(file):
			self.log.info('Skipped... "%s" already exist.' % file)
			return

		f = open(file, 'w')
		self.created.append(file)
		f.write(template % options)
		f.close()

	def generate_secret(self):
		return self.djangorecipe.generate_secret()
