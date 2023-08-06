from Products.CMFCore.CMFCatalogAware import aq_base

def opaqueItems(self):
    """
        Return opaque items (subelements that are contained
        using something that is not an ObjectManager).
    """
    items = []

    # Call 'talkback' knowing that it is an opaque item.
    # This will remain here as long as the discussion item does
    # not implement ICallableOpaqueItem (backwards compatibility).
    if hasattr(aq_base(self), 'talkback'):
        talkback = self.talkback
        if talkback is not None:
            items.append((talkback.id, talkback))

    return tuple(items)


