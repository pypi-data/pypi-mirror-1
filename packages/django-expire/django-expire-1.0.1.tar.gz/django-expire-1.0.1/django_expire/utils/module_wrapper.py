from django.conf import settings
from django.test import TestCase
from django.utils.importlib import import_module


def restore_attrs(wrapper):
    """
    Restore all attributes for a wrapped module to their original values
    (removing any which weren't originally set).

    """
    for key, value in wrapper._attrs_to_restore.iteritems():
        setattr(wrapper._wrapped_module, key, value)
    for setting in wrapper._delete_settings:
        try:
            delattr(wrapper._wrapped_module, setting)
        except AttributeError:
            pass


class ModuleWrapper(object):
    """
    A wrapper for modules which will remember attribute changes made so they
    can be reverted.

    """

    def __init__(self, module):
        """
        Initialise some containers to remember overwritten attributes to
        restore and newly added attributes to delete.

        """
        self.__dict__['_attrs_to_restore'] = {}
        self.__dict__['_attrs_to_delete'] = set()
        self.__dict__['_wrapped_module'] = module

    def __getattr__(self, key):
        """
        Retrieve an attribute.

        """
        getattr(self._wrapped_module, key)

    def __setattr__(self, key, value):
        """
        Change an attribute, remembering its original value so it can be
        reverted (or deleted if it didn't exist).

        """
        attrs_to_restore = self._attrs_to_restore
        try:
            if key not in attrs_to_restore:
                attrs_to_restore[key] = getattr(value, key)
        except AttributeError:
            self._attrs_to_delete.add(key)
        setattr(self._wrapped_module, key, value)

    def __delattr__(self, key):
        """
        Remove an attribute, remembering its original value so it can be
        restored.
        
        Deleting attributes which don't exist will *not* raise an exception.

        """
        try:
            if key not in self._attrs_to_delete and\
                            key not in self._attrs_to_restore:
                self._attrs_to_restore[key] = getattr(self._wrapped_module,
                                                      key)
            delattr(self._wrapped_module, key)
        except AttributeError:
            pass


class ModuleWrapperTestCase(TestCase):
    """
    A base test case that can be used to modify attributes in any number of
    modules under the knowledge that they will be returned to their original
    value (or removed if they didn't previously exist).

    To set which modules should be used, set the modules attribute on your test
    case subclass to a dictionary for modules which you would like to
    temporarily change attributes for.
    
    Each key should be the attribute which the wrapper will be available as and
    each value a module (or a dotted string representation of a module).
    
    For example::

        class MyTestCase(ModuleWrapperTestCase):
            modules = {'mymodule': myproject.mymodule}
            #...

    """
    modules = None

    def _pre_setup(self, *args, **kwargs):
        super(ModuleWrapperTestCase, self)._pre_setup(*args, **kwargs)
        if self.modules:
            for attr, module in self.modules.iteritems():
                if isinstance(module, basestring):
                    module = import_module(module)
                setattr(self, attr, ModuleWrapper(module))


class SettingsTestCase(ModuleWrapperTestCase):
    """
    A base test case that can be used to modify settings in
    ``django.conf.settings`` under the knowledge that they will be returned
    to their original value (or removed if they didn't previously exist).

    """
    modules = {'settings': settings}

    def restore_settings(self):
        """
        Restore all settings to their original values (removing any which
        weren't originally in settings).

        """
        restore_attrs(self.settings)
