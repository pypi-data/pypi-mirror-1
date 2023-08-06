"""Metadata storage class, with special treatment for Dublin Core metadata."""

class Metadata (object):
    """Store metadata, with special treatment for Dublin Core metadata.

       Takes notice of any arbitrary data. Does not allow
       attributes mirroring DC metadata but with different casing.

       Lazier than dublincore module; attributes read as '' by default
       and only actually enter existence when they are written to.
       Writing '' deletes an attribute.

       You can set attributes to any basic value (string mainly,
       but also list, tuple, dict ..). General meaning will be preserved
       (eg tuples are not guaranteed to remain tuples, but are guaranteed to
       remain sequences.)
       Nested Metadata objects are not allowed.

       'Looks like' a dublinCoreMetadata instance, so if you have dublincore
       and want eg.XML from a Metadata object, you can call
       dublincore.dublinCoreMetadata.makeXML (this, schema)
       
       All attributes are optional.
       
       Non DublinCore attribute names are forced to lowercase.
       
       Attributes
       -----------
       Title : string
       Creator : string
       Subject : string
       Description : string
       Publisher : string
       Contributor : string
       Date : string
       Type : string
       Format : string
       Identifier : string
       Source : string
       Language : string
       Relation : string
       Coverage : string
       Rights : string
       
       
       """
    __dublincore_attrs = 'Title Creator Subject Description Publisher \
                          Contributor Date Type Format Identifier Source \
                          Language Relation Coverage Rights'.split()
    def __init__(self, yaml = None, **kwargs):
        """Initialize metadata, reading key,value pairs from yaml and/or
        keyword args.
        DC metadata may be given in any case (title or Title or even TITLE).
        All other metadata keys are automatically lowercased."""
        self.update (kwargs)
        if yaml:
            self.from_yaml (yaml)
        # if the subject is a list, each term should be separated by 
        # semicolon

    def update (self, dict):
        for key, value in dict.items():
            titlecased = key.title()
            if titlecased in self.__dublincore_attrs and value != '':
                setattr (self, titlecased, value)
            else:
                setattr (self, key.lower(), value)

    def to_yaml (self):
        """Return a yaml representation of self"""
        import yaml
        return yaml.dump (self.__dict__, default_flow_style = False)

    def from_yaml (self, yaml):
        """Set parameters on self according to loaded yaml"""
        data = None
        if type (yaml) == str:
            import yaml as y
#            import cStringIO as IO
#            yaml = IO.StringIO (yaml)
            data = y.safe_load (yaml)
        elif hasattr (yaml, 'read'):
            import yaml as y
            data = y.safe_load (yaml)
        assert type (data) == dict
        self.update (data)
        
    def __repr__ (self):
        keys = self.__dict__.keys()
        keys.sort()
        kwbuffer = ('%s = %r' % (k, getattr (self, k)) for k in keys)
        formatted = ", ".join (kwbuffer)
        return "%s (%s)" % (self.__class__.__name__, formatted)

    def __setattr__ (self, key, value):
        tcase = key.title()
        if tcase in self.__dublincore_attrs:
            if tcase != key:
                print 'Warning: setting Dublin Core metadata items like %r \
                       using non-titlecase name (%r) is deprecated!' % (tcase,
                                                                        key)
            key = tcase

        else:
            lower = key.lower()
            if lower != key:
                print 'Warning: setting non-DC metadata using non-lowercase \
                       name %r is inappropriate!' % (key)
            key = lower
        if value == '':
            object.__delattr__ (self, key)
        else:
            object.__setattr__ (self, key, value)
        # XXX handle non-metadata attribute access?
    def __getattr__ (self, key):
        dcattrs = object.__getattribute__ (self, '__class__').__dublincore_attrs
        tcase = key.title()
        if tcase in dcattrs:
            if key != tcase:
                print 'Warning: don\'t ask for DC metadata using \
                       non-titlecased names (eg %r)!' % key
            key = tcase
        else:
            key = key.lower()
        value = object.__getattribute__ (self, '__dict__').get (key, '')
        if value != '':
            return value
        value = object.__getattribute__ (self, key)
        return value
        
        
        
def from_yaml (yaml):
    """Create a Metadata instance from YAML data
    
    Parameters
    ----------
    yaml : string or file-like object
           YAML is loaded using safe_load, so no special type treatment 
           (eg '!!mytype') is allowed.
    
    """
    return Metadata (yaml = yaml)

class Re2yaml (object):
    pass
    #register here

#example re2yaml:
#
# targetresolution : ('(?P<width>[0-9]+)?x?(?P<height>[0-9]+) ?(?P<xpixelsize>[0-9]):(?P<ypixelsize>[0-9])', 
#                     'target resolution: { width: %(width)d, height: %(height)d, pixelsize: %(xpixelsize)d/%(ypixelsize)d}\n',
#                      None)
# 
# width, height, xpixelsize, ypixelsize are automatically converted to int because they are specified as integer formatted.