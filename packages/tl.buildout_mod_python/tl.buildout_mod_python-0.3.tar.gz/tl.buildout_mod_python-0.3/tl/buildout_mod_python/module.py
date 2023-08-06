# Copyright (c) 2007 Thomas Lotze
# See also LICENSE.txt

"""zc.buildout recipe to build the mod_python Apache module.
"""

import os
import os.path
import tempfile
import shutil
import subprocess
import md5 # deprecated in 2.5, but hashlib isn't in 2.4 yet

import pkg_resources

import gocept.cmmi


URL = "http://www.apache.org/dist/httpd/modpython/mod_python-3.3.1.tgz"
MD5SUM = "a3b0150176b726bd2833dac3a7837dc5"


class Recipe(gocept.cmmi.Recipe):
    """zc.buildout recipe to build the mod_python Apache module.

    Configuration options:
        url
        md5sum
        extra-options

        httpd
        python

        eggs
        find-links
        index
        extra-paths

        config-parts

    Exported options:
        so-path
        lib-dir
        path-file
        extra-env
        extra-config
    """

    def __init__(self, buildout, name, options):
        super(Recipe, self).__init__(buildout, name, options)

        location = options["location"]

        options.setdefault("url", URL)
        options.setdefault("md5sum", MD5SUM)

        # Create the egg recipe instance now to let it initialize the options.
        self.egg = pkg_resources.load_entry_point(
            "zc.recipe.egg", "zc.buildout", "eggs")(buildout, name, options)

        # Collect some options for buildout book-keeping.
        httpd = options.get("httpd", "httpd")
        apxs_path = buildout[httpd]["apxs-path"]

        python = options.get("python", buildout["buildout"]["python"])
        self.executable = buildout[python]["executable"]

        options["extra-options"] = (
            "--with-apxs=%s --with-python=%s %s" %
            (apxs_path, self.executable, options.get("extra-options", "")))

        # We need to re-install after httpd or python were built differently.
        checksum = md5.new()
        checksum.update(repr(sorted(buildout[httpd].values())))
        checksum.update(repr(sorted(buildout[python].values())))
        options["__dependencies-sig__"] = checksum.hexdigest()

        # Export some options.
        options["so-path"] = os.path.join(location, "mod_python.so")
        options["lib-dir"] = os.path.join(location, "lib")
        options["path-file"] = os.path.join(location, "paths")

        options["extra-env"] = ("PATH=%s:$PATH" % location)

        options["extra-config"] = """\
LoadModule python_module %(so-path)s
PythonPath "open('%(path-file)s').read().splitlines() + sys.path"
""" % options

    def install(self):
        options = self.options

        install_dir = tempfile.mkdtemp("buildout-install-" + self.name)
        options["extra-vars"] = ('DESTDIR="%s"\n' % install_dir +
                                 options.get("extra-vars", ""))

        # We need to re-install after httpd was built differently.
        parts = super(Recipe, self).install()

        # Put the goodies in a sane place.
        for dirpath, dirnames, filenames in os.walk(install_dir):
            if "mod_python.so" in filenames:
                shutil.move(os.path.join(dirpath, "mod_python.so"),
                            options["so-path"])
            if "mod_python" in dirnames:
                shutil.move(dirpath, options["lib-dir"])

        shutil.rmtree(install_dir)

        # Link the Python executable used for compiling to a location where it
        # may be called "python". This location will be put on http'd PATH so
        # that executable actually gets used. Sometimes, mod_python behaves
        # suspiciously as if its authors had been smoking something illegal.
        os.symlink(self.executable,
                   os.path.join(options["location"], "python"))

        # Make the mod_python package available to the Python installation.
        self.install_module()

        # Collect module search paths.
        self.write_path_file()

        return parts

    def update(self):
        self.install_module()
        self.write_path_file()

    def install_module(self):
        out = subprocess.Popen(
            [self.executable, "-c",
             "import sys; print sys.version; print sys.prefix"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
            ).communicate()[0]

        version = out[:3]
        prefix = out.splitlines()[-1].strip()

        pth = open(os.path.join(prefix, "lib", "python" + version,
                                "site-packages", "mod_python.pth"), "w")
        pth.write(self.options["lib-dir"])
        pth.close()

    def write_path_file(self):
        options = self.options

        path_file = open(options["path-file"], "w")

        if options.get("eggs"):
            ignored, working_set = self.egg.working_set(())
            for spec in working_set:
                path_file.write(spec.location + "\n")

        for line in options.get("extra-paths", "").splitlines():
            path_file.write(os.path.abspath(line.strip()) + "\n")

        path_file.close()
