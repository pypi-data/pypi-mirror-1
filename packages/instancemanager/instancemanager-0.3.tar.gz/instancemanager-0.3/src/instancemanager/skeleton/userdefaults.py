"""Defaults for zope locations and so.

This file comes in two editions: the program-internal defaults and the
'.instancemanager/userdefaults.py' file in your homedirectory. The
user defaults are initially the same as instancemanager's own
defaults. You can adapt these to your local preferences.

Certain things are more project-specific. That can be handled quite
easily, too:

* Copy this file to 'yourprojectname.py' in the '.instancemanager/'
directory.

* Make local modifications to the values like zope port number,
  username and the various sources.

The project file overwrites the user defaults, which in turn
overwrites instancemanager's defaults.

Important: two extra variables are defined on-the-fly: 'user_dir' and
'project'. These variables can be used in the variables named
'*_template', as they get their variables expanded.

'user_dir' -- User home directory (like '/home/reinout').

'project' -- Name of the project (which you gave to instancemanager,
like 'instancemanager yourprojectname create').

"""

# Python and zope versions
#     python = 'python'
#     zope_version = '2.8.5'

# Location of zope (not the instance, but the zope software itself)
#     zope_location_template = '/opt/zope/zope%(zope_version)s'

# Data for creating the instance
#     user = 'test'
#     password = 'test'
#     port = '8080'

# Template for where you want your zope instance created. On linux,
# for the user 'reinout' and the project 'sampleproject' the default
# will expand to '/home/reinout/instances/sampleproject'.
#     zope_instance_template = '%(user_dir)s/instances/%(project)s'

# You can provide pre-made Data.fs files for your product (for
# example a recent copy of your customer's live Data.fs). The
# template below by default expands to something like
# '/home/reinout/instances/datafs/sampleproject.fs', adapt it to your
# local preferences.
#     datafs_template = '%(user_dir)s/instances/datafs/%(project)s.fs'

# Sources. They are all pairs of (a) an actual source list and (b) a
# basedir template. The items of the source list are simply appended
# to the base directory. Sources are symlinked or extracted to the
# instance's Products/ directory.
# 
# A symlink_sources of ['item1', 'item2'] combined with the default
# basedir template would result in two symlinks inside your Products/
# directory: 
# item1 => /home/reinout/svn/item1
# item2 => /home/reinout/svn/item2

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

# Automatic product re-installation can be handled if you place a
# special script in the zope root that calls your plone's
# quickinstaller. The content of that script is your responsibility,
# but instancemanager will call it if you want. Leave
# 'reinstall_script' empty if you dont' want this to happen (which is
# the default value).
#     reinstall_script = ''
#     reinstall_template = 'wget --http-user=%(user)s --http-passwd=%(password)s http://localhost:%(port)s/%(reinstall_script)s'

# Before product_reinstalling, zope is restarted. Instancemanager must
# wait a little while before zope reacts correctly to the 'wget'
# call. By default this is 5 seconds. Change it to 0.01 if you're
# running on a quadruple quantum computer.
#     zope_wait_time = 5
