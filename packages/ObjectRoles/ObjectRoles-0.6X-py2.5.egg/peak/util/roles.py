"""This module is DEPRECATED.  Please use AddOns (peak.util.addons) instead"""

from peak.util import addons

__all__ = ['Role', 'ClassRole', 'Registry', 'roledict_for']

roledict_for = addons.addons_for

class Role(addons.AddOn):
    """Attach extra state to (almost) any object"""
    __slots__ = ()

    role_key = classmethod(addons.AddOn.addon_key.im_func)

    def addon_key(cls, *args):
        return cls.role_key(*args)

    addon_key = classmethod(addon_key)
    
class ClassRole(addons.ClassAddOn, Role):
    """Attachment/annotation for classes and types"""
    __slots__ = ()
    
    def delete_from(cls, ob, *key):
        """Class Roles are not deletable!"""
        raise TypeError("ClassRoles cannot be deleted")
    delete_from = classmethod(delete_from)
    
class Registry(addons.Registry, Role):
    """ClassRole that's a dictionary with mro-based inheritance"""
    __slots__ = ()
    
def additional_tests():
    import doctest
    return doctest.DocFileSuite(
        'README.txt', package='__main__',
        optionflags=doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE,
    )



