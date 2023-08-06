# -*- coding: utf-8 -*-

##########################################################################
# humboldt.cmfbibliographyat - published under the GNU Public License V 2
# Written by Andreas Jung, ZOPYX Ltd. & Co. KG, D-72070 Tuebingen, Germany
##########################################################################


from StringIO import StringIO
from Products.CMFCore.utils import getToolByName

class Generator(object):

    def setupProperties(self, p, out):
        """ Add propertysheet with SFX server related properties """

        sheet_id = 'cmfbibliographyat'
        pp_tool = getattr(p, 'portal_properties')
        if not sheet_id in pp_tool.objectIds():
            pp_tool.addPropertySheet(sheet_id, sheet_id)

        sheet = pp_tool[sheet_id]
        if not sheet.hasProperty('sfx_integration'):
            sheet.manage_addProperty('sfx_integration', True, 'boolean')
        if not sheet.hasProperty('meta_resolver_url'):
            sheet.manage_addProperty('meta_resolver_url', 'http://worldcatlibraries.org/registry/gateway', 'string')

        print >> out, "Humboldt CMFBibliographyAT extensions activated \n"


def setupVarious(context):

    if context.readDataFile('humboldt.cmfbibliographyat_various.txt') is None:
        return
    # Add additional setup code here
    out = StringIO()
    site = context.getSite()
    gen = Generator()
    gen.setupProperties(site, out)
    logger = context.getLogger('humboldt.cmfbibliographyat')
    logger.info(out.getvalue())
