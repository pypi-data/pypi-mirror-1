
from kss.demo.interfaces import IKSSDemoRegistry
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.publisher.interfaces import NotFound
from zope.component import getUtility
from zope.interface import implements
try:
    from Products.Five import BrowserView
    BrowserView         # make pyflakes happy
except ImportError:
     from zope.publisher.browser import BrowserView

class KSSDemoRegistryView(BrowserView):

    def getSortedDemos(self):
        """Get demos"""
        registry = getUtility(IKSSDemoRegistry)
        return registry.getSortedDemos()

    def getDemoGroups(self):
        """Get demos groupped by plugin_namespace, category"""
        demo_groups = []
        prev_plugin_namespace, prev_category = None, None
        group = None
        for demo in self.getSortedDemos():
            plugin_namespace = demo['plugin_namespace']
            category =  demo['category']
            # Set a flag on first rows in group, 
            # since z3 seems not to  handle rpeeat(..).first()
            # These will be used for grouping
            if prev_plugin_namespace != plugin_namespace:
                is_first_plugin_namespace = True
                prev_plugin_namespace = plugin_namespace
            else:
                is_first_plugin_namespace = False
            if prev_category != category:
                is_first_category = True
                prev_category = category
            else:
                is_first_category = False
            # If plugin_namespace or category changed, time to
            # start a new group.
            if is_first_plugin_namespace or is_first_category:
                # Start a new group.
                group = []
                demo_groups.append(dict(
                    plugin_namespace = plugin_namespace,
                    category = category,
                    demos = group,
                    is_first_plugin_namespace = is_first_plugin_namespace,
                    is_first_category = is_first_category,
                    ))
            # In any case append our demo to the group
            group.append(demo)
        return demo_groups

class KSSDemoRegistryAdminView(BrowserView):
    """Things that only admin should do"""
    implements(IBrowserPublisher)

    # Zope3 requires the implementation of
    # IBrowserPublisher, in order for the methods
    # to be traversable.
    #
    # An alternative would be:
    # <browser:pages class="...">
    #   <page name="..." attribute="..." />
    #   <page name="..." attribute="..." />
    # </browser:pages>

    def publishTraverse(self, request, name):
        try:
            return getattr(self, name)
        except AttributeError:
            raise NotFound(self.context, name, request)

    def browserDefault(self, request):
        # make ui the default method
        return self, ('cookSeleniumTests', )

    # --
    # Accessable methods
    # --

    def cookSeleniumTests(self):
        """Cook selenium tests

        The *.html tests from each plugin are produced
        into the file seltest_all.pty in the directory
        of kss.demo.selenium_utils .
        """
        registry = getUtility(IKSSDemoRegistry)
        registry.cookSeleniumTests()
        return "Selenium tests cooked OK. (%i)" % (len(registry.selenium_tests), )
