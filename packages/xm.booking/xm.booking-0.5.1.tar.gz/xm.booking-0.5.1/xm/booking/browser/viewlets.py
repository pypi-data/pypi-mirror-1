from Acquisition import aq_inner
from plone.app.layout.viewlets import ViewletBase
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class Bookings(ViewletBase):

    render = ViewPageTemplateFile("bookingtable.pt")


class BookingForm(ViewletBase):

    def allowed(self):
        context = aq_inner(self.context)
        mem = getToolByName(context, 'portal_membership')
        return mem.checkPermission('eXtremeManagement: Add Booking', context)

    render = ViewPageTemplateFile("add.pt")
