##########################################################################
# humboldt.cmfbibliographyat - published under the GNU Public License V 2
# Written by Andreas Jung, ZOPYX Ltd. & Co. KG, D-72070 Tuebingen, Germany
##########################################################################


from Products.Archetypes.public import DisplayList

def publicationIdentifiers(self, instance=None):
    """ return a vocabulary for the 'identifiers' field """

    pt = instance.portal_type
    if pt in ('BookReference',):
        fields = ('ISBN', 'ASIN', 'DOI', 'PURL', 'URN', 'PMID')

    elif pt in ('BookletReference',
                'InproceedingsReference',
                'PhdthesisReference',
                ):
        fields = ('ISBN', 'ISSN', 'ASIN', 'DOI', 'PURL', 'URN', 'PMID')
    else:
        fields = ('ISBN', 'DOI', 'PURL', 'URN', 'PMID')

    return DisplayList([(term, term) for term in fields])
