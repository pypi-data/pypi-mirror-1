# -*- coding: utf-8 -*-
#
# File: RDV_PropositionsEdit.py
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
from Products.rendezvous.browser.RDV_RendezVousUtility import RDV_RendezVousUtility
##/code-section module-header

from zope import interface
from zope import component
from Products.CMFPlone import utils
from Products.Five import BrowserView
from zope.interface import implements
from Products.rendezvous.content.RDV_RendezVous import RDV_RendezVous
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin


class RDV_PropositionsEdit(BrowserView):
    """
    """

    ##code-section class-header_RDV_PropositionsEdit #fill in your manual code here
    NB_COLUMNS = 5
    ##/code-section class-header_RDV_PropositionsEdit

    def getNbColumns(self):
        """Return the number of columns
        """
        propositionsbydates = RDV_RendezVousUtility.getPropositionsByDates(self)
        try:
            uid = self.context.aq_inner.UID()
            nb = self.request.SESSION['rendezvous']['nb_columns'][uid]
        except KeyError:
            nb = self.NB_COLUMNS
        for date, propositions in propositionsbydates.items():
            nb = max(len(propositions), nb)
        return nb

    def incNbColumns(self):
        uid = self.context.aq_inner.UID()
        session_rendezvous = self.request.SESSION.get('rendezvous', {})
        if not 'nb_columns' in session_rendezvous:
            session_rendezvous['nb_columns'] = {}
        session_rendezvous['nb_columns'][uid] = self.getNbColumns() + self.NB_COLUMNS
        self.request.SESSION['rendezvous'] = session_rendezvous

    def getPropositionsByOrderedDates(self):
        return RDV_RendezVousUtility.getPropositionsByOrderedDates(self)

    def saveChanges(self):
        context = self.context.aq_inner
        propositions_by_dates = {}
        for date, propositions in self.request.form.items():
            if date in ('finish', 'extend'):
                continue
            propositions_by_dates[date] = [p for p in propositions if p]
            if not propositions_by_dates[date]:
                propositions_by_dates[date] = ['']
        # save in the session only
        RDV_RendezVousUtility.setPropositionsByDates(self, propositions_by_dates)
        if 'finish' in self.request.form:
            # save to the filesystem
            context.setPropositionsByDates(propositions_by_dates)
            self.request.response.redirect(context.absolute_url())
        elif 'extend' in self.request.form:
            self.incNbColumns()
            self.request.response.redirect(context.absolute_url() + '/@@edit_propositions')



    def __init__(self, context, request):
        super(RDV_PropositionsEdit, self).__init__(context, request)


##code-section module-footer #fill in your manual code here
##/code-section module-footer


