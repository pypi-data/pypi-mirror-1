from peak.util.decorators import decorate, decorate_class
from weakref import ref
import sys

__all__ = ['Role', 'ClassRole', 'roledict_for']

_roledicts = {}

def roledict_for(ob):
    """Get the dictionary that should contain roles for `ob`"""
    try:
        d = ob.__dict__
        sd = d.setdefault
        return d
    except (AttributeError, TypeError):
        r = ref(ob)
        try:
            return _roledicts[r]
        except KeyError:
            return _roledicts.setdefault(ref(ob, _roledicts.__delitem__), {})


def additional_tests():
    import doctest
    return doctest.DocFileSuite(
        'README.txt', package='__main__',
        optionflags=doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE,
    )













class Role(object):
    """Attach extra state to (almost) any object"""

    __slots__ = ()

    class __metaclass__(type):
        def __call__(cls, ob, *data):
            a = roledict_for(ob)
            role_key = cls.role_key(*data)
            try:
                return a[role_key]
            except KeyError:
                # Use setdefault() to prevent race conditions
                ob = a.setdefault(role_key, type.__call__(cls, ob, *data))
                return ob

    decorate(classmethod)
    def role_key(cls, *args):
        if args: return (cls,)+args
        return cls

    decorate(classmethod)
    def exists_for(cls, ob, *key):
        """Does an aspect of this type for the given key exist?"""
        return cls.role_key(*key) in roledict_for(ob)

    decorate(classmethod)
    def delete_from(cls, ob, *key):
        """Ensure an aspect of this type for the given key does not exist"""
        a = roledict_for(ob)
        try:
            del a[cls.role_key(*key)]
        except KeyError:
            pass

    def __init__(self, subject):
        pass




class ClassRole(Role):
    """Attachment/annotation for classes and types"""

    class __metaclass__(Role.__class__):
        def __call__(cls, ob, *data):
            role_key = cls.role_key(*data)
            d = ob.__dict__
            if role_key in d:
                return d[role_key]
            d2 = roledict_for(ob)
            try:
                return d2[role_key]
            except KeyError:
                # Use setdefault() to prevent race conditions
                ob = d2.setdefault(role_key, type.__call__(cls, ob, *data))
                return ob

    decorate(classmethod)
    def for_enclosing_class(cls, *args, **kw):
        if 'frame' in kw:
            frame = kw.pop('frame')
        else:
            if 'level' in kw:
                level = kw.pop('level')
            else:
                level = 2
            frame = sys._getframe(level)
        if kw:
            raise TypeError("Unexpected keyword arguments", kw)

        a = frame.f_locals
        role_key = cls.role_key(*args)
        try:
            return a[role_key]
        except KeyError:
            # Use setdefault() to prevent race conditions
            ob = a.setdefault(role_key, type.__call__(cls, None, *args))
            decorate_class(ob.__decorate, frame=frame)
            return ob


    decorate(classmethod)
    def exists_for(cls, ob, *key):
        """Does an aspect of this type for the given key exist?"""
        role_key = cls.role_key(*key)
        return role_key in ob.__dict__ or role_key in roledict_for(ob)

    decorate(classmethod)
    def delete_from(cls, ob, *key):
        """Class Roles are not deletable!"""
        raise TypeError("ClassRoles cannot be deleted")

    def __decorate(self, cls):
        self.created_for(cls)
        return cls

    def created_for(self, cls):
        """Override to access the decorated class, as soon as it's known"""

    def __init__(self, subject):
        """Ensure ``created_for()`` is called, if class already exists"""
        if subject is not None:
            self.created_for(subject)



















