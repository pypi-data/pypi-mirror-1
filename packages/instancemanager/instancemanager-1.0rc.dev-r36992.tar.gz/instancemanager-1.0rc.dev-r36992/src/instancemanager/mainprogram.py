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

def getProjects():
    userDir = os.path.expanduser('~')
    configDir = os.path.join(userDir, config.CONFIGDIR)
    results = [p.replace('.py', '') for p in os.listdir(configDir)
               if p.endswith('.py')
               and (p not in ['__init__.py', 'userdefaults.py'])
               and (not p.startswith(config.SECRET_PREFIX))
               and (not p.startswith(config.STUB_PREFIX))]
    return results

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
        projects = getProjects()
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
parser.add_option(
    '--manifest',
    '-m',
    help='Print Manifest of installed Products and collisions',
    action='store_true',
    default=False)

actions.addOptions(parser)

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


def performActionOnProject(projectConfig, options):
    Actions = actions.getActions()
    for Action in Actions:
        destination = parser.get_option(Action.option).dest
        if getattr(options, destination):
            action = Action(configuration=projectConfig)
            action.run(options=options)

def handleMultiAction(projectConfig, multiActionName):
    """Perform the options specified in the multiAction.

    A multi-action is a list of options you'd normally pass (in turn)
    to instancemanager.
    """

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
        log.debug("Extracting arguments from line %r.",
                  line)
        # Compensate for '--test "-a bcd -d efg"' arguments that are
        # intended as one single argument.
        copiedArguments = []
        insideDoubleQuotes = False
        inQuotes = []
        for argument in arguments:
            log.debug("Argument part: %r.", argument)
            if insideDoubleQuotes:
                if argument.endswith('"'):
                    inQuotes.append(argument[:-1])
                    joined = ' '.join(inQuotes)
                    copiedArguments.append(joined)
                    insideDoubleQuotes = False
                else:
                    inQuotes.append(argument)
            else:
                if argument.startswith('"'):
                    inQuotes = [argument[1:],]
                    insideDoubleQuotes = True
                    log.debug("Start of stuff inside double quotes: %r",
                              inQuotes)
                else:
                    copiedArguments.append(argument)
        arguments = copiedArguments
        log.debug("Remaining arguments: %r.", arguments)
        (options, args) = parser.parse_args(arguments)
        performActionOnProject(projectConfig, options)

def main():
    utils.initLog()
    options, project, multiAction, loglevel = parseArguments()
    utils.addConsoleLogging(loglevel)
    if project == 'ALL':
        log.info("Performing action on all projects.")
        projects = getProjects()
        for project in projects:
            log.info("Project: %s", project)
            projectConfig = configuration.Configuration(project)
            performActionOnProject(projectConfig, options)
            if multiAction:
                handleMultiAction(projectConfig, multiAction)
    else:
        log.info("Project: %s", project)
        projectConfig = configuration.Configuration(project)
        performActionOnProject(projectConfig, options)
        if multiAction:
            handleMultiAction(projectConfig, multiAction)


if __name__ == '__main__':
    main()
