# Copyright (c) 2007-2009 Thomas Lotze
# See also LICENSE.txt

"""zc.buildout recipe to build the mod_python Apache module.
"""

import os
import os.path
import tempfile
import shutil
import subprocess
import md5 # deprecated in 2.5, but hashlib isn't in 2.4 yet

import gocept.cmmi
import pkg_resources
import virtualenv

from tl.buildout_apache import config


class Recipe(gocept.cmmi.Recipe):
    """zc.buildout recipe to build the mod_python Apache module.

    Configuration options:
        url
        md5sum
        extra-options
        extra-vars

        httpd
        python
        virtualenv

    Exported options:
        modpython
        executable
    """

    def __init__(self, buildout, name, options):
        super(Recipe, self).__init__(buildout, name, options)

        location = options["location"]

        for key, value in config.items("modpython"):
            options.setdefault(key, value)

        # mod_python.so stuff
        httpd = options.get("httpd", "httpd")
        self.apxs_path = buildout[httpd]["apxs-path"]
        options.setdefault("modpython",
                           os.path.join(location, "mod_python.so"))

        # Determine some paths relevant to the Python installation, depending
        # on whether we are to create our own virtual environment. If so, it
        # is OK to do this using the same Python interpreter as the buildout.
        python = options.get("python", buildout["buildout"]["python"])
        self.real_executable = buildout[python]["executable"]
        self.virtualenv = boolean(options["virtualenv"])
        if self.virtualenv:
            (self.python_home, self.python_lib,
             self.python_inc, self.python_bin) = (
                virtualenv.path_locations(os.path.join(location, "python")))
            self.executable = os.path.join(
                self.python_bin, os.path.basename(self.real_executable))
        else:
            self.executable = self.real_executable

        # Determine a place to keep the mod_python Python module.
        self.lib_dir = os.path.join(location, "lib")

        # We export the exact executable name to be used by mod_python. It
        # needs to be named "python" and it must be found on httpd's PATH.
        options.setdefault(
            "executable",
            os.path.join(os.path.dirname(self.executable), "python"))

        # We need to re-install after httpd or python were built differently.
        checksum = md5.new()
        checksum.update(repr(sorted(buildout[httpd].values())))
        if python == "buildout":
            checksum.update(open(self.real_executable).read())
        else:
            checksum.update(repr(sorted(buildout[python].values())))
        options["__dependencies-sig__"] = checksum.hexdigest()

    def install(self):
        options = self.options

        # Create the virtual Python environment if needed.
        if self.virtualenv:
            _, venv_path = tempfile.mkstemp()
            venv = open(venv_path, 'w')
            venv.write(VENV_TEMPLATE % dict(
                    # The egg located here may not correspond to the Python
                    # version being virtualized. This should not be a problem,
                    # though.
                    virtualenv_location=pkg_resources.working_set.find(
                        pkg_resources.Requirement.parse("virtualenv")
                        ).location,
                    home_dir=self.python_home,
                    lib_dir=self.python_lib,
                    inc_dir=self.python_inc,
                    bin_dir=self.python_bin,
                    ))
            venv.close()
            executable = subprocess.Popen(
                [self.real_executable, venv_path],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
                ).communicate()[0]
            assert executable.strip() == self.executable
            os.unlink(venv_path)

        # Run the CMMI process for mod_python. Configure options are up to
        # date as they are included in the dependency signature.
        options["extra-options"] = ("--with-apxs=%s --with-python=%s " %
                                    (self.apxs_path, self.executable) +
                                    options.get("extra-options", ""))
        install_dir = tempfile.mkdtemp("buildout-install-" + self.name)
        options["extra-vars"] = ('DESTDIR="%s"\n' % install_dir +
                                 options.get("extra-vars", ""))

        parts = super(Recipe, self).install()

        # Put the goodies in a sane place.
        for dirpath, dirnames, filenames in os.walk(install_dir):
            if "mod_python.so" in filenames:
                shutil.move(os.path.join(dirpath, "mod_python.so"),
                            options["modpython"])
            if "mod_python" in dirnames:
                shutil.move(dirpath, self.lib_dir)

        shutil.rmtree(install_dir)

        # Make sure the Python executable is found by mod_python.
        if self.create_python_executable():
            parts.append(options["executable"])

        # Make the mod_python package available to the Python installation.
        parts.append(self.install_module())

        return parts

    def update(self):
        self.create_python_executable()
        self.install_module()

    def create_python_executable(self):
        # The Python interpreter to be used by mod_python needs to be named
        # "python". Since the real executable is that of a writable Python
        # installation, it should be safe enough to assume that creating a
        # symbolic link named "python" will not cause a file name clash
        # between different versions of the Python interpreter. This is done
        # at every update since it is cheap and saves us worrying about
        # whether the link might have been removed by an update or re-install
        # of the Python environment.
        if self.executable != self.options["executable"]:
            os.symlink(self.executable, self.options["executable"])
            return True

    def install_module(self):
        # Write paths to pth file in correct site-packages directory. At least
        # the modpython module must already be on the Python path when
        # mod_python is loaded as it is imported before the PythonPath option
        # gets evaluated. This is done at every update since it is cheap and
        # saves us worrying about whether the path file might have been
        # removed by an update or re-install of the Python environment.

        out = subprocess.Popen(
            [self.options["executable"], "-c",
             "import sys; print sys.version; print sys.prefix"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
            ).communicate()[0]

        version = out[:3]
        prefix = out.splitlines()[-1].strip()

        pth_filename = os.path.join(prefix, "lib", "python" + version,
                                    "site-packages", "mod_python.pth")
        pth = open(pth_filename, "w")
        pth.write(self.lib_dir)
        pth.close()

        return pth_filename


def boolean(value):
    return value.lower() in (1, "yes", "true", "on")


VENV_TEMPLATE = """\
import sys
sys.path.insert(0, %(virtualenv_location)r)
import virtualenv
import logging
virtualenv.logger = virtualenv.Logger([(logging.DEBUG, sys.stderr)])
try:
 print virtualenv.install_python(
    %(home_dir)r, %(lib_dir)r, %(inc_dir)r, %(bin_dir)r,
    site_packages=True, clear=True)
except:
 pass
"""
