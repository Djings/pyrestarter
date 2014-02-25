pyrestarter
===========

Restart your python scripts when their source files change.


This simple python script can restart other python scripts, when their codebase changes.


Required Libraries/Tools
========================

* watchdog (https://pypi.python.org/pypi/watchdog/)
    - for watching the filesystem

* snakefood (http://furius.ca/snakefood/)
    - for the dependency analysis

In Ubuntu it comes down to:
```
apt-get install snakefood python-pip
pip install watchdog
```


Usage
=====

python restarter.py <yourscript.py>

Shutdown the restarting script with CTRL+C or SIGINT.
