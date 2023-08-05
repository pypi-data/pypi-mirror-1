#!/usr/bin/env python
"""Prepare userdefaults.py (for in the skeleton directory).

Copies instancemanager's 'defaults.py' to the skeleton directory's
'userdefaults.py'. It comments-out  the default values.  
"""

def handleLine(line):
    """Return a cleaned-up line.

    What we need to do is just to return the original line, except to
    comment out non-comment lines with a '=' in them.
    """

    if not line.startswith('#'):
        # Non-comment line, could be inside a documentation block,
        # though. So we check for presence of a '=' character (which
        # we thereby forbid in documentation blocks).
        if '=' in line:
            return '#     ' + line
    # Otherwise, just return the original line
    return line

def copyFileContents():
    defaults = open('defaults.py', 'r')
    userdefaults = open('skeleton/userdefaults.py', 'w')
    for line in defaults.readlines():
        newLine = handleLine(line)
        userdefaults.write(newLine)
    defaults.close()
    userdefaults.close()
    

if __name__ == '__main__':
    copyFileContents()
    print "Copied defaults.py to skeleton/userdefaults.py"
    print """WARNING: "multi_actions" are not
copied correctly at the moment by the
copy_defaults_to_userdefaults.py script.
So remove those by hand afterwards.
Yes, that means you! :)"""
