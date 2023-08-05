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
        extra-env
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
        for key in "httpd-path", "envvars-path", "apxs-path", "module-dir":
            options.setdefault(key, httpd_options[key])

        for key in "htdocs", "cgi-bin":
            options[key] = os.path.normpath(os.path.join(
                buildout["buildout"]["directory"], options[key]))

        # We need to re-install after httpd was built differently in order to
        # query the built-in modules again.
        options["httpd-sig"] = (httpd_options.get("md5sum", "") +
                                httpd_options.get("extra-options", ""))

        # Recursively collect unique config-parts, breadth-first, considering
        # root as the initial part.
        config_parts = [(name, options)]
        for name, part in config_parts:
            parts = [(name, buildout[name])
                     for name in part.get("config-parts", "").split()]
            config_parts.extend(
                part for part in parts if part not in config_parts)

        # Collect unique modules from config-parts, in order.
        self.modules = []
        for name, part in config_parts:
            self.modules.extend(module
                                for module in part.get("modules", "").split()
                                if module not in self.modules)
        options["modules"] = " ".join(self.modules)

        # Format other config-parts stuff.
        for key, format in (
            ("extra-env", lambda part: "".join("export %s\n" % line.strip()
                                               for line in part.splitlines()
                                               if line.strip())),
            ("extra-config", lambda part: part),
            ):
            options[key] = "\n".join(
                "#\n# Config part: %s\n#\n%s" % (name, value)
                for name, value in ((name, format(part.get(key, "")))
                                    for name, part in config_parts)
                if value)

    def install(self):
        options = self.options.copy()
        location = options["location"]

        # main server config
        options["listen"] = "\n".join(
            "Listen " + line for line in options["listen"].split())

        builtins = set(builtin_modules(options["httpd-path"]))
        options["load-module"] = "\n".join(
            "LoadModule %s_module %s/mod_%s.so" %
            (module, options["module-dir"], module)
            for module in self.modules
            if module not in builtins)

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
                ctl_path,
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
