##########################################################################
# humboldt.cmfbibliographyat - published under the GNU Public License V 2
# Written by Andreas Jung, ZOPYX Ltd. & Co. KG, D-72070 Tuebingen, Germany
##########################################################################


import urllib
from zope.component import getMultiAdapter
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from Products.CMFCore.utils import getToolByName


class SFXViewlet(ViewletBase):
    render = ViewPageTemplateFile('sfx.pt')

    def getSFXURL(self):

        pp_tool = getToolByName(self.context, 'portal_properties')
        bib_props = getToolByName(pp_tool, 'cmfbibliographyat', None)
        if bib_props is None:
            return None

        if bib_props.sfx_integration:
            coinsData = self.context.getCoinsDict()
            data = list()
            data.append(('ctx_ver', 'Z39.88-2004'))
            for k in ('rft_val_fmt', 'rfr_id'):
                data.append((k, coinsData[k]))
            for k,v in coinsData.items():
                if v is None:
                    continue

                if isinstance(v, (int, basestring)):
                    if k.startswith('rft.') and v:
                        data.append((k[4:], v))  # chop of 'rft' prefix
                else:
                    for v2 in v:
                        if k.startswith('rft.') and v2:
                            data.append((k[4:],  v2)) # chop of 'rft' prefix

            qs = '&'.join(['%s=%s' % (k, urllib.quote(v)) for k,v in data])
            return '%s?%s' % (bib_props.meta_resolver_url, qs)
        return None

