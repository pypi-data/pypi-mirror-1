# this class allows to compute an attribute calling a method for the first time and then it stores the result
# in the attribute (overwriting the getter method). Useful for lazy attributes
# use as a decorator
class Lazy(object):
    def __init__(self, calculate_function):
        self._calculate = calculate_function

    def __get__(self, obj, _=None):
        if obj is None:
            return self
        value = self._calculate(obj)
        setattr(obj, self._calculate.func_name, value)
        return value

