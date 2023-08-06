from zope.component.factory import Factory

class ATFactory(Factory):
    """Zope 3 style factory for archetypes.
    
    We expect parent as kw arg in the __call__ function to hook the newly
    created object to the acquisition chain. this ensures .initializeArchtype()
    perform what's expected.
    """

    def __call__(self, *args, **kw):
        parent = kw.get('parent')
        ob = self._callable(*args, **kw)
        ob = ob.__of__(parent)
        ob.initializeArchetype()
        return ob
