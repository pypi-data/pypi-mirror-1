# Copyright (c) 2007 Thomas Lotze
# See also LICENSE.txt

"""zc.buildout recipe for an Apache HTTP server root and apachectl script.
"""

import os
import os.path
import stat
import subprocess
import re

import pkg_resources

from tl.buildout_apache import config


MOD_LINE = re.compile("^\s*mod_(.*)\.c\s*$")


read_resource = lambda filename: pkg_resources.resource_string(__name__,
                                                               filename)


class Recipe(object):
    """zc.buildout recipe for an Apache HTTP server root and apachectl script.

    Configuration options:
        httpd

        ulimit
        conf-dir
        lynx-path

        user
        group
        listen
        modules

        servername
        serveradmin
        htdocs
        cgi-bin
        extra-config

        config-parts
    """

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options

        for key, value in config.items("root"):
            options.setdefault(key, value)

        options["location"] = os.path.join(
            buildout["buildout"]["parts-directory"], name)

        # Collect and normalize some options for buildout book-keeping.
        httpd_options = buildout[options.get("httpd", "httpd")]
        for name in "httpd-path", "envvars-path", "apxs-path", "module-dir":
            options.setdefault(name, httpd_options[name])

        for name in "htdocs", "cgi-bin":
            options[name] = os.path.normpath(os.path.join(
                buildout["buildout"]["directory"], options[name]))

        # We need to re-install after httpd was built differently in order to
        # query the built-in modules again.
        options["httpd-sig"] = (httpd_options["md5sum"] +
                                httpd_options["extra-options"])

        # Recursively collect unique config-parts, consider root as the
        # initial part, use self.options instead of options to avoid confusion
        # with (self.name, self.buildout[self.name]).
        config_parts = [(self.name, self.options)]
        for name, part in config_parts:
            parts = [(name, self.buildout[name])
                     for name in part.get("config-parts", "").split()]
            config_parts.extend(
                part for part in parts if part not in config_parts)

        options["modules"] = " ".join(sum((part.get("modules", "").split()
                                           for name, part in config_parts),
                                          []))

        options["extra-config"] = "\n".join(
            "#\n# Config part: %s\n#\n%s" % (name, part["extra-config"])
            for name, part in config_parts
            if "extra-config" in part)

    def install(self):
        options = self.options.copy()
        location = options["location"]

        # main server config
        options["listen"] = "\n".join(
            "Listen " + line for line in options["listen"].split())

        modules = options["modules"].split()
        builtins = builtin_modules(options["httpd-path"])
        options["load-module"] = "\n".join(
            "LoadModule %s_module %s/mod_%s.so" %
            (module, options["module-dir"], module)
            for module in set(modules).difference(builtins))

        names = options["servername"].split()
        options["servername"] = "ServerName " + names.pop(0)
        options["serveralias"] = "\n".join(
            "ServerAlias " + name for name in names)

        admin = options.setdefault("serveradmin", "")
        if admin:
            options["serveradmin"] = "ServerAdmin " + admin

        # directories
        for sub in "", "conf", "lock", "log", "run":
            path = os.path.join(location, sub)
            if not os.path.exists(path):
                os.mkdir(path)
            else:
                assert os.path.isdir(path)

        #files
        conf_path = os.path.join(location, "conf", "httpd.conf")
        ctl_path = os.path.join(self.buildout["buildout"]["bin-directory"],
                                self.name)

        options["conf-path"] = conf_path
        options["serverroot"] = location

        open(conf_path, "w").write(read_resource("httpd.conf.in") % options)

        open(ctl_path, "w").write(read_resource("apachectl.in") % options)
        os.chmod(ctl_path, (os.stat(ctl_path).st_mode |
                            stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))

        return [location,
                ]

    def update(self):
        pass


def builtin_modules(httpd_path):
    """Query the httpd binary for its built-in modules.
    """
    stdout, ignored = subprocess.Popen([httpd_path, "-l"],
                                       stdout=subprocess.PIPE).communicate()
    return (mo.groups(0)[0]
            for mo in (MOD_LINE.search(line)
                       for line in stdout.splitlines())
            if mo)
