class Mixin(object):
    def mixIn(cls, dest):
        if not cls in dest.__bases__:
            dest.__bases__ = tuple(list(dest.__bases__) + [cls])

    mixIn = classmethod(mixIn)
