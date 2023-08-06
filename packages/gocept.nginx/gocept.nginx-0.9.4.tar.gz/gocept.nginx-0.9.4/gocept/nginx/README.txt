==========================
NGNIX configuration recipe
==========================

The gocept.nginx recipe allows to configure an nginx in buildout:

>>> write("buildout.cfg", """
... [buildout]
... parts = frontend
...
... [frontend]
... recipe = gocept.nginx
... configuration = 
...     worker_processes 1;
...     events {
...         worker_connections 1024;
...     }
...     http {
...         # configuration
...     }
... """)

>>> print system(buildout),
Installing frontend.

There is a script called ``frontend`` which is used to control nginx:

>>> cat('bin', 'frontend')
#!/bin/sh
ARGV="$@"
NGINX='.../_TEST_/sample-buildout/parts/nginx/sbin/nginx'
PIDFILE='.../_TEST_/sample-buildout/parts/frontend/frontend.pid'
CONFIGURATION='.../_TEST_/sample-buildout/parts/frontend/frontend.conf'
<BLANKLINE>
ERROR=0
if [ "x$ARGV" = "x" ] ; then 
    ARGV="-h"
fi
<BLANKLINE>
case $ARGV in
start)
    echo "Starting nginx "
    $NGINX -c $CONFIGURATION
    error=$?
    ;;
stop)
    echo "Stopping nginx "
    kill `cat $PIDFILE`
    error=$?
    ;;
reload)
    echo "Reloading nginx "
    kill -HUP `cat $PIDFILE`
    error=$?
    ;;
reopen_transcript)
    echo "Reopening logfiles"
    kill -USR1 `cat $PIDFILE`
    error=$?
    ;;
configtest)
    echo "Testing nginx configuration "
    $NGINX -c $CONFIGURATION -t
    ERROR=$?
    ;;
esac
<BLANKLINE>
exit $ERROR

In the parts directory the configuration file is created. Note that the PID
file location is prepended automatically. Also there is a default for
``access_log`` and ``error_log``

>>> ls('parts')
d  frontend
>>> ls('parts', 'frontend')
-  frontend.conf
>>> cat('parts', 'frontend', 'frontend.conf')
pid .../_TEST_/sample-buildout/parts/frontend/frontend.pid;
lock_file .../_TEST_/sample-buildout/parts/frontend/frontend.lock;
error_log .../_TEST_/sample-buildout/parts/frontend/frontend-error.log;
worker_processes 1;
events {
worker_connections 1024;
}
http {
access_log .../_TEST_/sample-buildout/parts/frontend/frontend-access.log;
# configuration
}


If an ``error_log`` or ``access_log`` statement is specified anywhere in the
configuration the respective statement will not be added automatically:

>>> write("buildout.cfg", """
... [buildout]
... parts = frontend
...
... [frontend]
... recipe = gocept.nginx
... configuration = 
...     worker_processes 1;
...     error_log /dev/null
...     events {
...         worker_connections 1024;
...     }
...     http {
...         # configuration
...         access_log /dev/null
...     }
... """)

>>> print system(buildout),
Uninstalling frontend.
Installing frontend.

>>> cat('parts', 'frontend', 'frontend.conf')
pid .../_TEST_/sample-buildout/parts/frontend/frontend.pid;
lock_file .../_TEST_/sample-buildout/parts/frontend/frontend.lock;
<BLANKLINE>
worker_processes 1;
error_log /dev/null
events {
worker_connections 1024;
}
http {
# configuration
access_log /dev/null
}


Deployment support
++++++++++++++++++

The recipe is zc.deployment compatible. The created files will be put in the
deployment specifig locations:


>>> mkdir('etc')
>>> mkdir('init.d')
>>> mkdir('logrotate')

>>> write("buildout.cfg", """
... [buildout]
... parts = frontend
...
... [deploy]
... user = testuser
... name = testdeploy
... etc-directory = etc
... rc-directory = init.d
... log-directory = logs
... run-directory = run
... logrotate-directory = logrotate
...
... [frontend]
... recipe = gocept.nginx
... deployment = deploy
... configuration = 
...     worker_processes 1;
...     events {
...         worker_connections 1024;
...     }
...     http {
...         # config
...     }
... """)

>>> print system(buildout),
Uninstalling frontend.
Installing frontend.


The ctl-script is in init.d now:

>>> cat('init.d', 'testdeploy-frontend')
#!/bin/sh
ARGV="$@"
NGINX='.../_TEST_/sample-buildout/parts/nginx/sbin/nginx'
PIDFILE='run/frontend.pid'
CONFIGURATION='etc/frontend.conf'
...

The config file also includes the user now:

>>> cat('etc', 'frontend.conf')
pid run/frontend.pid;
lock_file run/frontend.lock;
user testuser;
error_log logs/frontend-error.log;
worker_processes 1;
events {
worker_connections 1024;
}
http {
access_log logs/frontend-access.log;
# config
}


If we're in deployment mode log-rotate files are also created:

>>> cat('logrotate', 'testdeploy-frontend')
logs/frontend-error.log {
  rotate 5
  weekly
  postrotate
    init.d/testdeploy-frontend reopen_transcript
  endscript
}
logs/frontend-access.log {
  rotate 5
  weekly
  postrotate
    init.d/testdeploy-frontend reopen_transcript
  endscript
}

When a log file is given by the user, no logrotate is created:

>>> write("buildout.cfg", """
... [buildout]
... parts = frontend
...
... [deploy]
... user = testuser
... name = testdeploy
... etc-directory = etc
... rc-directory = init.d
... log-directory = logs
... run-directory = run
... logrotate-directory = logrotate
...
... [frontend]
... recipe = gocept.nginx
... deployment = deploy
... configuration = 
...     worker_processes 1;
...     events {
...         worker_connections 1024;
...     }
...     http {
...         # config
...         access_log /dev/null
...     }
... """)

>>> print system(buildout),
Uninstalling frontend.
Installing frontend.

>>> cat('logrotate', 'testdeploy-frontend')
logs/frontend-error.log {
  rotate 5
  weekly
  postrotate
    init.d/testdeploy-frontend reopen_transcript
  endscript
}


Setting the user in the nginx config only works when nginx is started as root.
Since that is often not the case setting the user can be prevented by setting
the user variable to "empty":

>>> write("buildout.cfg", """
... [buildout]
... parts = frontend
...
... [deploy]
... user = testuser
... name = testdeploy
... etc-directory = etc
... rc-directory = init.d
... log-directory = logs
... run-directory = run
... logrotate-directory = logrotate
...
... [frontend]
... recipe = gocept.nginx
... deployment = deploy
... user =
... configuration = 
...     worker_processes 1;
...     events {
...         worker_connections 1024;
...     }
...     http {
...         # config
...     }
... """)
>>> print system(buildout),
Uninstalling frontend.
Installing frontend.

>>> cat('etc', 'frontend.conf')
pid run/frontend.pid;
lock_file run/frontend.lock;
error_log logs/frontend-error.log;
worker_processes 1;
events {
worker_connections 1024;
}
http {
access_log logs/frontend-access.log;
# config
}
