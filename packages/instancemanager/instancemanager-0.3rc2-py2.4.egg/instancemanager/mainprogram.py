"""Manager of development zope instances
"""

import actions
import config
import configuration
import utils
import logging
import sys
import os
import os.path

log = logging.getLogger('main')

def parseArguments():
    """Parse the arguments, exit on error.
    """

    args = sys.argv[1:]
    if len(args) != 2:
        log.warn("Incorrect number of arguments.")
        usage()
        sys.exit(1)

    userDir = os.path.expanduser('~')
    configDir = os.path.join(userDir, config.CONFIGDIR)
    projectlist = [p.replace('.py', '') for p in os.listdir(configDir)
                if p.endswith('.py')
                and p not in ['__init__.py', 'userdefaults.py']]
    actionlist = actions.ACTIONS.keys()
    err = None
    # make sure we have a valid action
    if args[0] in actionlist:
        action = args[0]
    elif args[1] in actionlist:
        action = args[1]
    else:
        err = "No such action available"

    # make sure we have a valid project
    if args[0] in projectlist:
        project = args[0]
    elif args[1] in projectlist:
        project = args[1]
    else:
        err = "No such project available"
        
    if err is not None:
        log.warn(err)
        usage()
        sys.exit(1)

    log.debug("Arguments have been read: project=%s, action=%s.",
              project, action)
    return (project, action)


def usage():
    """Print the usage message.
    """

    print "Usage: instancemanager <project> <action>"
    print 'project: the name of the project, available projects are:'
    userDir = os.path.expanduser('~')
    configDir = os.path.join(userDir, config.CONFIGDIR)
    if os.path.exists(configDir):
        projects = [p.replace('.py', '') for p in os.listdir(configDir)
                    if p.endswith('.py')
                    and p not in ['__init__.py', 'userdefaults.py']]
        for project in projects:
            print '    %s' % project
    else:
        conf = configuration.Configuration()
        print "    You can look at userdefaults.py to change"
        print "    instancemanager to your local config."
        print "    Or run instancemanager again with <project> and <action>."
    print "action: the action to take, possible actions include:"

    actionlist = list(actions.ACTIONS.keys())
    actionlist.sort()
    for actionName in actionlist:
        action = actions.ACTIONS[actionName]
        print '    %s -- %s' % (actionName, action.name)

def main():
    utils.initLog()
    utils.addConsoleLogging()
    project, actionId = parseArguments()
    projectConfig = configuration.Configuration(project)
    actionFactory = actions.ACTIONS[actionId]
    action = actionFactory(configuration=projectConfig)
    action.run()

if __name__ == '__main__':
    main()
