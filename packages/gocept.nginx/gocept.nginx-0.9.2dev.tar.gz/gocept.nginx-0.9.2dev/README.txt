==========================
NGNIX configuration recipe
==========================

The gocept.nginx recipe allows to configure an ngin in buildout::

    [ngnix]
    recipe = gocept.cmmi
    url = http://sysoev.ru/nginx/nginx-0.5.30.tar.gz
    md5sum = 804cf3d6583fe820de42c5e7c50d7a1a

    [frontend]
    recipe = gocept.nginx
    hostname = localhost
    port = 8080
    configuration = 
        worker_processes 1;
        events {
            worker_connections 1024;
        }
        http {
          ...



Changes
=======

0.9.1 (2008-06-18)
------------------

- Fix configtest command in the generated ctl script.

0.9 (2008-01-14)
----------------

- Allowing configuration of config file location.

- Writing config file in own part by default.
