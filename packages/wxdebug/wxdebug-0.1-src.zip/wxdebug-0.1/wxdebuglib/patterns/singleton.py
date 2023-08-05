class Singleton(type):
    ''' Copied from taskcoach: http://members.chello.nl/f.niessink/
        
        Singleton metaclass. Use by defining the metaclass of a class Singleton,
        e.g.: class ThereCanBeOnlyOne:
                  __metaclass__ = Singleton 
    '''              

    def __call__(class_, *args, **kwargs):
        if not hasattr(class_, 'instance'):
            class_.instance = super(Singleton, class_).__call__(*args, **kwargs)
        return class_.instance

    def deleteInstance(class_):
        ''' Delete the (only) instance. '''
        try:
            del class_.instance
        except:
            # May be no instance created
            pass
