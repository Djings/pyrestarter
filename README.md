pyrestarter
===========

Restart your python scripts when their source files change.


This simple python script can restart other python scripts, when their codebase changes.


Required Libraries/Tools
------------------------

* watchdog (https://pypi.python.org/pypi/watchdog/)
    - for watching the filesystem

* snakefood (http://furius.ca/snakefood/)
    - for the dependency analysis

In Ubuntu it comes down to:
```
apt-get install snakefood python-pip
pip install watchdog
```

A word on dependencies
------------

By default the pyrestarter only watches dependent files below the current root to speed
up the dependency parsing. If you wish to restart uppon updated system libraries or libraries
installed elsewhere, specify the -g option to watch for global dependencies.

Usage
-----

restarter <yourscript.py> [your script argument [ more args ... ] ]

Shutdown the restarting script with CTRL+C or SIGINT.
