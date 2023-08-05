# Copyright (c) 2007 Thomas Lotze
# See also LICENSE.txt

"""zc.buildout recipe to build the mod_python Apache module.
"""

import os
import os.path
import tempfile
import shutil

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
        path-list
        extra-config
    """

    def __init__(self, buildout, name, options):
        super(Recipe, self).__init__(buildout, name, options)
        self.egg = pkg_resources.load_entry_point(
            "zc.recipe.egg", "zc.buildout", "eggs")(buildout, name, options)

        location = options["location"]

        options.setdefault("url", URL)
        options.setdefault("md5sum", MD5SUM)

        # Collect some options for buildout book-keeping.
        httpd = options.get("httpd", "httpd")
        apxs_path = buildout[httpd]["apxs-path"]

        python = options.get("python", buildout["buildout"]["python"])
        executable = buildout[python]["executable"]

        options["extra-options"] = (
            "--with-apxs=%s --with-python=%s " % (apxs_path, executable) +
            options.get("extra-options", ""))

        # We need to re-install after httpd was built differently.
        options["httpd-sig"] = (buildout[httpd]["md5sum"] +
                                buildout[httpd]["extra-options"])

        # Export some options.
        options["so-path"] = os.path.join(location, "mod_python.so")
        options["lib-dir"] = os.path.join(location, "lib")

        num_eggs = sum(1 for spec in options.get("eggs", "").splitlines()
                       if spec.strip())

        options["path-list"] = repr(
            [os.path.join(location, str(i)) for i in xrange(num_eggs)] +
            options.get("extra-paths", "").split() +
            [options["lib-dir"]])

        options["extra-config"] = (
            "LoadModule python_module %s\n" % options["so-path"] +
            'PythonPath "%s + sys.path"' % options["path-list"])

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

        # Link to the packages in the eggs from directories in lib-dir. We
        # couldn't export the real egg locations in the constructor as we
        # didn't know them then. We also don't just link the eggs themselves
        # as the buildout may be run from inside a develop egg which would
        # result in a symlink loop.
        eggs, ws = self.egg.working_set(())
        for i, spec in enumerate(eggs):
            dest = os.path.join(options["location"], str(i))
            os.mkdir(dest)
            path = ws.find(pkg_resources.Requirement.parse(spec)).location
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if (os.path.isdir(item_path) and
                    "__init__.py" in os.listdir(item_path)):
                    os.symlink(item_path, os.path.join(dest, item))

        return parts
