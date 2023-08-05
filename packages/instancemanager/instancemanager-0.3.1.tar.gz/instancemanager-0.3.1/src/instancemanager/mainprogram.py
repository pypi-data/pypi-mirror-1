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
from optparse import OptionParser

log = logging.getLogger('main')


def usage():
    """Return the usage message.
    """

    res = []
    res.append("Usage: instancemanager [options] [multi-action] <project>")
    res.append("multi-action: default ones are 'fresh' and 'soft'.")
    res.append('project: the name of the project, available projects are:')
    userDir = os.path.expanduser('~')
    configDir = os.path.join(userDir, config.CONFIGDIR)
    if os.path.exists(configDir):
        projects = [p.replace('.py', '') for p in os.listdir(configDir)
                    if p.endswith('.py')
                    and p not in ['__init__.py', 'userdefaults.py']]
        for project in projects:
            res.append('    %s' % project)
        res.append("    You can use ALL to perform the action " +\
            "for all projects.")
    else:
        conf = configuration.Configuration()
        res.append("    You can look at userdefaults.py to change")
        res.append("    instancemanager to your local config.")
        res.append("    Or run instancemanager again with <project> and <action>.")
    return '\n'.join(res)


parser = OptionParser(usage())
parser.add_option(
    '--verbose',
    '-v',
    help='Show all logging messages.',
    action='store_true',
    default=False)
parser.add_option(
    '--quiet',
    '-q',
    help='Only show error messages.',
    action='store_true',
    default=False)
actions.addOptions(parser)

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

    (options, args) = parser.parse_args()
    # The arguments are either just a project or a project and a
    # multi-action.
    projects = getProjects()
    projects.append('ALL')
    # Search for project/multi-action
    project = None
    multiAction = None
    if len(args) == 0:
        pass
    if len(args) > 0:
        firstArgument = args[0]
        if firstArgument in projects:
            project = firstArgument
    if len(args) > 1:
        secondArgument = args[1]
        if project:
            multiAction = secondArgument
        else:
            # Second chance to find a project
            if secondArgument in projects:
                project = secondArgument
                # Then, the first argument will have to be a
                # multi-action.
                multiAction = firstArgument
    # Set the log level
    if options.verbose:
        loglevel = logging.DEBUG
    elif options.quiet:
        loglevel = logging.ERROR
    else:
        loglevel = logging.INFO
    if not project:
        log.error("Missing project.")
        parser.print_help()
        sys.exit(1)

    log.debug("Arguments have been read: project=%s, multiAction=%s.",
              project, multiAction)
    log.debug("Options: %r.", options)
    return (options, project, multiAction, loglevel)


def performActionOnProject(project, options):
    projectConfig = configuration.Configuration(project)
    Actions = actions.getActions()
    for Action in Actions:
        destination = parser.get_option(Action.option).dest
        if getattr(options, destination):
            action = Action(configuration=projectConfig)
            action.run(options=options)

def handleMultiAction(project, multiActionName):
    """Perform the options specified in the multiAction.

    A multi-action is a list of options you'd normally pass (in turn)
    to instancemanager.
    """

    projectConfig = configuration.Configuration(project)
    multiActions = projectConfig.configData['multi_actions']
    multiAction = multiActions.get(multiActionName, None)
    if not multiAction:
        log.error("No multi-action of this name found: %s.\n"
                  "Available multi-actions for this project: %s.\n"
                  "Note that the invocation of instancemanager has "
                  "changed lately.\n",
                  multiActionName,
                  multiActions.keys())
        parser.print_help()
        return
    for line in multiAction:
        # Turn the line into a list.
        arguments = line.split(' ')
        (options, args) = parser.parse_args(arguments)
        performActionOnProject(project, options)

def main():
    utils.initLog()
    options, project, multiAction, loglevel = parseArguments()
    utils.addConsoleLogging(loglevel)
    if project == 'ALL':
        log.info("Performing action on all projects.")
        projects = getProjects()
        for project in projects:
            log.info("Project: %s", project)
            performActionOnProject(project, options)
            if multiAction:
                handleMultiAction(project, multiAction)
    else:
        performActionOnProject(project, options)
        if multiAction:
            handleMultiAction(project, multiAction)


if __name__ == '__main__':
    main()
