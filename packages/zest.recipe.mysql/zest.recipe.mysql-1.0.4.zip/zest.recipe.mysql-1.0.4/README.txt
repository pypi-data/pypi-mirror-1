Recipe to install Mysql
=======================

Code repository: 
http://svn.plone.org/svn/collective/buildout/zest.recipe.mysql


It can be a problem getting both mysql and mysql's python binding to install
reliably on everyone's development machine. Problems we encountered were
mostly on the mac, as mysql gets installed into different locations by the
official mysql distribution, macports and fink. And on the mac, the python
binding needs a patch.

One solution: fix the underlying stuff and make mysql and mysql-python a
dependency that has to be handled by the OS. Alternative solution: this
'zest.recipe.mysql' recipe. **Warning: rough edges**. It is not a properly
documented and tested package as it originally was a quick
need-to-get-something-working-now job.

Here's a quick piece of buildout to get you started if you want to test
it::

 [buildout]
 parts =
     mysql
     ...

 [mysql]
 recipe = zest.recipe.mysql
 # Note that these urls usually stop working after a while... thanks...
 mysql-url = http://dev.mysql.com/get/Downloads/MySQL-5.0/mysql-5.0.86.tar.gz/from/http://mysql.proserve.nl/
 mysql-python-url = http://surfnet.dl.sourceforge.net/sourceforge/mysql-python/MySQL-python-1.2.2.tar.gz

 [plone]
 ...
 eggs =
     ...
     ${mysql:eggs}

* This ought to download and install mysql and mysql-python.

* Mysql and mysql-python end up in '.../parts/mysql'.

* mysql-python is installed as a development egg by buildout.

* The socket and the database are in '.../var/mysql'.

Options
-------

``mysql-url`` -- Download URL for the target version of MySQL (required).

``mysql-python-url`` -- Download URL for the target version of the
Python wrappers (required)

``python`` -- path to the Python against which to build the wrappers
(optional, currrently unused).

``config-skeleton`` -- path to a file used as a template for generating
the instance-local ``my.cnf`` file (optional).  If this option is not
supplied, no configuration will be generated.  If passed, the text from
the indicated file will be used as a Python string template, with the
following keys passed in the mapping to the ``%`` operator:

 - ``MYSQLD_INSTALL``

 - ``MYSQLD_SOCKET``

 - ``MYSQLD_PIDFILE``

 - ``DATADIR``

``with-innodb`` -- if set to a non-false value, will pass the
``--with-innodb`` option to the configure command.
