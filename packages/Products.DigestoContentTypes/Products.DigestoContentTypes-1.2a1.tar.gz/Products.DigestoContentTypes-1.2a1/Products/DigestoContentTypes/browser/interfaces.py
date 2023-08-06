# -*- coding: utf-8 -*-

from zope.interface import Interface

class ITypesTools(Interface):
    """A hack for Normativa"""

    def get_vocabulary_for(subfield, instance, req_kind, req_source, include_current):
        """Gets the displaylist for kinds subfield"""

    def get_years():
        """Returns possible years for drop down"""

    def get_areas():
        """Return all area names"""

    def get_area_emails(area):
        """Return all emails of an area"""

    def get_kinds():
        """Return all kinds from utility"""

    def get_normalized_kinds():
        """Returns tuples of normalized, original values of kinds"""


class ISearchTools(Interface):
    """Tools to perform searches"""

    def handle_request(request):
        """Modifies the query in the request for queryCatalog"""

    def search_results(request):
        """Performs a query to the catalog based on the search parameters"""


class IAbbreviationsView(Interface):
    """View for abbreviations management"""


class IDigestoContentTypesCommands(Interface):
    """Commands for KSS in DigestoContentTypes"""
