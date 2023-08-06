# -*- coding: utf-8 -*-

from zope.component import getUtility
from zope.interface import implements

from Products.DigestoContentTypes import DigestoContentTypesMessageFactory as _
from Products.DigestoContentTypes.utilities.interfaces import INormativaTypes
from Products.Five.browser import BrowserView

from interfaces import ISearchTools
from Products.CMFCore.utils import getToolByName
from DateTime.DateTime import DateTime

class SearchTools(BrowserView):
    implements(ISearchTools)


    def search_results(self, request):

        if not request.get('SearchableText','') and\
           not request.get('getKind','') and\
           not request.get('getArea','') and\
           not request.get('getNumber','') and\
           not request.get('getDate','') and\
           not request.get('getSource',''):
            return []

        portal_catalog = getToolByName(self.context, 'portal_catalog')
        query = {'portal_type' : 'Normativa',
                 'SearchableText' : request.get('SearchableText',''),
                 'getKind' : request.get('getKind',''),
                 'getArea' : request.get('getArea',''),
                 'getSource' : request.get('getSource','')}

        def fixyy(year):
            #caso YY
            if year >=0 and year < 20:
                return(2000 + year)                
            elif year >=20 and year <= 99:
                return(1900 + year)
            else:
                return year

        # Search by year
        date = request.get('getDate','')
        if date:
            try:
                date = fixyy(int(date))
                query['getDate'] = {'query':[DateTime(str(date)+'/01/01'), DateTime(str(date)+'/12/31')], 'range':'minmax'}
            except:
                query['getDate'] = ''


        # Search by number in SearchableText
        stext = request.get('SearchableText','')
        if stext:
            try:
                words = stext.split(" ")
                words = [word for word in words if word]
                if len(words) == 1:
                    #caso 123/2008 o 123-2008
                    num_year = words[0].split('/')
                    if len(num_year) != 2:
                        num_year = words[0].split('-')

                    if len(num_year) == 2:
                        num = int(num_year[0])
                        year = int(num_year[1])

                        year = fixyy(year)

                        query['getDate'] = {'query':[DateTime(str(year)+'/01/01'), DateTime(str(year)+'/12/31')], 'range':'minmax'}
                        query['getNumber'] = num
                        query['SearchableText'] = ''

                elif len(words) == 2:
                    # Case Law 123/2008 or Law 123-2008
                    nt = getUtility( INormativaTypes )
                    normalized_types = nt.get_types()
                    normalized_word = words[0]
                    if normalized_word in normalized_types:
                        num_year = words[1].split('/')
                        if len(num_year) != 2:
                            num_year = words[1].split('-')

                        if len(num_year) == 2:
                            num = int(num_year[0])
                            year = int(num_year[1])

                            year = fixyy(year)

                            query['getDate'] = {'query':[DateTime(str(year)+'/01/01'), DateTime(str(year)+'/12/31')], 'range':'minmax'}
                            query['getNumber'] = num
                            query['getKind'] = normalized_word
                            query['SearchableText'] = ''

            except:
                pass


        # Search by number

        # Number comes as string in the request, let's make it an int
        number = request.get('getNumber','')
        if number and not isinstance(number, int):
            try:
                number = int(number)
                query['getNumber'] = number
            except:
                pass

        # Asign number to the search index matching the radio button
        # selected in the form, or we leave it as getNumber.
        if isinstance(number, int):
            numero_normativa = request.get('numero_normativa','')

            def use_number_as(number, attribute, query):
                temp_results = portal_catalog.searchResults(**query)
                temp_results_modifies = [getattr(a,attribute) for a in temp_results]
                i = 0
                while i < len(temp_results_modifies):
                    j = 0
                    while j < len(temp_results_modifies[i]):
                        if not isinstance(temp_results_modifies[i][j], int):
                            temp_results_modifies[i][j] = temp_results_modifies[i][j].getNumber()
                        j = j + 1
                    i = i + 1

                temp_results_tuple = zip(temp_results,temp_results_modifies)

                results = [a[0] for a in temp_results_tuple if number in a[1]]
                return results


            if numero_normativa == 'modifies':
                query['getNumber'] = ''
                return use_number_as(number, 'getModifies', query)
            elif numero_normativa == 'repeals':
                query['getNumber'] = ''
                return use_number_as(number, 'getRepeals', query)
            elif numero_normativa == 'isrepealedby':
                query['getNumber'] = ''
                return use_number_as(number, 'getRepealedBy', query)


        if query.get('SearchableText') and\
        not query.get('getKind') and\
        not query.get('getArea') and\
        not query.get('getNumber') and\
        not query.get('getDate') and\
        not query.get('getSource'):
            query['portal_type'] = ['Normativa', 'Attachment']

        results = portal_catalog.searchResults(**query)

        return results

