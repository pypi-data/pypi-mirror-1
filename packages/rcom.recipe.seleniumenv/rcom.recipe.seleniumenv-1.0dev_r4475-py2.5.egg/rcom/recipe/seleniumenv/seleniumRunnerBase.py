#!%(executablepath)s

import subprocess
import unittest
import platform
import time
import sys
import os
import signal
from urllib import urlopen
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-s", "--product", dest="product", help="The product to search and run selenium tests. This is defaulted to enpraxis.educommons.") 
parser.add_option("-t", "--test", dest="test", help="The particular test to run. All the test will be run if -t is not present.")
parser.add_option("-i", "--instance", dest="instance", help="The Plone site's name. This is used for the url to test.")
parser.add_option("-o", "--output", dest="html_file", help="The runner can generate an html summary of the execution.")
parser.add_option("-p", "--port", dest="port", default=4444, type="int", help="The port in which wake up the server. Default: 4444.")
parser.add_option("-b", "--browser", dest="browser", default="*firefox", help="The browser to use for the tests that are browser independent. Note: Some tests might still run on a different browser if they have been writen to do that. Defaults to *firefox")
parser.add_option("-f", action="store_true", dest="forcedbrowser", help="Add the -f tag to force all the tests to use the browser desired.")
parser.add_option("-v", action="store_true", dest="verbose", help="Verbose will print on stdout all the output from the selenium RC server.")

(options, args) = parser.parse_args()

# The test will be required until I find a way to get all the paths to add 
# and be able to import all the products
if not options.product:
    parser.error("The product is a required parameter")
if not options.instance:
    parser.error("The instance's name is a required parameter")

# Here we add "all" the products to the path
# TODO: add ALL the installed products to the sys.path, to be able to find test in all of them
product_list = [
            '%(importpath)s']

for product in product_list:
    if options.product in product:
        product = os.path.join(product,options.product.replace(".", os.sep),"tests")
        break

sys.path[0:0] = [
                product,
                '%(clientpath)s']

# We set the parameters to pass to the server and launch it
params = " -singleWindow"
if options.verbose:
    verbose = None
else:
    verbose = open(os.devnull,"w")
if options.port:
    params += " -port " + str(options.port)
if options.forcedbrowser:
    params += " -forcedBrowserModeRestOfLine " + options.browser
server = subprocess.Popen("%(java-cmd)s -jar %(sellocation)s/selenium-server.jar" + params, shell=True, stdout=verbose)
time.sleep(5)

# Now we import the tests and set the required variables to locate the instance and selenium server
package = __import__("seleniumtests")
suite = unittest.TestSuite()
if not options.test:
    test_modules = [module_name for module_name in dir(package) if not module_name.startswith("_")]
else:
    test_modules = [options.test,]

for module_name in test_modules:
    try:
        module = sys.modules["seleniumtests." + module_name]
    except KeyError, e:
        print "Couldn't find the tests script: ", e
        continue
    module.port = options.port
    module.browser = options.browser
    module.url = "http://localhost:%(http-address)s/"
    module.instance = options.instance
    #We add the tests to the suite
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))

# And we run the tests
if options.html_file:
    import HTMLTestRunner
    fp = file(options.html_file, 'wb')
    runner = HTMLTestRunner.HTMLTestRunner(
                stream=fp,
                title='Selenium tests execution summary',
                description='Product tested: ' + options.product
                )
    runner.run(suite)
else:
    unittest.TextTestRunner(verbosity=2).run(suite)

# And we kill the server
print "\nKilling Selenium Server"
print urlopen("http://localhost:"+str(options.port)+"/selenium-server/driver/?cmd=shutDown").read()
if (platform.system() == 'Windows'):
    import win32api
    handle = win32api.OpenProcess(1, 0, server.pid)
    win32api.TerminateProcess(handle, 0)
else:
    os.kill(server.pid,signal.SIGTERM)

try: verbose.close()
except AttributeError, e:pass

