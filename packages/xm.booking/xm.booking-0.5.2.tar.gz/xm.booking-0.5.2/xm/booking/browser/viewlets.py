from Acquisition import aq_inner
from plone.app.layout.viewlets import ViewletBase
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from zope.interface import Interface
from zope.interface import implements


class BookingFormInterface(Interface):

    def allowed():
        """Is the user allowed to add a booking here?
        """
        pass


class Bookings(ViewletBase):

    render = ViewPageTemplateFile("bookingtable.pt")


class BookingForm(ViewletBase):
    implements(BookingFormInterface)

    def allowed(self):
        """Is the user allowed to add a booking here?
        """
        context = aq_inner(self.context)
        mem = getToolByName(context, 'portal_membership')
        return mem.checkPermission('eXtremeManagement: Add Booking', context)

    render = ViewPageTemplateFile("add.pt")
