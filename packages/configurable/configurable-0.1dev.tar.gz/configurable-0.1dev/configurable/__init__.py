import os
from types import StringType, IntType, FloatType, BooleanType, TupleType
import ConfigParser



class AttrDict(dict):
    """
    AttrDict()
        A dictionary exposing items as attributes as well.
        Attributes beginning with "_" are handled as normal attributes.
        
    >>> a = AttrDict(asd=123)
    >>> a["foo"] = "bar"
    >>> a.hihi = "hoho"
    >>> assert a.asd == 123
    >>> assert a.foo == "bar"
    >>> assert a.hihi == "hoho"
    >>> a._fnurk = 123
    >>> assert not a.has_key("_fnurk")
    """
    def __getattr__(self, name):
        if len(name) and name[0]!="_":
            return self.__getitem__(name)
        return dict.__getattr__(self, name)
    
    def __setattr__(self, name, value):
        if len(name) and name[0]!="_":
            self.__setitem__(name, value)
        return dict.__setattr__(self, name, value)
        
    def dump(self):
        for (key, val) in self.iteritems():
            print key, "=", val
        
____AttrDict = AttrDict()
AttrDictType = type(____AttrDict)
del ____AttrDict






class ConfigMixIn(object):
    """
    A class subclassing ConfigMixIn and having a config attribute
    of type Config can have its config params set through a config file.
    
    Each section of a config file opened with ConfigFile with a name
    matching a ConfigMixIn subclass, will have all parameters defined
    in that section copied to the config attribute of that class.
    
    Don't forget to pass globals() to ConfigFile so its constructor can
    find all classes in your global namespace subclassing ConfigMixIn.
    
    
    Note that the config attribute is shared between ALL classes (if set
    on class level). Subclass Configurable instead of ConfigMixIn
    (and call its constructor) if you need local copies of config.
    
    #>>> klass.configure_class(prop2=777)
    
    >>> class klass(ConfigMixIn):
    ...    config = Config(
    ...        prop1 = "asd",
    ...        prop2 = 123,
    ...        prop3 = True,
    ...    )
    >>> k = klass()
    >>> assert k.config.prop1 == "asd"
    >>> assert k.config.prop2 == 123
    >>> assert k.config.prop3 == True
    >>> k.config.prop2 = 777 # alter prop2
    >>> k2 = klass()
    >>> assert k.config.prop2 == 777 # prop2 was altered for ALL instances!
    >>> assert k2.config.prop2 == 777
    """
    class InvalidConfigParam(Exception):
        pass
    
    def configure(self, **kw):
        for (key, val) in kw.iteritems(): 
            if not self.config.has_key(key):
                raise self.InvalidConfigParam(key)
            self.config[key] = val
    
    @classmethod
    def configure_class(cls, **kw):
        for (key, val) in kw.iteritems():
            if not cls.config.has_key(key):
                raise cls.InvalidConfigParam(key)
            cls.config[key] = val




class Configurable(ConfigMixIn):
    """
    The difference between a ConfigMixIn and a Configurable is that
    the latter has an __init__() function which creates a local copy
    of its config attribute so instances can change their configuration
    without altering class-wide behaviour.
    
    >>> class klass(Configurable):
    ...    config = Config(
    ...        prop1 = "asd",
    ...        prop2 = 123,
    ...        prop3 = True,
    ...    )
    >>> k = klass()
    >>> assert k.config.prop1 == "asd"
    >>> assert k.config.prop2 == 123
    >>> assert k.config.prop3 == True
    >>> k.config.prop2 = 777 # alter prop2
    >>> k2 = klass()
    >>> assert k.config.prop2 == 777 
    >>> assert k2.config.prop2 == 123 # prop2 was NOT altered for all instances!
    
    Also note that configure_class() on a Configurable affects configuration
    of instances created AFTER the call to configure_class(). In a ConfigMixIn
    on the other hand, all instances share the same configuration.
    """
    def __init__(self, **kw):
        self.config = self.config._copy()
        self.configure(**kw)
        

        
        

class Config(AttrDict):
    """
    Config instances assigned to class MUST be named 'config'.
    
    BEWARE: the config instance is shared between ALL instances
    if created for a class.
    """
    
    _simple_types = (IntType, FloatType, BooleanType)
    
    def __init__(self, convert_simple_types=True, convert_all_types=False, **kw):
        self._convert_all_types = convert_all_types
        self._convert_simple_types = convert_all_types or convert_simple_types
        AttrDict.__init__(self, **kw)
    
    def _convert_type(self, t, value):
        if t is BooleanType \
                and type(value) is StringType \
                and value.lower() == "false":
            return False
        else:
            return t(value)
        
    def __setitem__(self, name, value):
        if len(name) and name[0]!="_":
            t = type(getattr(self, name))
            if self._convert_all_types \
                    or (self._convert_simple_types and t in self._simple_types):
                value = self._convert_type(t, value)
        AttrDict.__setitem__(self, name, value)
    
    def _copy(self):
        cnew = Config(**self)
        cnew._convert_all_types = self._convert_all_types
        cnew._convert_simple_types = self._convert_simple_types
        return cnew
        
        
        
        

__configFileExample = """
[sect1]
foo=bar

[Klass]
prop1=qwe
prop2=456
prop3=false

[SubKlass]
hihi = HEHE
"""


class ConfigFile(AttrDict):
    """
    ConfigFile - Uses ConfigParser to make config params accessible through a
      tree-like structure. It also configures classes subclassing Configurable,
      setting sub-attributes on its config attribute to match parameters found
      in the config section having the same name as the class.
      See examples below and ConfigMixIn and Configurable for more info.
      
        Simple example:
        >> c = ConfigFile("foo.conf")
        >> myparam = c.sectionname.paramname
        
    Detailed doctest example:
    >>> import tempfile
    >>> f, path = tempfile.mkstemp(prefix="doctest_")
    >>> _ = os.write(f, __configFileExample)
    >>> os.close(f)
    >>> class Klass(Configurable):
    ...    class SubKlass(Configurable):
    ...        config = Config(hihi = "hoho")
    ...    config = Config(
    ...        prop1="asd",
    ...        prop2=123,
    ...        prop3=True
    ...    )
    >>> assert Klass.config.prop1 == "asd"
    >>> assert Klass.config.prop2 == 123
    >>> assert Klass.config.prop3 == True
    >>> assert Klass.SubKlass.config.hihi == "hoho"
    >>> c = ConfigFile(path, globals())
    >>> assert Klass.config.prop1 == "qwe"
    >>> assert Klass.config.prop2 == 456
    >>> assert Klass.config.prop3 == False
    >>> assert Klass.SubKlass.config.hihi == "HEHE"
    >>> assert c.Klass.prop1 == "qwe"
    >>> assert c.Klass.prop2 == "456"
    >>> assert c.Klass.prop3 == "false"
    >>> assert c.SubKlass.hihi == "HEHE"
    >>> assert c.sect1.foo == "bar"
    """
    def __init__(self, filenames, namespace=dict(), seek_depth=2):
        """
        Instantiating with namespace=globals() causes all ConfigMixIns
        in global namespace to be configured.
        """
        AttrDict.__init__(self)
        self._configparser = ConfigParser.SafeConfigParser()
        if type(filenames) is StringType:
            filenames = (filenames,)
        self._configparser.read(*filenames)
        # build attribute tree
        for section in self._configparser.sections():
            items = AttrDict(self._configparser.items(section))
            self[section] = items
        self.configure_configurables(namespace, seek_depth)
        
    def is_object(self, value):
        "seek everything that is an object"
        try:
            if issubclass(value, object):
                return True
        except TypeError:
            pass
        return False
    
    def should_configure(self, value):
        "configure everything that is a ConfigMixIn (including Configurable)"
        try:
            if issubclass(value, ConfigMixIn):
                return True
        except TypeError:
            pass
        return False

    def configure_configurables(self, namespace, level):
        if level <= 0:
            return
        for section in self._configparser.sections():
            items = AttrDict(self._configparser.items(section))
            # work configurables on this level
            if namespace.has_key(section):
                cls = namespace[section]
                if self.should_configure(cls):
                    cls.configure_class(**items)
            # work next level
            for name, value in namespace.iteritems():
                if len(name) and name[0] == "_":
                    continue
                # only look at new-style classes
                if self.is_object(value):
                    self.configure_configurables(vars(value), level-1)






class TypeTemplateException(Exception): pass

class TypeTemplate:
    """
    TypeTemplate provides a straight-forward way to turn strings
    into other types or tuples of types. The most obvious area
    where to apply this is when handling strings originating from
    configuration files parsed with any of the *ConfigParser classes.

    >>> T = TypeTemplate
    >>> t = T(float)
    >>> t("25")
    25.0
    >>> t = T(str, int, bool)
    >>> t("foo, 1, 0")
    ('foo', 1, False)
    >>> T.namespace = locals()
    >>> fnurk = 33
    >>> T(object, bool)("fnurk, 6")
    (33, True)
    >>> t = T(str, float, bool)
    >>> t.delimiter = "xy"
    >>> t("bar xy 77 xy hehe")
    ('bar', 77.0, True)
    """

    delimiter = ","
    namespace = {}
    strip_tokens = True

    def __init__(self, *template):
        self._template = template

    def __call__(self, s):
        if len(self._template) >= 2:
            return self.string_to_tuple(s)
        elif len(self._template) == 1:
            return self.string_to_type(s, self._template[0])
        return None

    def string_to_tuple(self, s):
        tokens = s.split(self.delimiter)
        if self.strip_tokens:
            tokens = [tok.strip() for tok in tokens]
        if len(tokens) != len(self._template):
            raise TypeTemplateException("Needed %d tokens, found %d: %s" \
                                     %(len(self._template), len(tokens), s))
        return tuple([ self.string_to_type(s,t) \
                       for s,t in zip(tokens, self._template) ])

    def string_to_boolean(self, s):
        s = s.strip()
        if len(s)==0 or s=="0" or s.lower()=="false":
            return False
        return True    

    def string_to_object(self, s):
        return self.namespace[s]

    def string_to_type(self, s, t):
        if t is TupleType: #should never happen for now
            return self.string_to_tuple(s, t)
        elif t is BooleanType:
            return self.string_to_boolean(s)
        elif t is object:
            return self.string_to_object(s)
        return t(s)



__all__ = [
    "AttrDict",
    "AttrDictType",
    "ConfigMixIn",
    "Configurable",
    "Config",
    "ConfigFile",
    "TypeTemplateException",
    "TypeTemplate"
]        
 



if __name__ == "__main__":
    import doctest
    doctest.testmod()
