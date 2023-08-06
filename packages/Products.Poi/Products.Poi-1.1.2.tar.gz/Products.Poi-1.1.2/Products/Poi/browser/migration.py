from StringIO import StringIO
from Acquisition import aq_inner
from zope import interface
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
import logging
log = logging.getLogger("Poi")


class IMigration(interface.Interface):

    def fix_btrees():
        """The order of inheritance of PoiPscTracker was broken at
        some point.  We need to fix BTreeFolders without `self._tree`.
        """

    def fix_descriptions(context):
        """Fix issue Descriptions.

        In revision 53855 a change was made that caused the Description
        field of issues that were first strings to now possibly turn into
        unicode.  That fixed this issue:
        http://plone.org/products/poi/issues/135

        But as stated at the bottom of that issue, this can give a
        UnicodeEncodeError when changing the issue or adding a response to
        it.  The Description string that is in the catalog brain is
        compared to the unicode Description from the object and this fails
        when the brain Description has non-ascii characters.

        A good workaround is to clear and rebuild the catalog.  But
        running this upgrade step also fixes it.
        """


class Migration(BrowserView):

    def __call__(self):
        migration_id = self.request.get('migration_id')
        if migration_id in IMigration.names():
            message = getattr(self, migration_id)()
            context = aq_inner(self.context)
            ptool = getToolByName(self.context, 'plone_utils')
            ptool.addPortalMessage("Ran migration %s." % migration_id)
            if message:
                ptool.addPortalMessage(message)
        return self.index()

    def available_migrations(self):
        return IMigration.names()        

    def fix_btrees(self):
        out = StringIO()
        context = aq_inner(self.context)
        catalog = getToolByName(self.context, 'portal_catalog')
        for b in catalog(portal_type='PoiPscTracker'):
            tracker = b.getObject()
            if tracker._tree is None:
                tracker._initBTrees()
                out.write('Fixed BTreeFolder at %s\n' %
                          '/'.join(tracker.getPhysicalPath()))
        return out.getvalue()

    def fix_descriptions(self):
        context = aq_inner(self.context)
        log.info("Start fixing issue descriptions.")
        catalog = getToolByName(context, 'portal_catalog')
        brains = catalog.searchResults(portal_type='PoiIssue')
        log.info("Found %s PoiIssues.", len(brains))
        fixed = 0
        for brain in brains:
            if isinstance(brain.Description, str):
                issue = brain.getObject()
                if isinstance(issue.Description(), unicode):
                    log.debug("Un/reindexing PoiIssue %s", brain.getURL())
                    # This is the central point really: directly
                    # reindexing this issue can fail if the description
                    # has non-ascii characters.  So we unindex it first.
                    catalog.unindexObject(issue)
                    catalog.reindexObject(issue)
                    fixed += 1
                    if fixed % 100 == 0:
                        log.info("Fixed %s PoiIssues so far; still busy...",
                                 fixed)
        msg = "Fix completed.  %s PoiIssues needed fixing." % fixed
        log.info(msg)
        return msg
