# Copyright (c) 2007 Thomas Lotze
# See also LICENSE.txt

"""zc.buildout recipe for creating a virtual Python installation
"""

import os
import os.path
from os.path import join
import sys
import shutil
import subprocess


class Recipe(object):
    """zc.buildout recipe for creating a virtual Python installation

    Configuration options:
        executable-name
        real-python
        site-packages
        extra-paths
        headers

    Exported options:
        location
        executable
    """

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name

        # set some defaults
        self.options = {
            "executable-name": "python",
            "real-python": sys.executable,
            "site-packages": "",
            "extra-paths": "",
            "headers": "",
            }
        self.options.update(options)
        options = self.options

        # export some options
        options["location"] = join(
            buildout["buildout"]["parts-directory"], name)
        options["executable"] = join(
            options["location"], "bin", options["executable-name"])

        # explore the real Python, store fingerprint
        real = options["real-python"]
        options["__real-executable__"] = real
        options["__python-version__"] = subprocess.Popen(
            [real, "-c", "import sys; print sys.version; "
                         "print sys.prefix; print sys.exec_prefix"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]

    def install(self):
        options = self.options
        location = options["location"]
        executable = options["executable"]

        real = options["__real-executable__"]
        pythonx_y = "python" + options["__python-version__"][:3]
        prefix, exec_prefix = options["__python-version__"].splitlines()[-2:]

        if os.path.exists(location):
            shutil.rmtree(location)
        os.mkdir(location)

        # copy the executable
        os.mkdir(join(location, "bin"))
        shutil.copy(real, executable)

        # link standard modules
        lib = join(location, "lib", pythonx_y)
        os.makedirs(lib)
        real_lib = join(prefix, "lib", pythonx_y)
        for item in os.listdir(real_lib):
            if item != "site-packages":
                os.symlink(join(real_lib, item), join(lib, item))
        site_packages = join(lib, "site-packages")
        os.mkdir(site_packages)
        if exec_prefix != prefix:
            real_exec_lib = join(prefix, "lib", pythonx_y)
            for item in os.listdir(real_exec_lib):
                os.symlink(join(real_exec_lib, item), join(lib, item))

        # handle site packages and extra paths
        lines = []
        if boolean(options["site-packages"]):
            lines.append("import site; site.addsitedir('%s')" %
                         join(real_lib, "site-packages"))
        lines.extend(line.strip() for line in options["extra-paths"])
        if lines:
            pth = open(join(site_packages, "virtual-python.pth"), "w")
            pth.writelines(line + "\n" for line in lines)
            pth.close()

        # link headers
        if boolean(options["headers"]):
            os.mkdir(join(location, "include"))
            os.symlink(join(prefix, "include", pythonx_y),
                       join(location, "include", pythonx_y))

        # make the executable available in buildout's bin directory
        bin = join(self.buildout["buildout"]["bin-directory"],
                   options["executable-name"])
        if os.path.exists(bin):
            os.remove(bin)
        os.symlink(executable, bin)

        return [location, bin]


def boolean(value):
    return value.lower() in (1, "yes", "true", "on")
