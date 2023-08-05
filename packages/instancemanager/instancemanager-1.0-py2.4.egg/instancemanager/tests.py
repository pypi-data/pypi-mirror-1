#! /usr/bin/env python2.4

# Import the modules
import actionutils
import configuration
import sources

# Add the modules that you want to test via doctests.
modules = (
    actionutils,
    configuration,
    sources,
    )

def _test():
    import doctest
    import sys
    optionflags = (doctest.ELLIPSIS |
                   doctest.NORMALIZE_WHITESPACE |
                   doctest.REPORT_ONLY_FIRST_FAILURE)
    verbose = "-v" in sys.argv
    for mod in modules:
        doctest.testmod(mod, verbose=verbose,
                        optionflags=optionflags, report=0)
    doctest.master.summarize()

if __name__ == "__main__":
    _test()

