"""zc.buildout recipe for an Apache HTTP server root and apachectl script.
"""

import os
import os.path
import re
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
        self.name = name
        self.options = options

        deployment = self.deployment = options.get('deployment')
        if deployment:
            self.deployment = buildout[deployment].get('name', deployment)
            options['etc-directory'] = buildout[deployment]['etc-directory']
            options['rc-directory'] = buildout[deployment]['rc-directory']
            options['run-directory'] = buildout[deployment]['run-directory']
            options['log-directory'] = buildout[deployment]['log-directory']
            options['logrotate'] = os.path.join(
                buildout[deployment]['logrotate-directory'],
                self.deployment + '-' + self.name)
            options['user'] = buildout[deployment]['user']
        else:
            options["run-directory"] = os.path.join(
                buildout["buildout"]["parts-directory"], name)
            options['rc-directory'] = buildout['buildout']['bin-directory']

        options.setdefault('nginx', 'nginx')
        options.setdefault('nginx_location', os.path.join(
            buildout["buildout"]["parts-directory"], options['nginx']))

    def install(self):
        options = self.options
        if self.deployment:
            prefix = self.deployment + '-'
        else:
            options['etc-directory'] = options["log-directory"] = \
                options["run-directory"]
            prefix = ""
            if not os.path.exists(options['run-directory']):
                os.mkdir(options['run-directory'])
                options.created(options['run-directory'])

        config_path = os.path.join(
            options['etc-directory'],
            prefix+self.name+'.conf')
        ctl_path = os.path.join(options["rc-directory"],
                                prefix+self.name)
        pid_path = os.path.join(
            options['run-directory'], prefix+self.name+'.pid')
        lock_path = os.path.join(
            options['run-directory'], prefix+self.name+'.lock')
        error_log_path = os.path.join(
            options['log-directory'], prefix+self.name+'-error.log')
        access_log_path = os.path.join(
            options['log-directory'], prefix+self.name+'-access.log')

        # Write the configuration file
        configuration = options['configuration']
        config_file = file(config_path, 'w')
        config_file.write('pid %s;\n' % pid_path)
        config_file.write('lock_file %s;\n' % lock_path)
        if self.deployment:
            config_file.write('user %s;\n' % options['user'])
        rotate_error_log = rotate_access_log = False
        if re.search(r'^\s*error_log ', configuration, re.M) is None:
            config_file.write('error_log %s;' % error_log_path)
            rotate_error_log = True
        if re.search(r'^\s*access_log ', configuration, re.M) is None:
            pattern = re.compile(r'^(\s*http\s*{)$', re.M)
            configuration = pattern.sub(
                '\\1\naccess_log %s;' % access_log_path, configuration)
            rotate_access_log = True
        config_file.write(configuration)
        config_file.close()
        options.created(config_path)

        # files
        open(ctl_path, "w").write(read_resource("nginxctl.in") % dict(
            nginx_location=options['nginx_location'],
            pid_file=pid_path,
            config_file=config_path))

        os.chmod(ctl_path, (os.stat(ctl_path).st_mode |
                            stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))
        options.created(ctl_path)

        if self.deployment and (rotate_error_log or rotate_access_log):
            logrotate_path = options['logrotate']
            logrotate_file = open(logrotate_path, 'w')
            if rotate_error_log:
                logrotate_file.write(logrotate_template % dict(
                    logfile=error_log_path,
                    rc=ctl_path))
            if rotate_access_log:
                logrotate_file.write(logrotate_template % dict(
                    logfile=access_log_path,
                    rc=ctl_path))
            logrotate_file.close()
            options.created(logrotate_path)

        return options.created()

    def update(self):
        pass


logrotate_template = """%(logfile)s {
  rotate 5
  weekly
  postrotate
    %(rc)s reopen_transcript
  endscript
}
"""
