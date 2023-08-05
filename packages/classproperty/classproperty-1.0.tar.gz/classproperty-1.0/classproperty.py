class classpropertytype(property):

    def __init__(self, name, bases=(), members={}):
        return super(classpropertytype, self).__init__(
            members.get('__get__'),
            members.get('__set__'),
            members.get('__delete__'),
            members.get('__doc__')
            )

classproperty = classpropertytype('classproperty')

if __name__ == "__main__":
    import doctest
    doctest.testfile('classproperty.txt')
