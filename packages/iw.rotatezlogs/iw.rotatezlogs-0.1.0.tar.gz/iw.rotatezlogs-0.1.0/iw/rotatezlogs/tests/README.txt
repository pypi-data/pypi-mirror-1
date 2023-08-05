######################
rotatezlogs unit tests
######################

Prepare testing
###############

You **must** install `rotatezlogs` in $SOFTWARE_HOME/Products and
**not** in $INSTANCE_HOME/Products to run unit tests. Unit tests
**cannot** work if the files of this product are installed in a Zope
$INSTANCE_HOME/Products.

Note that you may otherwise install `rotatezlogs` in an
$INSTANCE_HOME/Products folder.

You must set the environment variable PYTHONPATH to your SOFTWARE_HOME
before running the tests.

Examples
########

Windows example:

::

  > set PYTHONPATH=C:\path\to\zope\lib\python
  > c:\path\to\python.exe test_rotatezlogs.py

Unix example:

::

  $ export PYTHONPATH=/path/to/zope/lib/python
  $ python test_rotatezlogs.py
