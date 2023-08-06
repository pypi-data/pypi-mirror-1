# -*- coding: utf-8 -*-
#
# File: RDV_RendezVousEdit.py
#
# Copyright (c) 2008 by Ecreall
# Generator: ArchGenXML Version 2.2 (svn)
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Vincent Fretin <vincentfretin@ecreall.com>"""
__docformat__ = 'plaintext'

##code-section module-header #fill in your manual code here
from plone.portlets.interfaces import IPortletRenderer
from plone.app.portlets.portlets import calendar
from plone.portlets.interfaces import IPortletManager
from zope.component import getUtility, getMultiAdapter
from Products.CMFCore.utils import getToolByName
from plone.app.portlets.portlets.calendar import Renderer as CalRenderer
from plone.memoize.compress import xhtml_compress
from Acquisition import aq_inner
from Products.rendezvous.browser.RDV_RendezVousUtility import RDV_RendezVousUtility

class _RDV_Calendar(CalRenderer):
    """overload the calendar for removing events
    """
    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view
        self.__parent__ = view

    def render(self):
        return xhtml_compress(self._template())

    def getDatesForCalendar(self):
        context = aq_inner(self.context)
        year = self.year
        month = self.month
        weeks_ = self.calendar.getWeeksList(month, year)
        selected_dates = self.view.getSelectedDates()
        weeks = []
        for week_ in weeks_:
            week = []
            for daynumber in week_:
                day = {}
                week.append(day)
                day['day'] = daynumber
                if daynumber == 0:
                    continue
                day['is_today'] = self.isToday(daynumber)
                day['date_string'] = '%d-%0.2d-%0.2d' % (year, month, daynumber)
                if day['date_string'] in selected_dates:
                    day['selected'] = True
                else:
                    day['selected'] = False
            weeks.append(week)
        return weeks
##/code-section module-header

from zope import interface
from zope import component
from Products.CMFPlone import utils
from Products.Five import BrowserView
from zope.interface import implements
from Products.rendezvous.content.RDV_RendezVous import RDV_RendezVous
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin


class RDV_RendezVousEdit(BrowserView):
    """
    """

    ##code-section class-header_RDV_RendezVousEdit #fill in your manual code here
    ##/code-section class-header_RDV_RendezVousEdit

    def getSelectedDates(self):
        return RDV_RendezVousUtility.getSelectedDates(self)

    def toggleSelectedDate(self, selected_date):
        return RDV_RendezVousUtility.toggleSelectedDate(self, selected_date)

    def getFormatedDates(self):
        return [self.context.toLocalizedTime(date) for date in sorted(self.getSelectedDates())]

    def __getattr__(self, key):
        try:
            return self.__dict__[key]
        except KeyError:
            return getattr(self.renderer, key)



    def __init__(self, context, request):
        super(RDV_RendezVousEdit, self).__init__(context, request)

        date = self.request.get('rdvdate', None)
        if date:
            self.toggleSelectedDate(date)

        self.renderer = _RDV_Calendar(context, request, self)
        self.portal_catalog = getToolByName(self.context, 'portal_catalog')
        self.renderer.update()


##code-section module-footer #fill in your manual code here
##/code-section module-footer


