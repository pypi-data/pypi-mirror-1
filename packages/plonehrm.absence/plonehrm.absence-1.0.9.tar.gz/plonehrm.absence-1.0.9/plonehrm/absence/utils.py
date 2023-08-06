from zope.i18n import translate
from Products.CMFCore.utils import getToolByName


def localize(context, text):
    props = getToolByName(context, 'portal_properties')
    lang = props.site_properties.getProperty('default_language')
    return translate(text, target_language=lang)


