import os, shutil, glob
import pkg_resources
import ConfigParser
import hexagonit.recipe.download
import zc.recipe.egg
import stat

class Recipe:
    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.options = options
        self.name = name
        # this copies configuration set in defaults.cfg to our options namespace
        config_file = pkg_resources.resource_stream(__name__, "defaults.cfg")
        config = ConfigParser.ConfigParser()
        config.readfp(config_file)
        #Default options parsing
        for key, value in config.items("seleniumenv"):
            options.setdefault(key, value)
        #Selenium url parsing
        if options['seleniumversion'] == "nightlyBuild":
            selurl = 'http://release.openqa.org/cgi-bin/selenium-remote-control-redirect.zip'
        else:
            selurl = 'http://release.seleniumhq.org/selenium-remote-control/%s/selenium-remote-control-%s-dist.zip' % (options['seleniumversion'],options['seleniumversion'])
            self.selopt = {'url':selurl,
                       'destination':os.path.join(buildout['buildout']['parts-directory'],"seleniumrc"),
                        'strip-top-level-dir':'true',
                        'ignore-existing':'true'
                      } 

    def install_runner(self):
        #Setting the locations that the runner will use
        self.options['executablepath'] = self.buildout['buildout']['executable']
        reqs, ws = zc.recipe.egg.Eggs(self.buildout, self.name, self.options).working_set()
        self.options['importpath']= "',\n\t\t'".join(ws.entries)
        self.options['clientpath'] = glob.glob(os.path.join(self.buildout['buildout']['parts-directory'], "seleniumrc","selenium-python-client*"))[0]
        self.options['sellocation'] = glob.glob( os.path.join(
                                                            self.buildout['buildout']['parts-directory'],
                                                            "seleniumrc",
                                                            "selenium-server*"))[0]
        self.options['http-address'] = self.buildout['instance']['http-address']
        # And now passing the path to the bin directory
        runner_path = os.path.join(self.buildout["buildout"]["bin-directory"], "seleniumRunner")
        open(runner_path, "w").write(pkg_resources.resource_string(__name__, "seleniumRunnerBase.py") % self.options)
        os.chmod(runner_path, (os.stat(runner_path).st_mode |
                            stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))
        # Moving the HTMLTestRunner to the client's folder doesn't seem like the best
        # to do, but I can't find a good place to put it to be able to import later
        shutil.copy(
                pkg_resources.resource_filename(__name__, "HTMLTestRunner.py"),
                self.options['clientpath'])


    def install(self):
        # We download all the parts
        parts = hexagonit.recipe.download.Recipe(self.buildout, "seleniumrc",
                                                 self.selopt).install()
        # Installs the script to launch selenium server
        self.install_runner()
        return parts
        
    def update(self):
       pass 
