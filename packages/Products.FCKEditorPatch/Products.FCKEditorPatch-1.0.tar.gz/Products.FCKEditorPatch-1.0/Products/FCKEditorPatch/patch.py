from Products.FCKeditor import utils

def patchInfoDictForType(ptype, portal_types, utranslate):
    """
    UI type infos
    @param ptype: a portal type name
    @param portal_types: the portal_types tool
    @param utranslate: the translation func
    @return: {'portal_type': xxx, 'type_ui_info': UI type info}
    """
    try:
        type_info = getattr(portal_types, ptype)
    except AttributeError:
        # we have a type that didn't provide enough
        # info for archetypes to register it correctly
        import re
        classpat = re.compile(r'([A-Z][a-z]+)')
        new_ptype = (" ").join(classpat.findall(ptype))
        type_info = getattr(portal_types, new_ptype)
    title = type_info.Title()
    product = type_info.product
    type_ui_info = ("%s (portal type: %s, product: %s)" %
                    (utranslate(title, default=title), ptype, product))
    return {
        'portal_type': ptype,
        'type_ui_info': type_ui_info
        }

utils.infoDictForType = patchInfoDictForType
print "PATCHED FCKEDITOR FOR PORTAL_TYPE BUG"

