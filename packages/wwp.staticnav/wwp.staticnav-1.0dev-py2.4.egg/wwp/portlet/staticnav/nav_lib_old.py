


from Products.CMFCore.utils import getToolByName


def nav_init(context):

    urltool = getToolByName(context, 'portal_url')
    catalog = getToolByName(context, 'portal_catalog')
    print 'hello'

    return urltool,catalog

