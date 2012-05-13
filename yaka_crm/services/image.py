from StringIO import StringIO
from PIL import Image

import hashlib

__all__ = ['resize']

cache = {}

def resize(orig, size):
  cache_key = (hashlib.md5(orig).digest(), size)
  if cache_key in cache:
    return cache[cache_key]

  image = Image.open(StringIO(orig))

  # Compute cropping coordinates
  x1 = y1 = 0
  x2, y2 = image.size
  w_ratio = 1.0 * x2 / size
  h_ratio = 1.0 * y2 / size
  if h_ratio > w_ratio:
    y1 = int(y2 / 2 - size * w_ratio / 2)
    y2 = int(y2 / 2 + size * w_ratio / 2)
  else:
    x1 = int(x2 / 2 - size * h_ratio / 2)
    x2 = int(x2 / 2 + size * h_ratio / 2)
  image = image.crop((x1, y1, x2, y2))

  image.thumbnail((size, size), Image.ANTIALIAS)

  output = StringIO()
  image.save(output, "JPEG")
  data = output.getvalue()
  cache[cache_key] = data
  return data