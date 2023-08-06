# Copyright (c) 2007, 2008 Thomas Lotze
# See also LICENSE.txt

"""zc.buildout recipe for creating a virtual Python installation
"""

import os
import os.path
from os.path import join
import sys
import shutil
import subprocess

import pkg_resources


class Recipe(object):
    """zc.buildout recipe for creating a virtual Python installation

    Configuration options:
        executable-name
        real-python
        site-packages
        eggs
        extra-paths
        headers

    Exported options:
        location
        executable
    """

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options

        # set some defaults
        options.setdefault("executable-name", "python")
        options.setdefault("real-python", sys.executable)
        options.setdefault("site-packages", "false")
        options.setdefault("extra-paths", "")
        options.setdefault("headers", "false")

        # Create the egg recipe instance now to let it initialize the options.
        self.egg = pkg_resources.load_entry_point(
            "zc.recipe.egg", "zc.buildout", "eggs")(buildout, name, options)

        # export some options
        options["location"] = join(
            buildout["buildout"]["parts-directory"], name)
        options["executable"] = join(
            options["location"], "bin", options["executable-name"])

        # explore the real Python, store fingerprint
        options["__python-version__"] = subprocess.Popen(
            [options["real-python"], "-c", "import sys; " +
             "print sys.version; print sys.prefix; print sys.exec_prefix"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]

    def install(self):
        options = self.options
        location = options["location"]
        executable = options["executable"]

        pythonx_y = "python" + options["__python-version__"][:3]
        prefix, exec_prefix = options["__python-version__"].splitlines()[-2:]

        if os.path.exists(location):
            shutil.rmtree(location)
        os.mkdir(location)

        # copy the executable
        os.mkdir(join(location, "bin"))
        shutil.copy(options["real-python"], executable)

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

        # handle site packages, eggs and extra paths
        lines = []
        if boolean(options["site-packages"]):
            lines.append("import site; site.addsitedir('%s')" %
                         join(real_lib, "site-packages"))
        if options.get("eggs"):
            ignored, working_set = self.egg.working_set(())
            lines.extend(spec.location for spec in working_set)
        lines.extend(line.strip()
                     for line in options["extra-paths"].splitlines())
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

    def update(self):
        pass


def boolean(value):
    return value.lower() in (1, "yes", "true", "on")
