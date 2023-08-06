###########
rotatezlogs
###########

By `Ingeniweb <http://www.ingeniweb.com>`_.

About
#####

This product provides two additional logger handlers to the standard
ones (see the doc in `zope.conf`) that rotate the log files.

It is not always possible to rotate Zope logs using system wide
services. This utility enables to rotate automatically Zope logs (with
or without zipping) using the features of the "logging" standard
module.

Don't look for new objects in the ZMI factory. All is configured in
`zope.conf` (see `Installation`_ below.)

This is mainly useful for Windows : rotating logs from an external
utility while Zope is up is not possible.

Note that the log rotation rules is based on the actual size of a log
file, and **not** on time periods (cron like).

Requirements
############

Tested with Zope 2.8, Zope 2.9, Zope 2.10, Windows and Unix.

`rotatezlogs` does not require additional product.

Will not work with Zope 2.7.x. We should completely rework
`component.xml` for this.

Installation
############

::

  $ easy_install [options] iw.rotatezlogs


Configure the rotating file logger handler
##########################################

In any logger directive of `zope.conf`, change the handler as in this
example for the <eventlog>.

::

  %import iw.rotatezlogs

  <eventlog>
    # Usual options, see the doc in zope.conf
    level info
    <rotatelogfile>
      # Required parameters
      # -------------------
      path $INSTANCE/log/event.log
      # We'll get up to 6 Mb of logs
      max-bytes 1MB
      backup-count 5

      # Optional parameters
      # -------------------
      # compression zip
      # format ------\n%(asctime)s %(levelname)s %(name)s %(message)s
    </rotatelogfile>
  </eventlog>

This works for other logs too (access, trace, zeo, ...).

When the size is about to be exceeded, the file is closed and a new
file is silently opened for output. Rollover occurs whenever the
current log file is nearly `max-bytes` in length; if `max-bytes` is
zero, rollover never occurs. If `backup-count` is non-zero, the system
will save old log files by appending the extensions ".1", ".2" etc.,
to the filename. For example, with a `backup-count` of 5 and a base
file name of `event.log`, you would get `event.log`, `event.log.1`,
`event.log.2`, up to `event.log.5`. The file being written to is
always `event.log`. When this file is filled, it is closed and renamed
to `event.log.1`, and if files `event.log.1`, `event.log.2`,
etc. exist, then they are renamed to `event.log.2`, `event.log.3`
etc. respectively.

If you want compressed rotated log files, you can add the optional
`compression` key parameter to the configuration. The value for `compression`
can be:

* `none` : the default, no compression is processed
* `zip` : rotated files are zipped to `xxx.log.1.zip` etc.
* `gzip` : rotated files are gzipped to `xxx.log.1.gz` etc.
* `bzip2` : rotated files are bzipped2 to `xxx.log.1.bz2` etc.

Note that some systems or Python installations come with no bzip2
support. In such case, we use `none` compression as fallback. You can
test the bzip2 support like this::

  $ python
  ...
  >>> import bz2

Install and configure a zope instance with buildout
###################################################

The easiest way. Edit your `buildout.cfg`::

  [instance]
  ...
  eggs =
    ...
    iw.rotatezlogs
    ...

  event-log-custom =
    %import iw.rotatezlogs
    <rotatelogfile>
      path ${buildout:directory}/var/log/instance.log
      max-bytes 1MB
      backup-count 5
    </rotatelogfile>

  access-log-custom =
    %import iw.rotatezlogs
    <rotatelogfile>
      path ${buildout:directory}/var/log/instance-Z2.log
      max-bytes 1MB
      backup-count 5
    </rotatelogfile>

See previous section for detailed explanations.

Copyright and license
#####################

Copyright (c) 2006-2008 Ingeniweb SAS

This software is subject to the provisions of the GNU General Public License,
Version 2.0 (GPL).  A copy of the GPL should accompany this distribution.
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
FOR A PARTICULAR PURPOSE

See the `.../rotatezlogs/LICENSE` file that comes with this product.

Testing
#######

Please read the `.../rotatezlogs/tests/README.txt`

Download
########

Stay in tune with the latest releases of `rotatezlogs`...

Subversion reposo:

  https://ingeniweb.svn.sourceforge.net/svnroot/ingeniweb/iw.rotatezlogs/

Releases:

  http://pypi.python.org/pypi/iw.rotatezlogs

Support
#######

`Mail to Ingeniweb support <mailto:support@ingeniweb.com>`_

`Donations are welcome for new features
<http://sourceforge.net/project/project_donations.php?group_id=74634>`_

Credits
#######

`The Ingeniweb team <http://www.ingeniweb.com>`_ (c) 2006-2008

* Main developer: `Gilles Lenfant <gilles.lenfant@ingeniweb.com>`_
* Eggification: `Tarek Ziade <tarek.ziade@ingeniweb.com>`_

Based on an idea by Mark Hammond.
