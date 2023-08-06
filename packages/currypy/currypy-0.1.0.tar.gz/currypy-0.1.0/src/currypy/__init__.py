import functools

class Curry(object):

    def __init__(self, function, *args, **kwds):
        self.initPartialObject(function, *args, **kwds)
        return

    def __call__(self, *args, **kwds):
        return self._partial(*args, **kwds)

    def initPartialObject(self, function, *args, **kwds):
        self._partial = functools.partial(function,
                                          *args,
                                          **kwds)
        return

    def __getstate__(self):
        odict = self.__dict__.copy()
        odict['function'] = self._partial.func
        odict['args'] = self._partial.args
        odict['keywords'] = self._partial.keywords
        del odict['_partial']
        return odict


    def __setstate__(self, dict):
        function = dict['function']
        args = dict['args']
        keywords = dict['keywords']

        self.initPartialObject(function, *args, **keywords)

        return

    # END class Curry
    pass
