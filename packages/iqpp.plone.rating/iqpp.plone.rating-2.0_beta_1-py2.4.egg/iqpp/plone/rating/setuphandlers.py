# CMFCore imports
from Products.CMFCore.utils import getToolByName

def importVarious(context):
    """Import various settings.
    """
    # This will call itself recursively, don't now why atm
    
    # portal = context.getSite()
    # qit = getToolByName(portal, "portal_quickinstaller")
    # 
    # products_to_install = ["iqpp.rating"]
    #                        
    # ids = [ x['id'] for x in qit.listInstallableProducts(skipInstalled=1) ]
    # for product in products_to_install:
    #     if product in ids:
    #         qit.installProduct(product)