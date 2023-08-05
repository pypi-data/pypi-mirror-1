class accessor(object):
    def __init__(self, func):
        self.func = func

    def patch(self, obj):
        self.name = self.func.func_name
        self.aname = "_" + self.name
        aname = self.aname # needed for closures getter setter
        self.setterName = "set" + self.name.capitalize()
        self.getterName = "get" + self.name.capitalize()
        
        def getter(self):
            return getattr(obj, aname)
        
        def setter(self, value):
            return setattr(self, aname, value)
        
        cls = obj.__class__
        setattr(cls, self.getterName, getter)
        setattr(cls, self.setterName, setter)
        setattr(cls, self.name, property(getter,setter))

    def __get__(self, obj, _=None):
        self.patch(obj)
        return getattr(obj, self.aname)

    def __set__(self, obj, value, _=None):
        self.patch(obj)
        return setattr(obj, self.aname, value)

# class Test(object):
#    @accessor
#    def test(self): pass

# t = Test()
# t.test = 10
# print t.test
# t.setTest(20)
# print t.test
# t.test = 30

# print t.__dict__
# print t.test

