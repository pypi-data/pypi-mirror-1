from Products.CMFCore.utils import getToolByName

def patchedIsKupuEnabled(self, useragent='', allowAnonymous=False,
                         REQUEST=None, context=None,
                         fieldName=None):
    """
    """
    if not REQUEST:
        REQUEST = self.REQUEST
    def numerics(s):
        """Convert a string into a tuple of all digit sequences"""
        seq = ['']
        for c in s:
            if c.isdigit():
                seq[-1] = seq[-1] + c
            elif seq[-1]:
                seq.append('')
        return tuple([ int(val) for val in seq if val])

    # First check whether the user actually wants tinymce
    pm = getToolByName(self, 'portal_membership')
    if pm.isAnonymousUser() and not allowAnonymous:
        return False

    user = pm.getAuthenticatedMember()
    if not pm.isAnonymousUser():
        editor = user.getProperty('wysiwyg_editor')
        if editor and editor.lower() != 'kupu':
            return False

    # Then check whether the current content allows html
    if context is not None and fieldName and hasattr(context, 'getWrappedField'):
        field = context.getWrappedField(fieldName)
        if field:
            allowedTypes = getattr(field, 'allowable_content_types', None)
            if allowedTypes is not None and not 'text/html' in [t.lower() for t in allowedTypes]:
                return False

    return True
