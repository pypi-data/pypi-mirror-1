# Copyright (c) 2008-2009 Thomas Lotze
# See also LICENSE.txt

import ConfigParser
import os
import os.path
import shutil
import sys
import tempfile
import zc.buildout

import pkg_resources


config_file = pkg_resources.resource_stream(__name__, "defaults.cfg")
config = ConfigParser.ConfigParser()
config.readfp(config_file)


class InstallPyGTK(object):
    """A zc.buildout recipe for installing pygtk & friends.

    Assumes the cairo, gobject and gtk+ C libraries to be installed
    system-wide.

    """

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options

        for key, value in config.defaults().items():
            options.setdefault(key, value)

        if options['pygtk-url'] and not options['pygobject-url']:
            raise zc.buildout.UserError(
                'Cannot build pygtk without pygobject.')

        self.location = options.setdefault("location", os.path.join(
            buildout["buildout"]["parts-directory"], name))

        py_version = sys.version[:3]
        path = os.path.join(
            self.location, "lib", "python%s" % py_version, "site-packages")
        # XXX evaluate pygtk.pth
        if options['pygobject-url']:
            options['path'] = '\n'.join([path, os.path.join(path, 'gtk-2.0')])
        else:
            options['path'] = path

    def install(self):
        # set up things
        if not os.path.isdir(self.location):
            os.mkdir(self.location)
        cmmi = self.egg = pkg_resources.load_entry_point(
            "gocept.cmmi", "zc.buildout", "default")

        # put the target python in front of the cmmi recipes' binary path
        # (the projects to be built don't have a --with-python option)
        python_path = tempfile.mkdtemp()
        os.symlink(sys.executable, os.path.join(python_path, "python"))
        path = os.environ["PATH"]
        pkg_config_path = os.path.join(self.location, "lib", "pkgconfig")
        extra_vars = """PATH=%(python_path)s:%(path)s
                        PKG_CONFIG_PATH=%(pkg_config_path)s
                        """ % dict(python_path=python_path,
                                   path=path,
                                   pkg_config_path=pkg_config_path)

        # build python bindings
        for project in ("pycairo", "pygobject", "pygtk"):
            url = self.options[project + "-url"]
            if not url:
                continue
            options = self.options.copy()
            options.update({"url": url,
                            "md5sum": self.options[project + "-md5sum"],
                            "extra-vars": extra_vars})
            cmmi(self.buildout, self.name, options).install()

        # clean up
        shutil.rmtree(python_path)

        return [self.location]

    def update(self):
        pass

