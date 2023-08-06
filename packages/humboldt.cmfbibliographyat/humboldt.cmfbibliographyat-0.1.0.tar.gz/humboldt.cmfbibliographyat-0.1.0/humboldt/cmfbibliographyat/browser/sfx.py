from zope.component import getMultiAdapter
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from Products.CMFCore.utils import getToolByName

from ZTUtils import make_query

class SFXViewlet(ViewletBase):
    render = ViewPageTemplateFile('sfx.pt')

    def getSFXURL(self):

        pp_tool = getToolByName(self.context, 'portal_properties')
        bib_props = getToolByName(pp_tool, 'cmfbibliographyat')

        if bib_props.sfx_integration:
            coinsData = self.context.getCoinsDict()
            data = dict()
            data['ctx_ver'] = 'Z39.88-2004'
            for k in ('rft_val_fmt', 'rfr_id'):
                data[k] = coinsData[k]
            for k,v in coinsData.items():
                if k.startswith('rft.') and v:
                    data[k[4:]] = v # chop of 'rft' prefix
            return '%s?%s' % (bib_props.meta_resolver_url, make_query(**data))
        return None

