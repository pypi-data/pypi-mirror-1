from zope.interface import implements
from Acquisition import aq_inner

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.statusmessages.interfaces import IStatusMessage

from Products.PressRoom.interfaces import IPressRoom
from Products.PressRoom import HAS_PLONE30

class PressRoom(BrowserView):
    """Browser view for the Press Room CT"""

    implements(IPressRoom)

    def getContacts(self):
        """Return  a list of Press Contacts for this Press Room only if they should be shown
        """
        if not self.context.getShow_contacts():
            return ()
        else:
            path = '/'.join(self.context.getPhysicalPath())
            return self.context.portal_catalog.searchResults(meta_type = 'PressContact',
                                                             review_state='published',
                                                             path=path,
                                                             sort_on='getObjPositionInParent',
                                                             )

    def canAddPressContacts(self):
        """Returns True if the current user has permission to add Press Contacts"""
        membership_tool = getToolByName(self.context, 'portal_membership')
        return membership_tool.checkPermission('PressRoom: Add portal press rooms', self.context)

    def getReleases(self):
        """Return  a list of Press Releases for this Press Room only if they should be shown
        """
        if not self.context.getShow_releases():
            return ()
        else:
            path = '/'.join(self.context.getPhysicalPath())
            return self.context.portal_catalog.searchResults(meta_type = 'PressRelease',
                                                             review_state='published',
                                                             sort_order='reverse',
                                                             path=path,
                                                             sort_on='getReleaseDate',
                                                             )

    def canAddPressReleases(self):
        """Returns True if the current user has permission to add Press Releases"""
        membership_tool = getToolByName(self.context, 'portal_membership')
        return membership_tool.checkPermission('Add_Portal_Content', self.context)

    def getClips(self):
        """Return  a list of Press Clips for this Press Room only if they should be shown
        """
        if not self.context.getShow_clips():
            return ()
        else:
            path = '/'.join(self.context.getPhysicalPath())
            return self.context.portal_catalog.searchResults(meta_type = 'PressClip',
                                                             review_state='published',
                                                             sort_order='reverse',
                                                             path=path,
                                                             sort_on='getStorydate',
                                                             )

    def canAddPressClips(self):
        """Returns True if the current user has permission to add Press Clips"""
        membership_tool = getToolByName(self.context, 'portal_membership')
        return membership_tool.checkPermission('Add_Portal_Content', self.context)

    def showTwoStatePrivateWarning(self):
        """Returns True if we're in Plone 3.0, the press room's supporting folders are private,
           and the current user is someone who can do something about it."""
        context = aq_inner(self.context)
        if not HAS_PLONE30:
            return False
        else:
            membership_tool = getToolByName(self.context, 'portal_membership')
            if not membership_tool.checkPermission('Review portal content', self.context):
                return False
            else:
                workflow_tool   = getToolByName(self.context, 'portal_workflow')
                for fn in ('press-releases', 'press-clips', 'press-contacts'):
                    folder = getattr(context, fn, None)
                    if folder is None:
                        return False
                    if workflow_tool.getInfoFor(folder, 'review_state') != 'private':
                        return False

        return True

    def publishPressRoomInfrastructure(self):
        """Publish the 3 content folders (clips, releases, contacts) and the Collections
        that are their home folders.  If the Press Room is unpublished, publish it too"""
        # this is usually relevant to only Plone 3.0, but is there any reason to exclude 2.5 use
        # at this point?

        # I decided to not make showTwoStatePrivateWarning a dependency at this level to allow
        # people who published one of the folders manually before realizing the issue.
        # That way, they can call this to fix the reset

        workflow_tool = getToolByName(self.context, 'portal_workflow')
        context = aq_inner(self.context)
        infrastructure = {'press-releases':'all-press-releases',
                          'press-clips':'all-press-clips',
                          'press-contacts':'press-contacts',
                          }

        for fn in infrastructure.keys():
            folder = getattr(context, fn, None)
            if folder:
                if workflow_tool.getInfoFor(folder, 'review_state') == 'private':
                    workflow_tool.doActionFor(folder, 'publish')
                sf = getattr(folder, infrastructure[fn], None)
                if sf and workflow_tool.getInfoFor(sf, 'review_state') == 'private':
                    workflow_tool.doActionFor(sf, 'publish')
                    
        # if the Press Room itself is unpublished, take care of it too -- note
        # we need to be clear that this is part of the effect
        if workflow_tool.getInfoFor(context, 'review_state') == 'private':
            workflow_tool.doActionFor(context, 'publish')
            IStatusMessage(self.request).addStatusMessage(_("Press Room published"),
                                                          type="info")

        IStatusMessage(self.request).addStatusMessage(_("Press Room infrastructure published"),
                                              type="info")

        self.request.response.redirect(context.absolute_url())
