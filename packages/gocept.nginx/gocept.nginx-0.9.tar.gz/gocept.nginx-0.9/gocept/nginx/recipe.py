"""zc.buildout recipe for an Apache HTTP server root and apachectl script.
"""

import os
import os.path
import stat

import pkg_resources


read_resource = lambda filename: pkg_resources.resource_string(__name__,
                                                               filename)


class Recipe(object):
    """zc.buildout recipe configuring an nginx server and startup script.

    Configuration options:
        nginx

        configuration
    """

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options

        location = options["location"] = os.path.join(
            buildout["buildout"]["parts-directory"], name)

        if not os.path.exists(location):
            os.mkdir(location)

        options.setdefault('nginx', 'nginx')
        options.setdefault('config_file', os.path.join(options['location'],
                                                       'nginx.conf'))
        options.setdefault('pid_file', os.path.join(options['location'],
                                                    'nginx.pid'))
        options.setdefault('ngnix_location', os.path.join(
            buildout["buildout"]["parts-directory"], options['nginx']))

    def install(self):
        location = self.options["location"]
        # Write the configuration file
        conf_path = os.path.join(self.options['config_file'])
        config_file = file(conf_path, 'w')
        config_file.write('pid %s;\n' % self.options['pid_file'])
        config_file.write(self.options['configuration'])

        # files
        ctl_path = os.path.join(self.buildout["buildout"]["bin-directory"],
                                self.name)
        open(ctl_path, "w").write(read_resource("nginxctl.in") % self.options)

        os.chmod(ctl_path, (os.stat(ctl_path).st_mode |
                            stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))

        return [ctl_path]

    def update(self):
        pass
