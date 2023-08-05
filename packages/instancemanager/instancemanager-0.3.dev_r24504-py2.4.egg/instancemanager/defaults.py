"""Configuration defaults for zope locations and so.

 This file comes in two editions: the program-internal defaults and
 the '.instancemanager/userdefaults.py' file in your home
 directory. The user defaults are initially the same as the own
 defaults of instancemanager. You can adapt these to your local
 preferences.

 Certain things are more project-specific. That can be handled quite
 easily, too:

 * Copy this file to 'yourprojectname.py' in the '.instancemanager/'
 directory.

 * Make local modifications to the values like zope port number,
   username and the various sources.

 The project file overwrites the user defaults, which in turn
 overwrites defaults of instancemanager.

 Important: two extra variables are defined on-the-fly: 'user_dir' and
 'project'. These variables can be used in the variables named
 '*_template', as they get their variables expanded.

 'user_dir' -- User home directory (like '/home/reinout').

 'project' -- Name of the project (which you gave to instancemanager,
 like 'instancemanager yourprojectname create').

"""

# Python and zope versions
python = 'python'
zope_version = '2.8.5'

# Location of zope (not the instance, but the zope software itself)
zope_location_template = '/opt/zope/zope%(zope_version)s'

# Data for creating the instance
user = 'test'
password = 'test'
port = '8080'

# Template for where you want your zope instance created. On Linux,
# for the user 'reinout' and the project 'sampleproject' the default
# will expand to '/home/reinout/instances/sampleproject'.
zope_instance_template = '%(user_dir)s/instances/%(project)s'

# You can provide pre-made Data.fs files for your product (for
# instance a recent copy of your customer's live Data.fs). The
# template below by default expands to something like
# '/home/reinout/instances/datafs/sampleproject.fs', adapt it to your
# local preferences.
datafs_template = '%(user_dir)s/instances/datafs/%(project)s.fs'

# You can provide a pre-made zope.conf file for your project (for when
# instancemanager's handling isn't good enough). The template below by
# default expands to something like
# '/home/reinout/instances/zopeconf/sampleproject.conf', adapt it to your
# local preferences.
zopeconf_template = '%(user_dir)s/instances/zopeconf/%(project)s.conf'

# Sources. They are all pairs of (a) an actual source list and (b) a
# basedir template. The items of the source list are simply appended
# to the base directory. Sources are symlinked or extracted to the
# Products/ directory of the instance.
# 
# A symlink_sources of ['item1', 'item2'] combined with the default
# basedir template would result in two symlinks inside your Products/
# directory: 
# item1 => /home/reinout/svn/item1
# item2 => /home/reinout/svn/item2

# Symlinks are just directories (or files) that are symlinked into
# Products/
symlink_sources = []
symlink_basedir_template = '%(user_dir)s/svn/'

# Symlink bundle sources are directories which *contents* need to be
# symlinked. For instance a plone2.5 bundle. Just specify 'plone2.5'
# here (if that's your local bundle name) and everything gets
# symlinked.
symlinkbundle_sources = []
symlinkbundle_basedir_template = '%(user_dir)s/svn/'

# .tgz files that need to be extracted directly into Products/
tgz_sources = []
tgz_basedir_template = '%(user_dir)s/download/'

# .tgz bundle files. They get extracted in a temporary location. If
# just one directory gets extracted, the contents of that directory
# get copied to Products/ (for instance for plone or formmailer
# bundles). If there are multiple directories (as is the case with
# some other bundles), all are copied to Products/.
tgzbundle_sources = []
tgzbundle_basedir_template = '%(user_dir)s/download/'

# Name of the plone root inside your zope root. Needed for the
# reinstall script. If it is not specified, we won't try to
# reinstall.
plone_site_name = ''

# The main products. It is used by the quickinstaller, the only effect
# is that these products are *always* reinstalled, no matter
# what. Handy during development when you want to run your products's
# installer without having to increase the version number again and
# again. If these products aren't installed, they are installed.
main_products = []

# This is the template dir where backups of the instance database are
# stored.
backup_basedir_template= '%(user_dir)s/backups/'
