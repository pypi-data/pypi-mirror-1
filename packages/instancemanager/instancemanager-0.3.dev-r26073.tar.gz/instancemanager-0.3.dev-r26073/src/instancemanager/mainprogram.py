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

STANDARD_LOGLEVEL = logging.INFO

def getProjects():
    userDir = os.path.expanduser('~')
    configDir = os.path.join(userDir, config.CONFIGDIR)
    results = [p.replace('.py', '') for p in os.listdir(configDir)
               if p.endswith('.py')
               and p not in ['__init__.py', 'userdefaults.py']]
    return results

def parseArguments():
    """Parse the arguments, exit on error.
    """

    args = sys.argv[1:]
    if len(args) < 2 or len(args) > 3:
        log.warn("Incorrect number of arguments.")
        usage()
        sys.exit(1)

    projects = getProjects()
    projects.append('ALL')
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
    if args[0] in projects:
        project = args[0]
    elif args[1] in projects:
        project = args[1]
    else:
        err = "No such project available"

    # Set the log level
    if len(args) == 3:
        loglevel = args[2].upper()
        if loglevel not in logging._levelNames.keys():
            usage()
            sys.exit(1)
        else:
            loglevel = logging.getLevelName(loglevel)
    else:
        loglevel = STANDARD_LOGLEVEL

    if err is not None:
        log.warn(err)
        usage()
        sys.exit(1)

    log.debug("Arguments have been read: project=%s, action=%s.",
              project, action)
    return (project, action, loglevel)


def usage():
    """Print the usage message.
    """

    print "Usage: instancemanager <project> <action> [<loglevel>]"
    print ''
    print 'project: the name of the project, available projects are:'
    userDir = os.path.expanduser('~')
    configDir = os.path.join(userDir, config.CONFIGDIR)
    if os.path.exists(configDir):
        projects = [p.replace('.py', '') for p in os.listdir(configDir)
                    if p.endswith('.py')
                    and p not in ['__init__.py', 'userdefaults.py']]
        for project in projects:
            print '    %s' % project
        print "    You can use ALL to perform the action " +\
            "for all projects."
    else:
        conf = configuration.Configuration()
        print "    You can look at userdefaults.py to change"
        print "    instancemanager to your local config."
        print "    Or run instancemanager again with <project> and <action>."
    print ''
    print "action: the action to take, possible actions include:"

    actionlist = list(actions.ACTIONS.keys())
    actionlist.sort()
    for actionName in actionlist:
        action = actions.ACTIONS[actionName]
        print '    %-15s -- %s' % (actionName, action.name)

    print ''
    print "loglevel (optional): log level to use. Valid levels are:"
    # Get list of levels that are strings:
    levels = [(levelHeight,levelName) for levelName,levelHeight
              in logging._levelNames.items() if isinstance(levelName, str)]
    # Sort according to levelHeight:
    levels.sort()
    for levelHeight, levelName in levels:
        extra = ''
        levelName = levelName.lower()
        if levelHeight == STANDARD_LOGLEVEL:
            extra = ' (default value)'
        print '    %-15s -- log level %2s%s' % (levelName, levelHeight, extra)

def performActionOnProject(project, actionId):
    actionFactory = actions.ACTIONS[actionId]
    projectConfig = configuration.Configuration(project)
    action = actionFactory(configuration=projectConfig)
    action.run()

def main():
    utils.initLog()
    project, actionId, loglevel = parseArguments()
    utils.addConsoleLogging(loglevel)
    if project == 'ALL':
        log.info("Performing '%s' for all projects.",
                 actionId)
        projects = getProjects()
        for project in projects:
            log.info("Project: %s", project)
            performActionOnProject(project, actionId)
    else:
        performActionOnProject(project, actionId)

if __name__ == '__main__':
    main()
