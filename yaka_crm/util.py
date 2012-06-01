import functools
import time
from logbook import Logger


class timer(object):
  """Decorator that mesures the time it takes to run a function."""

  __instances = {}

  def __init__(self, f):
    self.__f = f
    self.log = Logger(f.func_name)

  def __call__(self, *args, **kwargs):
    self.__start = time.time()
    result = self.__f(*args, **kwargs)
    value = time.time() - self.__start
    self.log.info('ellapsed time: {0:.2f}ms'.format(value * 1000))
    return result


# From http://wiki.python.org/moin/PythonDecoratorLibrary#Memoize
class memoized(object):
  """
  Decorator. Caches a function's return value each time it is called.
  If called later with the same arguments, the cached value is returned
  (not reevaluated).
  """

  def __init__(self, func):
    self.func = func
    self.cache = {}

  def __call__(self, *args):
    try:
      return self.cache[args]
    except KeyError:
      value = self.func(*args)
      self.cache[args] = value
      return value
    except TypeError:
      # uncachable -- for instance, passing a list as an argument.
      # Better to not cache than to blow up entirely.
      return self.func(*args)

  def __repr__(self):
    """Return the function's docstring."""
    return self.func.__doc__

  def __get__(self, obj, objtype):
    """Support instance methods."""
    return functools.partial(self.__call__, obj)
