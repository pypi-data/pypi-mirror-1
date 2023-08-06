from zope.interface import implements
from zope.component import (
    adapter, 
    getSiteManager,
    )
from interfaces import (
    IKSSDemoRegistry,
    IKSSSeleniumTestRegistry,
    IKSSDemoResource,
    IKSSSeleniumTestResource,
    IKSSDemoRegistrationEvent,
    IKSSDemoRegistryEvent,
    )
from zope.component.interfaces import (
    IUtilityRegistration,
    IRegistered,
    IUnregistered,
    )
import sys, os, re, textwrap
from elementtree import HTMLTreeBuilder
from string import Template
import kss.demo.selenium_utils
# shut the mouth of pyflakes
kss.demo.selenium_utils

# --
# Registry implementation for use with Zope
# --

def getRootDirOfModule(module_name):
    return os.path.dirname(sys.modules[module_name].__file__)

def getRootDirOfClass(cls):
    return getRootDirOfModule(cls.__module__)

def getRootDirOfInstance(obj):
    return getRootDirOfClass(obj.__class__)

# Create a mesh of provided interfaces
# This is needed, because an utility must have a single interface.
class IRegistry(IKSSDemoRegistry, IKSSSeleniumTestRegistry):
    pass

class KSSDemoRegistry(object):
    """KSS demo registry.
    """
    implements(IRegistry)

    def __init__(self):
        # We will set up my handlers to get notified of new plugins
        # (works via redispatching by events.py)
        site = getSiteManager()
        # registry for demos
        self.demos_dict = {}
        self.demos = []
        self.demos_are_sorted = False
        site.registerHandler(self.registerDemosFromPlugin)
        site.registerHandler(self.unregisterDemosFromPlugin)
        site.registerHandler(self.registerEarlierDemos)
        # registry for selenium tests
        self.selenium_tests = []
        site.registerHandler(self.registerSeleniumTestsFromPlugin)
        site.registerHandler(self.unregisterSeleniumTestsFromPlugin)
        # ... the rest of setup will be done from registerEarlierDemos

    @adapter(IKSSDemoRegistry, IUtilityRegistration, IRegistered, IKSSDemoRegistryEvent)
    def registerEarlierDemos(self, registry, registration=None, event=None, new_event=None):
        """Make sure that the resources registered earlier, are added
         (so this is a listener to the registration of myself
         which is needed because CA is not ready at time of the __init__)
        """
        if registry != self:
            # The utility only register on itself.
            return
        site = getSiteManager()
        for name, plugin in site.getUtilitiesFor(IKSSDemoResource):
            for demo in plugin.demos:
                self.registerDemo(demo)

    @adapter(IKSSDemoResource, IUtilityRegistration, IRegistered, IKSSDemoRegistrationEvent)
    def registerDemosFromPlugin(self, plugin, registration=None, event=None, new_event=None):
        """Add a demo collection to the registry.
        """
        for demo in plugin.demos:
            self.registerDemo(demo)

    @adapter(IKSSDemoResource, IUtilityRegistration, IUnregistered, IKSSDemoRegistrationEvent)
    def unregisterDemosFromPlugin(self, plugin, registration=None, event=None, new_event=None):
        """Remove a demo collection from the registry.
        """
        for demo in plugin.demos:
            self.unregisterDemo(demo)

    def registerDemo(self, demo):
        """Register a demo

        It has the attributes specified in IKSSDemo:

        plugin_namespace - string with the name of the plugin.
                           Or: "" when it is the core part.

        category         - text that will appear as the title of the
                           category. "" if out of category.

        demo_page        - (relative) url of the demo page. This should
                           traverse on ISimpleContent.

        title            - Title of the demo. This also identifies it
                           for removal.
        """
        key = demo.plugin_namespace, demo.category, demo.page_url
        if key in self.demos:
            raise Exception, 'The demo for %s has already been registered. Cannot add.' % (key, )
        self.demos_dict[key] = demo
        self.demos.append(demo)
        self.demos_are_sorted = False

    def unregisterDemo(self, demo):
        """Unregister the given demo."""
        key = demo.plugin_namespace, demo.category, demo.demo_page
        try:
            value = self.demos_dict[key]
        except KeyError:
            raise Exception, 'The demo for %s is yet unregistered. Cannot remove.' % (key, )
        del self.demos_dict[key]
        self.demos.remove(value)

    def getSortedDemos(self):
        """Get the (sorted) list of demos"""
        if not self.demos_are_sorted:
            self.demos.sort(key=lambda demo: (
                demo.plugin_namespace,
                demo.category,
                ))
            self.demos_are_sorted = True
        return list(self.demos)

    # --
    # Selenium tests
    # --

    @staticmethod
    def _getSeleniumTestsFromPlugin(plugin):
        test_filenames = []
        root_dir = getRootDirOfInstance(plugin)
        for selenium_test_directory in plugin.selenium_tests:
            tests_root_dir = os.path.join(root_dir, selenium_test_directory.test_directory)
            for test_filename in os.listdir(tests_root_dir):
                if test_filename.lower().endswith('.html') or \
                        test_filename.endswith('.htm'):
                    test_filenames.append(os.path.join(tests_root_dir, test_filename))
        return test_filenames

    @adapter(IKSSSeleniumTestResource, IUtilityRegistration, IRegistered, IKSSDemoRegistrationEvent)
    def registerSeleniumTestsFromPlugin(self, plugin, registration=None, event=None, new_event=None):
        """Add a demo collection to the registry.
        """
        for test_filename in self._getSeleniumTestsFromPlugin(plugin):
            self.registerSeleniumTestFile(test_filename)

    @adapter(IKSSSeleniumTestResource, IUtilityRegistration, IUnregistered, IKSSDemoRegistrationEvent)
    def unregisterSeleniumTestsFromPlugin(self, plugin, registration=None, event=None, new_event=None):
        """Remove a demo collection from the registry.
        """
        for test_filename in self._getSeleniumTestsFromPlugin(plugin):
            self.registerSeleniumTestFile(test_filename)

    def registerSeleniumTestFile(self, test_filename):
        """Register a selenium test by absolute filename
        """
        if test_filename in self.selenium_tests:
            raise Exception, 'The selenium test for %s has already been registered. Cannot add.' % (test_filename, )
        self.selenium_tests.append(test_filename)

    def unregisterSeleniumTestFile(self, test_filename):
        """Unregister the given selenium test."""
        try:
            del self.selenium_tests[test_filename]
        except KeyError:
            raise Exception, 'The selenium test for %s is yet unregistered. Cannot remove.' % (test_filename, )

    template = Template(textwrap.dedent('''\
            from seleniumtestcase import SeleniumTestCase
            import unittest, time

            class seltest_$testname(SeleniumTestCase):

            $tests

            def test_suite():
                return unittest.makeSuite(seltest_$testname)

            if __name__ == "__main__":
                unittest.main()
            '''))

    variable_regexp = re.compile('\$\{(?P<varname>\w*)\}')
    @classmethod
    def formatcommand(cls, command, *args):
        if not command:
            return '' # Change this to raise an exception?

        arguments = []
        for arg in args:
            if not arg:
                continue
            matched = cls.variable_regexp.match(arg)
            if matched is None:
                arguments.append('"%s"'%arg)
            else:
                arguments.append("self.getVar('%s')"%matched.group('varname'))
        return 'self.%s(%s)' % (command, ', '.join(arguments))

    def cookSeleniumTests(self):
        """Cook selenium tests

        The *.html tests from each plugin are produced
        into the file seltest_all.pty in the directory
        of kss.demo.selenium_utils .
        """
        # Try to open the file for writing.
        output_dir =  getRootDirOfModule('kss.demo.selenium_utils')
        output_filename = os.path.join(output_dir, 'seltest_all.py')
        try:
            f = open(output_filename, 'wb')
        except IOError, exc:
            raise IOError, ('Cannot open file "%s" for writing. '
                            'Make sure zope process has write access in directory. '
                            '["%s"]') \
                            % (output_filename, exc)

        htmlparser = HTMLTreeBuilder.TreeBuilder()
        tests = []
        for filename in self.selenium_tests:
            tree = HTMLTreeBuilder.parse(filename)
            root = tree.getroot()

            try:
                testname = root.find('.//title').text
            except AttributeError:
                continue
            commands = []
            for row in root.findall('.//tbody/tr'):
                commands.append(self.formatcommand(*[td.text for td in row.findall('td')]))

            testfilename = 'seltest_%s.py' % testname
            testbody='    def test_%s(self):\n'%testname+' '*8+'\n        '.join(commands)+'\n'
            tests.append(testbody)

        f.write(self.template.substitute(dict(
            testname=testname,
            tests='\n'.join(tests),
            )))
        f.close()
