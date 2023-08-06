from Products.CMFCore.interfaces import ISiteRoot
from Acquisition import aq_inner, aq_parent

def traverseTo(context, iface):
    """ This traverses towards ISiteRoot and looks for a interface iface
        and returns the object if found. None otherwise.
    """
    return _acquire_to_object(aq_inner(context), iface)

def _acquire_to_object(context, iface):
    if iface.providedBy(context):
        return context
    if ISiteRoot.providedBy(context):
        return None

    parent = aq_parent(context)
    if parent == context:
        return None

    return _acquire_to_object(parent, iface)
