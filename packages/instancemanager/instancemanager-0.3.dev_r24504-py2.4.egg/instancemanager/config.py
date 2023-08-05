"""Configuration for instance manager
"""

# Directory in the user's homedir where we store our config.
CONFIGDIR = '.instancemanager'

CONFIGCHANGES = {
    'address 8080': 'address %(port)s\n',
    'security-policy-implementation python':
    'security-policy-implementation python\n',
    'verbose-security on': 'verbose-security on\n',
    'debug-mode on': 'debug-mode on\n'
    }

LOGFILE = 'instancemanager.log'

QISCRIPT = 'quickreinstaller.py'

