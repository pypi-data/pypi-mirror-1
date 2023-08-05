import os, shutil, tempfile, urllib2, urlparse
import setuptools.archive_util
import pkg_resources
import ConfigParser
import hexagonit.recipe.download
import stat

class Recipe(hexagonit.recipe.download.Recipe):
    def __init__(self, buildout, name, options):
        # this copies configuration set in defaults.cfg to our options namespace
        config_file = pkg_resources.resource_stream(__name__, "defaults.cfg")
        config = ConfigParser.ConfigParser()
        config.readfp(config_file)
        for key, value in config.items("seleniumrc"):
            options.setdefault(key, value)

        super(Recipe, self).__init__(buildout, name, options)

        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'],
            self.name)
        self.url = options['url']

    def calculate_base(self, extract_dir):
        selrcdir = os.listdir(extract_dir)[0]
        version = selrcdir.split('-')[-1]
        return os.path.join(extract_dir, selrcdir, 'selenium-server-%s' % version)

    def install_wrapper(self):
        ctl_path = os.path.join(self.buildout["buildout"]["bin-directory"],
                                self.name)
        open(ctl_path, "w").write(pkg_resources.resource_string(__name__, "seleniumrc_ctl.in") % self.options)
        os.chmod(ctl_path, (os.stat(ctl_path).st_mode |
                            stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))
                                        
    def install(self):
        parts = super(Recipe, self).install()
        self.install_wrapper()
        return parts
        
    def update(self):
        parts = super(Recipe, self).update()
        self.install_wrapper()
        return parts