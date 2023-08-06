import logging

from Acquisition import aq_inner, aq_base
from Products.Five import BrowserView
from Products.Five.site.browser import LocalSiteView
from zope.app.component.interfaces import ISite
from zope.app.component.hooks import setSite
from zope.component import getSiteManager
from zope.component import queryMultiAdapter
from zope.interface import Interface, providedBy
import Products.Five.component

HOOK_NAME = '__local_site_hook__'
logger = logging.getLogger('ZestHelpers')


class FindLocalSites(BrowserView):
    """Offer to turn old-style sites into new-style local sites.

    Needed during migration from Plone 2.5 to Plone 3.
    """
    found_sites = []

    def __call__(self):
        if 'submit' in self.request.form.keys():
            # Update found_sites
            self.found_sites =[]
            self.find()
        # Display our page template.
        return self.index()

    def find(self):
        """Find sites with local site hooks and put them in self.found_sites.
        """
        context = aq_inner(self.context)

        def check_site(obj, path):
            """Is the object a site?

            We define this function inline so we have easy access to
            the found_sites variable.
            """
            if ISite.providedBy(obj):
                # We could report these too, but if they do not have
                # the local site hook (e.g. when this is a Plone Site)
                # then nothing needs to happen.
                logger.info("ISite provided by %s", obj.absolute_url())
            if hasattr(aq_base(obj), HOOK_NAME):
                logger.info("object %s has %s", obj.absolute_url(), HOOK_NAME)
                hook = getattr(obj, HOOK_NAME)
                if hook.__class__ == Products.Five.component.LocalSiteHook:
                    # new style
                    pass
                else:
                    # broken old style
                    self.found_sites.append(obj)
                    logger.info("object %s has old broken local site hook.",
                                obj.absolute_url())

        logger.info("Checking for local sites...")
        context.ZopeFindAndApply(context, apply_func=check_site,
                                 search_sub=True)
        logger.info("Ready checking for local sites.")


class SiteFixer(LocalSiteView):
    """Offer to migrate old Plone 2.5 local site to new Plone 3 local site.

    When it is already a new site, no options are shown.

    Note that when this is an old local site it will have a broken
    __local_site_hook__ so you will likely get an error during
    traversal.  Just ignore it (or continue in PDBDebugMode) as you
    are about to fix this.  Also note that clicking on the migrate
    button will trigger that same error, which should again be
    ignored.  After that it should be fine.
    """

    def isOldSite(self):
        """Is this an old site?

        Change compared to original Five implementation: also return
        True when we have a local site hook.  This is because that
        hook is what is causing us problems.  And the original checks
        do not fit the new code where we have removed five:localsite
        and other stuff from zcml or python code.
        """
        if not self.isSite():
            return False
        from Products.Five.site.interfaces import IFiveSiteManager
        if IFiveSiteManager.providedBy(getSiteManager()):
            return True
        obj = aq_base(self.context)
        if hasattr(obj, HOOK_NAME):
            hook = getattr(obj, HOOK_NAME)
            if hook.__class__ == Products.Five.component.LocalSiteHook:
                # new style
                return False
            else:
                # broken old style
                return True
        return False

    def migrateToFive15(self):
        """Migrate to new-style site.

        Change compared to default Five: do not fail when the context
        has no utilities map, which can easily happen if no utilities
        have been registered locally.
        """
        context = aq_inner(self.context)
        if hasattr(context, 'utilities'):
            all_utilities = context.utilities.objectItems()
        else:
            all_utilities = []

        self.unmakeSite()
        if hasattr(context, 'utilities'):
            context.manage_delObjects(['utilities'])
        components_view = queryMultiAdapter((context, self.request),
                                            Interface, 'components.html')
        components_view.makeSite()
        setSite(context)

        site_manager = getSiteManager()
        for id, utility in all_utilities:
            info = id.split('-')
            if len(info) == 1:
                name = ''
            else:
                name = info[1]
            interface_name = info[0]

            for iface in providedBy(utility):
                if iface.getName() == interface_name:
                    site_manager.registerUtility(utility, iface, name=name)

        return "Migration done!"
