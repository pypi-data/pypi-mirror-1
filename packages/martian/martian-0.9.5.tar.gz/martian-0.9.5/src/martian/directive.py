import sys
import inspect

from zope.interface.interfaces import IInterface

from martian import util
from martian.error import GrokImportError

class StoreOnce(object):

    def set(self, locals_, directive, value):
        if directive.dotted_name() in locals_:
            raise GrokImportError(
                "The '%s' directive can only be called once per %s." %
                (directive.name, directive.scope.description))
        locals_[directive.dotted_name()] = value

    def get(self, directive, component, default):
        return getattr(component, directive.dotted_name(), default)

    def setattr(self, context, directive, value):
        setattr(context, directive.dotted_name(), value)

ONCE = StoreOnce()

class StoreOnceGetFromThisClassOnly(StoreOnce):

    def get(self, directive, component, default):
        return component.__dict__.get(directive.dotted_name(), default)

class StoreMultipleTimes(StoreOnce):

    def get(self, directive, component, default):
        if getattr(component, directive.dotted_name(), default) is default:
            return default

        if getattr(component, 'mro', None) is None:
            return getattr(component, directive.dotted_name())

        result = []
        for base in reversed(component.mro()):
            list = getattr(base, directive.dotted_name(), default)
            if list is not default and list not in result:
                result.append(list)

        result_flattened = []
        for entry in result:
            result_flattened.extend(entry)
        return result_flattened

    def set(self, locals_, directive, value):
        values = locals_.setdefault(directive.dotted_name(), [])
        values.append(value)

MULTIPLE = StoreMultipleTimes()

class StoreDict(StoreOnce):

    def get(self, directive, component, default):
        if getattr(component, directive.dotted_name(), default) is default:
            return default

        if getattr(component, 'mro', None) is None:
            return getattr(component, directive.dotted_name())

        result = {}
        for base in reversed(component.mro()):
            mapping = getattr(base, directive.dotted_name(), default)
            if mapping is not default:
                result.update(mapping)
        return result

    def set(self, locals_, directive, value):
        values_dict = locals_.setdefault(directive.dotted_name(), {})
        try:
            key, value = value
        except (TypeError, ValueError):
            raise GrokImportError(
                "The factory method for the '%s' directive should return a "
                "key-value pair." % directive.name)
        values_dict[key] = value

DICT = StoreDict()

_SENTINEL = object()
_USE_DEFAULT = object()

class ClassScope(object):
    description = 'class'

    def check(self, frame):
        return util.frame_is_class(frame) and not is_fake_module(frame)

CLASS = ClassScope()

class ClassOrModuleScope(object):
    description = 'class or module'

    def check(self, frame):
        return util.frame_is_class(frame) or util.frame_is_module(frame)

CLASS_OR_MODULE = ClassOrModuleScope()

class ModuleScope(object):
    description = 'module'

    def check(self, frame):
        return util.frame_is_module(frame) or is_fake_module(frame)

MODULE = ModuleScope()

class Directive(object):

    default = None

    def __init__(self, *args, **kw):
        self.name = self.__class__.__name__

        self.frame = frame = sys._getframe(1)
        if not self.scope.check(frame):
            raise GrokImportError("The '%s' directive can only be used on "
                                  "%s level." %
                                  (self.name, self.scope.description))

        self.check_factory_signature(*args, **kw)

        validate = getattr(self, 'validate', None)
        if validate is not None:
            validate(*args, **kw)

        value = self.factory(*args, **kw)

        self.store.set(frame.f_locals, self, value)

    # To get a correct error message, we construct a function that has
    # the same signature as check_arguments(), but without "self".
    def check_factory_signature(self, *arguments, **kw):
        args, varargs, varkw, defaults = inspect.getargspec(
            self.factory)
        argspec = inspect.formatargspec(args[1:], varargs, varkw, defaults)
        exec("def signature_checker" + argspec + ": pass")
        try:
            signature_checker(*arguments, **kw)
        except TypeError, e:
            message = e.args[0]
            message = message.replace("signature_checker()", self.name)
            raise TypeError(message)

    def factory(self, value):
        return value

    def get_default(self, component):
        return self.default

    @classmethod
    def dotted_name(cls):
        return cls.__module__ + '.' + cls.__name__

    @classmethod
    def get(cls, component, module=None):
        # Create an instance of the directive without calling __init__
        self = cls.__new__(cls)

        value = self.store.get(self, component, _USE_DEFAULT)
        if value is _USE_DEFAULT and module is not None:
            value = self.store.get(self, module, _USE_DEFAULT)
        if value is _USE_DEFAULT:
            value = self.get_default(component)

        return value

    @classmethod
    def set(cls, component, value):
        # Create an instance of the directive without calling __init__
        self = cls.__new__(cls)
        cls.store.setattr(component, self, value)


class MultipleTimesDirective(Directive):
    store = MULTIPLE
    default = []


class MarkerDirective(Directive):
    store = ONCE
    default = False

    def factory(self):
        return True


class baseclass(MarkerDirective):
    scope = CLASS
    store = StoreOnceGetFromThisClassOnly()


def validateText(directive, value):
    if util.not_unicode_or_ascii(value):
        raise GrokImportError("The '%s' directive can only be called with "
                              "unicode or ASCII." % directive.name)

def validateInterfaceOrClass(directive, value):
    if not (IInterface.providedBy(value) or util.isclass(value)):
        raise GrokImportError("The '%s' directive can only be called with "
                              "a class or an interface." % directive.name)


def validateInterface(directive, value):
    if not (IInterface.providedBy(value)):
        raise GrokImportError("The '%s' directive can only be called with "
                              "an interface." % directive.name)


# this here only for testing purposes, which is a bit unfortunate
# but makes the tests a lot clearer for module-level directives
# also unfortunate that fake_module needs to be defined directly
# in the fake module being tested and not in the FakeModule base class;
# the system cannot find it on the frame if it is in the base class.
def is_fake_module(frame):
    return frame.f_locals.has_key('fake_module')
