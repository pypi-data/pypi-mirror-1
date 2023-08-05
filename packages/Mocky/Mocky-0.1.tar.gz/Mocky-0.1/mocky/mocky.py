class Mocky(object):
    """Mocky is a class that wants to help you with setting up mock
    objects for your tests.  It helps you observe which functions get
    called (with which parameters) and which attributes are set.

    Unless given a name, a Mocky's name is 'root':

      >>> Mocky().name
      'root'

    Let's start with a simple example that sets some variables so we
    get a feeling of how Mocky works.  Note that attribute accesss
    will never result in AttributeError.  Instead, an attribute access
    to a nonexistent member variable will yield another Mocky
    instance:

      >>> f = Mocky('f')
      >>> f
      f
      >>> unusual = f.unusual
      >>> unusual
      f.unusual
      >>> type(unusual) is Mocky
      True
      >>> unusual is f.unusual
      True
      >>> f.a.c.r = 'Fidelio'
      Set f.a.c.r to 'Fidelio'
      >>> f.a.c.r
      'Fidelio'

    Note that when we set 'f.a.c.r' to 'Fidelio', Mocky printed out
    that the attribute was set.  Suppose we have a function 'fun' that
    sets some fancy variable on a given object:

      >>> def fun(obj):
      ...     if obj.please_process_me:
      ...         obj.there_you = 'go'
      >>> myobj = Mocky('myobj')
      >>> fun(myobj)
      Set myobj.there_you to 'go'
      >>> myobj.please_process_me = False
      Set myobj.please_process_me to False
      >>> fun(myobj)

    Mocky also supports calling.  Another function that does a bit
    more with our test object:

      >>> def starve(character):
      ...     character.getStatus().hitpoints -= 1
      >>> starve(Mocky('Hugo')) # doctest: +ELLIPSIS
      Traceback (most recent call last):
      ...
      TypeError: unsupported operand type(s) for -=: 'Mocky' and 'int'
      >>> ezequiel = Mocky('ezequiel')
      >>> ezequiel.getStatus().hitpoints = 0
      Called ezequiel.getStatus()
      Set ezequiel.getStatus().hitpoints to 0
      >>> starve(ezequiel)
      Called ezequiel.getStatus()
      Set ezequiel.getStatus().hitpoints to -1

    For calls, Mocky will return the same value if the signature is
    the same:

      >>> secret = f.unusual(password='secret')
      Called f.unusual(password='secret')
      >>> secret is f.unusual(password='secret')
      Called f.unusual(password='secret')
      True
      >>> secret is f.unusual(password='unsafe')
      Called f.unusual(password='unsafe')
      False
    """
    def __init__(self, name='root'):
        self.__dict__['name'] = name
        self.__dict__['_calls'] = {}

    def __call__(self, *args, **kwargs):
        argsstr = ', '.join([repr(arg) for arg in args])
        keys = sorted(kwargs.keys())
        kwargsstr = ', '.join(['%s=%r' % (key, kwargs[key]) for key in keys])
        if argsstr and kwargsstr:
            allargs = ', '.join([argsstr, kwargsstr])
        else:
            allargs = argsstr or kwargsstr

        print "Called %s(%s)" % (self.name, allargs)
        if allargs not in self._calls:
            self._calls[allargs] = Mocky('%s(%s)' % (self.name, allargs))
        return self._calls[allargs]

    def __repr__(self):
        return self.name

    def __getattr__(self, name):
        if name not in self.__dict__:
            self.__dict__[name] = Mocky('%s.%s' % (self.name, name))
        return self.__dict__[name]

    def __setattr__(self, name, value):
        print "Set %s.%s to %r" % (self.name, name, value)
        self.__dict__[name] = value
