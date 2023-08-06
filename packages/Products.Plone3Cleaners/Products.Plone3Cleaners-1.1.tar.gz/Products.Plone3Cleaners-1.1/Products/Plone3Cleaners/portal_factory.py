import logging

from Acquisition import aq_inner
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

logger = logging.getLogger('Plone3Helpers')


class FactoryCleaner(BrowserView):
    """Remove portal_factory items from the portal_catalog.

    They should not be there,
    but sometimes life is not fair.
    """

    items_cleaned = 0

    def __call__(self):
        if 'clean' in self.request.form.keys():
            self.clean()
        elif 'kill' in self.request.form.keys():
            self.kill()
        # Display our page template.
        return self.index()

    def clean(self):
        self.items_cleaned = 0
        context = aq_inner(self.context)
        cat = getToolByName(context, 'portal_catalog')
        brains = cat()
        for brain in brains:
            path = brain.getPath()
            if '/portal_factory/' in path:
                logger.info("Removing brain with path %s", path)
                cat.uncatalog_object(path)
                self.items_cleaned += 1

    def kill(self):
        self.items_cleaned = 0
        context = aq_inner(self.context)
        cat = getToolByName(context, 'portal_catalog')
        brains = cat()
        for brain in brains:
            path = brain.getPath()
            try:
                obj = brain.getObject()
            except (AttributeError, KeyError):
                logger.info("Removing brain with path %s", path)
                cat.uncatalog_object(path)
                self.items_cleaned += 1
            except:
                logger.warn("Please investigate non-caught error getting "
                            "object for path %s",
                            path)
