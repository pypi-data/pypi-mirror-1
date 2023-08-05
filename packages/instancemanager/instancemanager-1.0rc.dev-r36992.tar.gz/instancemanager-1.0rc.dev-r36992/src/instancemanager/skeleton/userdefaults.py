"""Configuration defaults for zope locations and so.

 This file comes in two editions: the program-internal defaults and
 the '.instancemanager/userdefaults.py' file in your home
 directory. The user defaults are initially the same as the internal 
 defaults of instancemanager. You can adapt the settings in userdefaults.py
 to match local preferences that apply to all (or most) of your projects.

 The settings in userdefaults.py are commented out, which means they
 have no effect initially.  So when you want to change a default
 setting, you also need to remove the comment sign (#) from the front
 of that line.

 Certain things are more project-specific. These can be handled quite
 easily, too:

 * Copy this file to 'yourprojectname.py' in the '.instancemanager/'
 directory.

 * Make local modifications to the values like zope port number,
   username and the various sources.

 The project file overrides the user defaults, which in turn
 overrides defaults of instancemanager.

 Important: three extra variables are defined on-the-fly: 'user_dir',
 'project' and 'clientname'. These variables can be used in the
 variables named '*_template', as they get their variables expanded.

 'user_dir' -- User home directory (like '/home/reinout').

 'project' -- Name of the project (which you gave to instancemanager,
 like 'instancemanager yourprojectname create').

 'clientname' -- Name of the zeo client or zope server.  If you do not
 use zeo, this is the same as 'project'.  If you use zeo, in case of 3
 zeo clients, with project 'test', these names in turn are 'test',
 'test1' and 'test2'.  This is currently only available for the
 zopeconf_template.

"""

# Python and zope versions
#     python = 'python'
#     zope_version = '2.8.5'

# For use on development machines, set this to True.
# WARNING: in no case set this to True on a live site!
# When False (the default), the products marked as 'develop' will not
# be installed.  When True, all products will be installed.
#     development_machine = False

# Location of zope (not the instance, but the zope software itself)
#     zope_location_template = '/opt/zope/zope%(zope_version)s'

# Data for creating the instance
#     user = 'test'
#     password = 'test'
#     port = '8080'
#ftp_port = '8021'
#     ftp_port = None

# Z3 only option, select the name of the password manager to encrypt
#     z3_pw_manager = 'MD5' # or 'Plain Text' or 'SHA1'

# Data for the zeo server.
# If use_zeo is False, there will just be one zope server. If it is
# True, a zeo server and a zeo client (which is the zope server) will
# be created. The port number of the zeo server will be that of the
# zope server (=zeo client) plus the zeoport_offset (which can be
# negative).
#     use_zeo = False
#     zeoport_offset = 1
# Let the zeo clients use persistent caches.
#     use_zeo_client_caches = False
# Start a simple zeo monitor on this port.
#     monitor_port = None

# number_of_zeo_clients, not surprisingly, is the number of zeo clients
# to use for this zeo server.  This is work in progress: nothing is
# done yet with zeo clients.  So stick to the default of one for now.
#     number_of_zeo_clients = 1

# Template for where you want your zope instance or zeo server
# created. On Linux, for the user 'reinout' and the project
# 'sampleproject' the default will expand to
# '/home/reinout/instances/sampleproject'.
#     zope_instance_template = '%(user_dir)s/instances/%(project)s'
#     zeo_server_template = '%(user_dir)s/instances/zeo/%(project)s'

# You can provide pre-made Data.fs files for your product (for
# example, a recent copy of your customer's live Data.fs). The
# template below by default expands to something like
# '/home/reinout/instances/datafs/sampleproject.fs', adapt it to your
# local preferences.
#     datafs_template = '%(user_dir)s/instances/datafs/%(project)s.fs'

# You can provide a pre-made zope.conf/zeo.conf file for your project
# (for when instancemanager's handling isn't good enough). The
# template below by default expands to something like
# '/home/reinout/instances/zopeconf/sampleproject.conf', adapt it to
# your local preferences.
#     zeoconf_template = '%(user_dir)s/instances/zeoconf/%(project)s.conf'
# This is a spot where you could use 'clientname' instead of
# 'project'.  In fact, when using multiple zeo clients this is the
# only sane option, as with just 'project', or anything else that
# results in the same string for each client, you will copy the same
# zope.conf to all clients, so all will try to use the same port,
# which will fail.  Also, with just one zeo client or no zeo at all,
# 'clientname' is the same as 'project', so we make that the default
# now.
#     zopeconf_template = '%(user_dir)s/instances/zopeconf/%(clientname)s.conf'

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
# 
# An item in a source can also be a dictionary.  If you have this item
# in e.g. your symlink_sources:
#
#     {'source':'xmtrunk',
#      'productname':'eXtremeManagement',
#      'develop':True,
#      #'droplist':(), # relevant only for bundles
#      },
# 
# then this will result in a link in your Products dir:
# eXtremeManagement => /home/reinout/svn/xmtrunk
#
# The idea is that this can be useful when you are working on several
# branches of the same product and have these all checked out in your
# subversion dir.
#
# The 'develop':True option signals that this is a product that must
# only be installed on a development machine, not on the live site.
# Default is False, which means that the product will normally be
# installed.
# 
# This works in tandem with the general development_machine config
# option at the top of this file.  If you set that to False, then the
# products marked with 'develop' will not be installed.
#
# The droplist option is not relevant in this example, which is not
# related to a bundle. See the next paragraph.
#
# Sometimes a bundle is used that has one or two Products that are
# not needed. An example of this is Plone2.5, containing
# Five, which is redundant in later versions of Zope, and causes
# an exception when installed from the Plone bundle. 
#
#     {'source':'Plone-2.5',
#      #'productname':'', # not relevant for bundles
#      'develop':False,
#      'droplist':('Five'), # drop Five from this bundle
#      },
#
# The droplist contains names of directories in a symlinkbundle or 
# archive bundle source that will be neither linked nor installed 
# into Products
#
# Starting with Plone 3 we need to be able to populate the lib/python
# folder in addition to the Products folder.
#
#    symlinkbundle_sources = [
#    {'source':'3.0-lib',
#     'pylib':True, # This tells im to  
#     'url':'https://svn.plone.org/svn/plone/bundles/3.0-lib'}
#    ]
#
# This feature only works for symlink and symlinkbundle sources for now.


# Symlinks are just directories (or files) that are symlinked into
# Products/
#     symlink_sources = []
#     symlink_basedir_template = '%(user_dir)s/svn/'

# Symlink bundle sources are directories whose *contents* need to be
# symlinked. For example, a plone2.5 bundle. Just specify 'plone2.5'
# here (if that's your local bundle name) and everything gets
# symlinked.
#     symlinkbundle_sources = []
#     symlinkbundle_basedir_template = '%(user_dir)s/svn/'

# Normally symlinks are OK, but in server setups you might want to use
# svn export instead to isolate a preview and a production instance.
#     use_svn_export = False

# Archive files (.tgz, .tar, .zip) that need to be extracted directly 
# into Products/
#     archive_sources = []
#     archive_basedir_template = '%(user_dir)s/download/'

# Archive bundle files. They get extracted in a temporary location. If
# just one directory gets extracted, the contents of that directory
# get copied to Products/ (for instance for plone or formmailer
# bundles). If there are multiple directories (as is the case with
# some other bundles), all are copied to Products/.
#     archivebundle_sources = []
#     archivebundle_basedir_template = '%(user_dir)s/download/'

# Name of the plone root inside your zope root. Needed for the
# reinstall script. If it is not specified, we won't try to
# reinstall.
#     plone_site_name = ''

# The main products. It is used by the quickinstaller. The only effect
# is that these products are *always* reinstalled, no matter
# what. Handy during development when you want to run your products's
# installer without having to increase the version number again and
# again. If these products aren't already installed, they will be.
#     main_products = []

# This is the template dir where backups of the instance database are
# stored.
#     backup_basedir_template= '%(user_dir)s/backups/%(project)s'

# The number of full backups to keep, older backups will be deleted.
# If you set this to 0 no backups will be deleted.
#     number_of_backups = 2

# This is the template dir where snapshot backups of the instance
# database are stored. Handy for intermediate "I'm going to do
# something dangerous right now" backups.
#     snapshot_basedir_template= '%(user_dir)s/snapshotbackups/%(project)s'

# This is an optional location of another instance's database, useful
# for copying over the database from your production instance to a
# preview instance. Invoke 'instancemanager --repozo sync projectname'
# to use it.
#     sync_database = ''

# This is the number of days you should keep old transactions when
# packing the database.
#     pack_days= '1'

# Extension profiles for adapting the plone config with GenericSetup.
# See self.ploneSite.portal_setup.listContextInfos() for possible ids.
# Two examples are: 'profile-CMFPlone:plone' and
# u'profile-Products.CMFQuickInstallerTool:CMFQuickInstallerTool'.

#     generic_setup_profiles= []

# Run command allows to run custom script. 
# If you need exact order of actions, add --runcommand to multi_actions
# definition, otherwise must be invoked manually by --runcommand option.
# run_command is called for all instances.
# To the run_command is appended one parameter - just created
# instance directory name.

#     run_command = ''

# XXX Note for instancemanager developers: "multi_actions" are not
# copied correctly at the moment by the
# copy_defaults_to_userdefaults.py script.
# So remove those by hand afterwards.
#     multi_actions = {}

